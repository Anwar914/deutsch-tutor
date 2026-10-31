"""Exercise real scheduling boundaries, isolation, portability and content constraints."""

import json
from datetime import date, timedelta

import pytest

from core.feedback import validate_sentences
from core.lesson_engine import load_lessons
from core.spaced_repetition import build_cards, due_cards, matches, review
from core.storage import Store, new_code, user_id
from core.timer import elapsed, pause, resume


@pytest.fixture
def store(tmp_path):
    """Use a fresh SQLite database per test."""
    return Store(tmp_path / "tutor.sqlite3")


def profile(store):
    """Register a distinct profile for an integration scenario."""
    uid = user_id(new_code())
    store.ensure_profile(uid)
    return uid


@pytest.mark.parametrize("level", ["A1", "A2", "B1"])
def test_catalogue_and_cards(level):
    lessons = load_lessons(level)
    assert len(lessons) >= 10
    for lesson in lessons:
        assert (
            (8 <= len(lesson.dialogue) <= 12) if level == "B1" else (5 <= len(lesson.dialogue) <= 8)
        )
        cards = build_cards(lesson)
        assert len(cards) == 8
        assert len({card["id"] for card in cards}) == 8
        if level == "B1":
            assert all(card["kind"] != "translate" for card in cards)
        for card in cards:
            assert matches(card["answers"][0], card["answers"])


def test_schedule_day_one_seven_and_failure(store):
    uid = profile(store)
    lesson = load_lessons("A2")[0]
    day = date(2026, 10, 20)
    store.complete(uid, lesson, 1200, day)
    assert due_cards(store, uid, "A2", day) == []
    cards = due_cards(store, uid, "A2", day + timedelta(days=1))
    assert len(cards) == 8  # unused week quota is honestly backfilled
    cid = cards[0]["card_id"]
    assert review(store, uid, cid, True, day + timedelta(days=1))
    assert not review(store, uid, cid, True, day + timedelta(days=1))
    with store.connect() as db:
        card = db.execute("SELECT * FROM cards WHERE card_id=?", (cid,)).fetchone()
        assert card["due"] == "2026-10-27"
        assert card["stage"] == 1
    assert review(store, uid, cid, False, day + timedelta(days=7))
    with store.connect() as db:
        card = db.execute("SELECT * FROM cards WHERE card_id=?", (cid,)).fetchone()
        assert card["due"] == "2026-10-28"
        assert card["stage"] == 0


def test_five_recent_three_week_old_and_overdue(store):
    uid = profile(store)
    lessons = load_lessons("A1")
    day = date(2026, 10, 31)
    store.complete(uid, lessons[0], 100, day - timedelta(days=7))
    store.complete(uid, lessons[1], 100, day - timedelta(days=1))
    cards = due_cards(store, uid, "A1", day)
    assert sum(c["bucket"].startswith("24") for c in cards) == 5
    assert sum(c["bucket"].startswith("Woche") for c in cards) == 3
    assert due_cards(store, uid, "A1", day + timedelta(days=10))


def test_isolation_completion_idempotency_and_streak(store):
    alice, bob = profile(store), profile(store)
    day = date(2026, 10, 31)
    lesson = load_lessons("A1")[0]
    assert store.complete(alice, lesson, 100, day)
    assert not store.complete(alice, lesson, 100, day)
    assert store.stats(alice, day)["introduced"] == 8
    assert store.stats(bob, day)["introduced"] == 0
    assert due_cards(store, bob, "A1", day + timedelta(days=1)) == []
    assert not review(store, bob, build_cards(lesson)[0]["id"], True, day + timedelta(days=1))
    assert store.stats(alice, day + timedelta(days=1))["streak"] == 1
    assert store.stats(alice, day + timedelta(days=2))["streak"] == 0
    store.delete_profile(bob)
    assert store.exists(alice)


def test_portability_and_atomic_rejection(store):
    alice, bob = profile(store), profile(store)
    store.save_active(alice, {"next_goal": "Fünf Wörter üben", "reflection": "Ich spreche mehr."})
    store.complete(alice, load_lessons("B1")[0], 100, date(2026, 10, 31))
    backup = store.export(alice)
    assert alice.encode() not in backup
    store.import_backup(bob, backup)
    assert store.stats(bob)["introduced"] == 8
    assert store.plan(bob)["goal"] == "Fünf Wörter üben"
    store.import_backup(bob, backup)
    assert store.stats(bob)["introduced"] == 8
    raw = json.loads(backup)
    raw["cards"][0]["due"] = "not-a-date"
    before = store.export(bob)
    with pytest.raises(ValueError):
        store.import_backup(bob, json.dumps(raw).encode())
    assert store.export(bob) == before


def test_timer_resume_pause_no_double_count():
    timer = {"elapsed": 5, "started": None}
    resume(timer, 100)
    resume(timer, 105)
    assert elapsed(timer, 110) == 15
    pause(timer, 110)
    assert elapsed(timer, 500) == 15
    resume(timer, 600)
    assert elapsed(timer, 610) == 25


def test_answer_normalization_and_input_validation():
    assert matches("  ICH   WOHNE in Berlin! ", ["Ich wohne in Berlin."])
    assert not matches("schon", ["schön"])
    with pytest.raises(ValueError):
        validate_sentences([""] * 5)
    with pytest.raises(ValueError):
        user_id("alice")
    with pytest.raises(ValueError):
        load_lessons("../../secret")
