"""Transactional SQLite persistence, isolated by hashed bearer profile codes."""

import hashlib
import json
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from core.models import Lesson


def today() -> date:
    """Use German calendar days consistently, including DST changes."""
    return datetime.now(ZoneInfo("Europe/Berlin")).date()


def new_code() -> str:
    """Return an unguessable recovery credential, never a display name."""
    return secrets.token_hex(24)


def user_id(code: str) -> str:
    """Validate and hash the recovery credential before any database operation."""
    if not re.fullmatch(r"[0-9a-f]{48}", code):
        raise ValueError("Ungültiger Lerncode: erwartet werden 48 kleine Hex-Zeichen.")
    return hashlib.sha256(code.encode()).hexdigest()


class Store:
    """Open short-lived connections, never share a cursor across Streamlit sessions."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id TEXT PRIMARY KEY, active TEXT
                );
                CREATE TABLE IF NOT EXISTS completions (
                    user_id TEXT NOT NULL, lesson_id TEXT NOT NULL, day TEXT NOT NULL,
                    level TEXT NOT NULL, title TEXT NOT NULL, seconds INTEGER NOT NULL,
                    PRIMARY KEY(user_id, lesson_id, day)
                );
                CREATE TABLE IF NOT EXISTS cards (
                    user_id TEXT NOT NULL, card_id TEXT NOT NULL, level TEXT NOT NULL,
                    payload TEXT NOT NULL, introduced TEXT NOT NULL, due TEXT NOT NULL,
                    stage INTEGER NOT NULL DEFAULT 0, correct INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY(user_id, card_id)
                );
                CREATE TABLE IF NOT EXISTS reviews (
                    user_id TEXT NOT NULL, card_id TEXT NOT NULL, day TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    PRIMARY KEY(user_id, card_id, day)
                );
                CREATE INDEX IF NOT EXISTS due_cards ON cards(user_id, level, due);
                CREATE TABLE IF NOT EXISTS plans (
                    user_id TEXT PRIMARY KEY, goal TEXT NOT NULL, reflection TEXT NOT NULL,
                    level TEXT NOT NULL
                );
            """)

    @contextmanager
    def connect(self):
        """Commit on success, rollback on error, always release the file handle."""
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def ensure_profile(self, uid: str) -> None:
        """Create the current profile idempotently."""
        with self.connect() as db:
            db.execute("INSERT OR IGNORE INTO profiles(user_id) VALUES (?)", (uid,))

    def exists(self, uid: str) -> bool:
        """Check a supplied recovery code without enumerating other profiles."""
        with self.connect() as db:
            return (
                db.execute("SELECT 1 FROM profiles WHERE user_id=?", (uid,)).fetchone() is not None
            )

    def load_active(self, uid: str) -> dict[str, Any] | None:
        """Recover a saved lesson, draft and phase."""
        with self.connect() as db:
            row = db.execute("SELECT active FROM profiles WHERE user_id=?", (uid,)).fetchone()
        return json.loads(row["active"]) if row and row["active"] else None

    def save_active(self, uid: str, active: dict[str, Any] | None) -> None:
        """Persist only explicit snapshots, never raw recordings."""
        with self.connect() as db:
            db.execute(
                "UPDATE profiles SET active=? WHERE user_id=?",
                (
                    json.dumps(active, ensure_ascii=False) if active else None,
                    uid,
                ),
            )

    def completed_ids(self, uid: str, level: str) -> set[str]:
        """Find studied lessons to choose the next unseen local lesson."""
        with self.connect() as db:
            rows = db.execute(
                "SELECT DISTINCT lesson_id FROM completions WHERE user_id=? AND level=?",
                (uid, level),
            ).fetchall()
        return {row[0] for row in rows}

    def complete(self, uid: str, lesson: Lesson, seconds: int, day: date | None = None) -> bool:
        """Atomically record completion, enroll vocabulary and clear the draft."""
        from core.spaced_repetition import build_cards

        day = day or today()
        with self.connect() as db:
            result = db.execute(
                "INSERT OR IGNORE INTO completions VALUES (?,?,?,?,?,?)",
                (uid, lesson.id, day.isoformat(), lesson.level, lesson.title, max(0, seconds)),
            )
            for card in build_cards(lesson):
                db.execute(
                    "INSERT OR IGNORE INTO cards VALUES (?,?,?,?,?,?,0,0)",
                    (
                        uid,
                        card["id"],
                        lesson.level,
                        json.dumps(card, ensure_ascii=False),
                        day.isoformat(),
                        (day + timedelta(days=1)).isoformat(),
                    ),
                )
            saved = db.execute("SELECT active FROM profiles WHERE user_id=?", (uid,)).fetchone()
            active = json.loads(saved["active"]) if saved and saved["active"] else {}
            db.execute(
                "INSERT OR REPLACE INTO plans VALUES (?,?,?,?)",
                (
                    uid,
                    str(active.get("next_goal", ""))[:400],
                    str(active.get("reflection", ""))[:1000],
                    lesson.level,
                ),
            )
            db.execute("UPDATE profiles SET active=NULL WHERE user_id=?", (uid,))
        return result.rowcount == 1

    def stats(self, uid: str, day: date | None = None) -> dict[str, Any]:
        """Report activity without equating card counts with CEFR proficiency."""
        day = day or today()
        with self.connect() as db:
            history = [
                dict(row)
                for row in db.execute(
                    "SELECT day, COUNT(*) AS lessons, SUM(seconds) AS seconds FROM completions "
                    "WHERE user_id=? GROUP BY day ORDER BY day",
                    (uid,),
                )
            ]
            total = db.execute(
                "SELECT COUNT(DISTINCT lesson_id) FROM completions WHERE user_id=?",
                (uid,),
            ).fetchone()[0]
            cards = db.execute(
                "SELECT COUNT(*), COALESCE(SUM(stage>=3),0) FROM cards WHERE user_id=?",
                (uid,),
            ).fetchone()
            dates = {
                row[0]
                for row in db.execute(
                    "SELECT day FROM completions WHERE user_id=? UNION "
                    "SELECT day FROM reviews WHERE user_id=?",
                    (uid, uid),
                )
            }
        cursor = day if day.isoformat() in dates else day - timedelta(days=1)
        streak = 0
        while cursor.isoformat() in dates:
            streak += 1
            cursor -= timedelta(days=1)
        return {
            "lessons": total,
            "introduced": cards[0],
            "learned": cards[1],
            "streak": streak,
            "history": history,
        }

    def export(self, uid: str) -> bytes:
        """Export this profile's learning data, excluding its recovery credential."""
        result: dict[str, Any] = {"version": 1}
        result["plan"] = self.plan(uid)
        with self.connect() as db:
            for table in ("completions", "cards", "reviews"):
                result[table] = [
                    {k: row[k] for k in row.keys() if k != "user_id"}
                    for row in db.execute(f"SELECT * FROM {table} WHERE user_id=?", (uid,))
                ]
        return json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")

    def import_backup(self, uid: str, data: bytes) -> None:
        """Validate an export fully before atomically merging into the current profile."""
        from core.spaced_repetition import Card

        if len(data) > 5_000_000:
            raise ValueError("Die Sicherung darf höchstens 5 MB groß sein.")
        raw = json.loads(data)
        if not isinstance(raw, dict) or raw.get("version") != 1:
            raise ValueError("Unbekanntes Sicherungsformat.")
        plan = raw.get("plan", {})
        if (
            not isinstance(plan, dict)
            or any(not isinstance(v, str) or len(v) > 1000 for v in plan.values())
            or (
                plan
                and (
                    set(plan) != {"goal", "reflection", "level"}
                    or plan["level"] not in ("A1", "A2", "B1")
                )
            )
        ):
            raise ValueError("Ungültiger Lernplan.")
        expected = {
            "completions": {"lesson_id", "day", "level", "title", "seconds"},
            "cards": {"card_id", "level", "payload", "introduced", "due", "stage", "correct"},
            "reviews": {"card_id", "day", "success"},
        }
        for table, fields in expected.items():
            rows = raw.get(table)
            if not isinstance(rows, list) or len(rows) > 20000:
                raise ValueError("Ungültige Sicherung.")
            for row in rows:
                if not isinstance(row, dict) or set(row) != fields:
                    raise ValueError("Ungültige Felder.")
                for key, value in row.items():
                    if key in {"seconds", "stage", "correct", "success"}:
                        if type(value) is not int or not 0 <= value <= 10_000_000:
                            raise ValueError("Ungültige Zahl.")
                    elif not isinstance(value, str) or len(value) > 10000:
                        raise ValueError("Ungültiger Text.")
                for field in ("day", "introduced", "due"):
                    if field in row:
                        date.fromisoformat(row[field])
                if "level" in row and row["level"] not in ("A1", "A2", "B1"):
                    raise ValueError("Ungültiges Niveau.")
                if table == "cards":
                    card = Card.model_validate_json(row["payload"])
                    if card.id != row["card_id"] or row["stage"] > 4:
                        raise ValueError("Ungültige Karte.")
                if table == "reviews" and row["success"] not in (0, 1):
                    raise ValueError("Ungültiges Ergebnis.")
        with self.connect() as db:
            if plan:
                db.execute(
                    "INSERT OR IGNORE INTO plans VALUES (?,?,?,?)",
                    (uid, plan["goal"], plan["reflection"], plan["level"]),
                )
            for table, fields in expected.items():
                columns = sorted(fields)
                for row in raw[table]:
                    db.execute(
                        f"INSERT OR IGNORE INTO {table} (user_id,{','.join(columns)}) "
                        f"VALUES ({','.join('?' for _ in range(len(columns) + 1))})",
                        (uid, *(row[column] for column in columns)),
                    )

    def delete_profile(self, uid: str) -> None:
        """Delete only this authenticated-by-code profile and all its learning data."""
        with self.connect() as db:
            for table in ("reviews", "cards", "completions", "plans", "profiles"):
                db.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))

    def plan(self, uid: str) -> dict[str, str]:
        """Read the saved next-day goal without discarding it on lesson completion."""
        with self.connect() as db:
            row = db.execute(
                "SELECT goal,reflection,level FROM plans WHERE user_id=?", (uid,)
            ).fetchone()
        return dict(row) if row else {}
