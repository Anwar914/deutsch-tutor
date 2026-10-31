"""Shared UI helpers, localization and explicitly persisted lesson snapshots."""

import copy
import html
import os
import re
from pathlib import Path

import streamlit as st

from core.lesson_engine import load_lessons
from core.models import Lesson, Level
from core.storage import Store, new_code, user_id
from core.timer import DURATIONS, elapsed, pause, resume
from core.tts import synthesize

ROOT = Path(__file__).resolve().parent.parent
PHASES = ("Verstehen", "Sprechen & Schreiben", "Wiederholen", "Feedback & Planung")
PHASES_AR = ("الفهم", "التحدث والكتابة", "المراجعة", "التقييم والتخطيط")


def setting(name: str, default: str = "") -> str:
    """Read environment variables first, then optional Streamlit secrets."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        return str(st.secrets.get(name, default))
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return default


def get_store() -> Store:
    """Resolve the database path without exposing configuration to the learner."""
    return Store(setting("TUTOR_DB_PATH", str(ROOT / "storage" / "tutor.sqlite3")))


def level() -> Level:
    """Use the active level or the last selected one."""
    active = st.session_state.get("active")
    return active["lesson"]["level"] if active else st.session_state.get("level", "A1")


def label(de: str, ar: str = "") -> str:
    """A1 receives bilingual controls; A2/B1 use German controls."""
    return f"{de} · {ar}" if level() == "A1" and ar else de


def arabic(text: str) -> None:
    """Render escaped Arabic with explicit RTL; no untrusted HTML is accepted."""
    st.html(f'<p class="arabic" lang="ar" dir="rtl">{html.escape(text)}</p>')


def instruction(de: str, ar: str) -> None:
    """Add short Arabic scaffolding automatically at A1 only."""
    st.write(de)
    if level() == "A1":
        arabic(ar)


@st.cache_data(ttl=3600, max_entries=3)
def catalogue(selected_level: Level) -> list[dict]:
    """Cache public lesson content only, never learner drafts."""
    return [lesson.model_dump() for lesson in load_lessons(selected_level)]


@st.cache_data(ttl=86400, max_entries=40, show_spinner=False)
def lesson_audio(text: str) -> bytes:
    """Cache synthesized public lesson text, bounded in time and size."""
    return synthesize(text)


def init_state(store: Store) -> None:
    """Initialize all per-session identity and lesson state in one place."""
    if "code" not in st.session_state:
        st.session_state.code = new_code()
    st.session_state.uid = user_id(st.session_state.code)
    store.ensure_profile(st.session_state.uid)
    st.session_state.setdefault("level", "A1")
    st.session_state.setdefault("active", None)


def persist(store: Store) -> None:
    """Save a paused snapshot so disconnected time is never counted as learning."""
    active = copy.deepcopy(st.session_state.active)
    if active:
        for timer in active["timers"]:
            pause(timer)
    store.save_active(st.session_state.uid, active)


def start_lesson(lesson: Lesson, store: Store) -> None:
    """Start immediately at input; persist the exact generated/local content."""
    st.session_state.level = lesson.level
    st.session_state.active = {
        "lesson": lesson.model_dump(),
        "phase": 0,
        "passes": 0,
        "timers": [{"elapsed": 0.0, "started": None} for _ in DURATIONS],
        "sentences": [""] * 5,
        "spoken": False,
        "rating": 3,
        "feedback": None,
        "reviews": None,
        "review_done": [],
        "next_goal": "",
        "reflection": "",
    }
    resume(st.session_state.active["timers"][0])
    persist(store)


def advance(store: Store) -> None:
    """Move forward while preserving elapsed time and all work."""
    active = st.session_state.active
    pause(active["timers"][active["phase"]])
    active["phase"] += 1
    resume(active["timers"][active["phase"]])
    persist(store)
    st.rerun()


@st.fragment(run_every=5)
def phase_timer() -> None:
    """Refresh only the timer, preserving recording and writing widgets."""
    active = st.session_state.active
    if not active:
        return
    phase = active["phase"]
    timer = active["timers"][phase]
    spent = elapsed(timer)
    remaining = max(0, int(DURATIONS[phase] - spent))
    st.progress(
        min(1.0, spent / DURATIONS[phase]),
        text=label(
            f"{remaining // 60:02d}:{remaining % 60:02d} verbleibend · {DURATIONS[phase] // 60} Minuten",
            "الوقت المتبقي في هذه المرحلة",
        ),
    )
    if st.button(
        label("Pause" if timer["started"] else "Timer fortsetzen", "إيقاف مؤقت / متابعة"),
        key="pause_timer",
    ):
        pause(timer) if timer["started"] else resume(timer)
        persist(get_store())
        st.rerun(scope="fragment")
    if remaining == 0:
        st.caption(
            label(
                "Die Zeit ist um. Du kannst in Ruhe fertigarbeiten.",
                "انتهى الوقت، يمكنك إكمال المهمة بهدوء.",
            )
        )
    # A saved snapshot never runs while the browser is disconnected.
    persist(get_store())


def highlighted(text: str, lesson: Lesson) -> None:
    """Safely emphasize literal vocabulary occurrences without executing markup."""
    terms = {v.answer for v in lesson.vocabulary} | {
        re.sub(r"^(der|die|das) ", "", v.term) for v in lesson.vocabulary
    }
    pattern = re.compile(
        r"(?<!\w)("
        + "|".join(re.escape(t) for t in sorted(terms, key=len, reverse=True))
        + r")(?!\w)",
        re.I,
    )
    parts, pos = [], 0
    for match in pattern.finditer(text):
        parts.extend(
            [
                html.escape(text[pos : match.start()]),
                "<strong>" + html.escape(match.group()) + "</strong>",
            ]
        )
        pos = match.end()
    parts.append(html.escape(text[pos:]))
    st.html('<p lang="de" dir="ltr">' + "".join(parts) + "</p>")


def show_stats(store: Store) -> None:
    """Display transparent progress indicators for the current profile."""
    stats = store.stats(st.session_state.uid)
    with st.container(horizontal=True):
        st.metric(label("Lernserie", "أيام متتالية"), f"{stats['streak']} Tage")
        st.metric(label("Lektionen", "الدروس"), stats["lessons"])
        st.metric(label("Gefestigte Karten", "بطاقات راسخة"), stats["learned"])
    st.caption(
        label(
            "Gefestigt = mindestens drei erfolgreiche Wiederholungen in Folge; keine CEFR-Einstufung.",
            "راسخة = ثلاث مراجعات صحيحة متتالية على الأقل؛ هذا ليس تحديدًا لمستوى اللغة.",
        )
    )
    if stats["history"]:
        st.bar_chart(
            [{"Tag": row["day"], "Lektionen": row["lessons"]} for row in stats["history"]],
            x="Tag",
            y="Lektionen",
        )


def require_active() -> tuple[Store, Lesson]:
    """Stop a page gracefully if the learner has not selected a level yet."""
    store = get_store()
    if not st.session_state.get("active"):
        st.info(
            label("Wähle zuerst dein Niveau auf der Lernseite.", "اختر مستواك أولًا في صفحة التعلم.")
        )
        st.stop()
    return store, Lesson.model_validate(st.session_state.active["lesson"])
