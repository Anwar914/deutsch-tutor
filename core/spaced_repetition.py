"""A transparent Leitner-light schedule with overdue handling and daily idempotency."""

import hashlib
import random
import re
import unicodedata
from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field

from core.models import Lesson
from core.storage import Store, today


class Card(BaseModel):
    """Safe persisted recall task; answers are hidden until submission."""

    id: str = Field(min_length=1, max_length=120)
    term: str = Field(min_length=1, max_length=100)
    kind: Literal["cloze", "order", "translate"]
    prompt: str = Field(min_length=1, max_length=1000)
    answers: list[str] = Field(min_length=1, max_length=10)


def normalize(text: str) -> str:
    """Ignore case, whitespace and punctuation, but preserve meaningful umlauts."""
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.sub(r"[^\w\s]", "", text).split())


def matches(answer: str, expected: list[str]) -> bool:
    """Use deterministic checks; explicitly allow self-review for valid alternatives."""
    return bool(answer.strip()) and normalize(answer) in {normalize(a) for a in expected}


def build_cards(lesson: Lesson) -> list[dict]:
    """Create eight stable tasks; B1 never receives an Arabic translation prompt."""
    cards = []
    for index, vocab in enumerate(lesson.vocabulary):
        digest = hashlib.sha256(
            f"{lesson.level}:{vocab.term}:{vocab.example}".encode()
        ).hexdigest()[:24]
        kind = ["cloze", "order", "translate"][index % 3]
        if kind == "translate" and lesson.level == "B1":
            kind = "cloze"
        if kind == "cloze":
            prompt = vocab.example.replace(vocab.answer, "_____", 1)
            answer = vocab.answer
        elif kind == "order":
            words = vocab.example.rstrip(".!?").split()
            original = words.copy()
            random.Random(digest).shuffle(words)
            if words == original and len(words) > 1:
                words = words[1:] + words[:1]
            prompt, answer = " / ".join(words), vocab.example
        else:
            prompt, answer = vocab.translation_ar, vocab.translation_de
        cards.append(
            Card(
                id=digest, term=vocab.term, kind=kind, prompt=prompt, answers=[answer]
            ).model_dump()
        )
    return cards


def due_cards(store: Store, uid: str, level: str, day: date | None = None) -> list[dict]:
    """Prefer 5 recent and 3 week-old cards, then fill available slots from overdue cards."""
    day = day or today()
    with store.connect() as db:
        rows = [
            dict(row)
            for row in db.execute(
                "SELECT * FROM cards WHERE user_id=? AND level=? AND due<=? "
                "AND card_id NOT IN (SELECT card_id FROM reviews WHERE user_id=? AND day=?) "
                "ORDER BY due,introduced,card_id",
                (uid, level, day.isoformat(), uid, day.isoformat()),
            )
        ]
    recent, week = [], []
    for row in rows:
        age = (day - date.fromisoformat(row["introduced"])).days
        row["bucket"] = "Woche / überfällig" if age >= 7 else "24 Stunden / überfällig"
        (week if age >= 7 else recent).append(row)
    recent.sort(
        key=lambda row: (row["introduced"] != (day - timedelta(days=1)).isoformat(), row["due"])
    )
    week.sort(
        key=lambda row: (row["introduced"] != (day - timedelta(days=7)).isoformat(), row["due"])
    )
    selected = recent[:5] + week[:3]
    selected_ids = {row["card_id"] for row in selected}
    selected += [row for row in rows if row["card_id"] not in selected_ids][: 8 - len(selected)]
    for row in selected:
        row["card"] = Card.model_validate_json(row["payload"]).model_dump()
    return selected


def review(store: Store, uid: str, card_id: str, success: bool, day: date | None = None) -> bool:
    """Schedule once per calendar day, transactionally; first success targets day seven."""
    day = day or today()
    with store.connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT * FROM cards WHERE user_id=? AND card_id=?",
            (uid, card_id),
        ).fetchone()
        if row is None or row["due"] > day.isoformat():
            return False
        inserted = db.execute(
            "INSERT OR IGNORE INTO reviews VALUES (?,?,?,?)",
            (uid, card_id, day.isoformat(), int(success)),
        )
        if inserted.rowcount == 0:
            return False
        stage = min(row["stage"] + 1, 4) if success else 0
        interval = {0: 1, 1: 6, 2: 14, 3: 30, 4: 60}[stage]
        db.execute(
            "UPDATE cards SET stage=?, correct=correct+?, due=? WHERE user_id=? AND card_id=?",
            (stage, int(success), (day + timedelta(days=interval)).isoformat(), uid, card_id),
        )
    return True
