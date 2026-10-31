"""Contract tests mock the provider, never perform paid API calls."""

import sys
from types import SimpleNamespace

import pytest

from core.feedback import correct_writing
from core.lesson_engine import generate_lesson, load_lessons
from core.models import Correction, Feedback


def fake_client(monkeypatch, result):
    """Capture request payloads and emulate the public SDK context manager."""
    requests = []

    class Client:
        def __init__(self, **kwargs):
            self.responses = self

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def parse(self, **kwargs):
            requests.append(kwargs)
            return SimpleNamespace(output_parsed=result)

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=Client))
    return requests


def test_feedback_contract_and_privacy(monkeypatch):
    sentences = [f"Ich übe Satz {i}." for i in range(5)]
    feedback = Feedback(
        encouragement="Gut!",
        corrections=[
            Correction(original=s, corrected=s, explanation_de="Richtig.", explanation_ar="")
            for s in sentences
        ],
        next_goal="Übe fünf Wörter.",
    )
    requests = fake_client(monkeypatch, feedback)
    assert correct_writing(sentences, "B1", "test", "test-model") == feedback
    assert requests[0]["store"] is False
    assert "German only" in requests[0]["input"][0]["content"]
    assert "test" not in requests[0]["input"][1]["content"]


def test_refusal_and_wrong_level(monkeypatch):
    fake_client(monkeypatch, None)
    with pytest.raises(ValueError):
        generate_lesson("A1", "Einkaufen", "test", "test-model")
    fake_client(monkeypatch, load_lessons("B1")[0])
    with pytest.raises(ValueError):
        generate_lesson("A1", "Einkaufen", "test", "test-model")
