"""Streamlit integration tests exercise the actual four-phase page."""

import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Never use real credentials, recordings or learner databases in UI tests."""
    monkeypatch.setenv("TUTOR_DB_PATH", str(tmp_path / "app.sqlite3"))
    monkeypatch.setenv("OPENAI_API_KEY", "")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
    assert not app.exception
    return app


def click(app, prefix):
    """Click a visible button by its German label prefix."""
    matches = [button for button in app.button if button.label.startswith(prefix)]
    assert len(matches) == 1, [b.label for b in app.button]
    matches[0].click().run()
    assert not app.exception


@pytest.mark.parametrize("level", ["A1", "A2", "B1"])
def test_level_starts_input_immediately(app, level):
    app.button(key=f"start_{level}").click().run()
    assert not app.exception
    assert app.session_state["active"]["lesson"]["level"] == level
    assert app.session_state["active"]["phase"] == 0
    if level == "B1":
        strings = [x.value for x in app.markdown] + [x.label for x in app.button]
        assert not any(re.search(r"[\u0600-\u06ff]", text) for text in strings)


def test_complete_offline_lesson(app):
    app.button(key="start_A2").click().run()
    for _ in range(3):
        click(app, "Durchgang abgeschlossen")
    click(app, "Weiter zum Sprechen")
    app.checkbox[0].check()
    for index, widget in enumerate(app.text_input):
        widget.input(f"Ich lerne heute Wort {index + 1}.")
    click(app, "Entwurf speichern")
    click(app, "Weiter zur Wiederholung")
    assert app.session_state["active"]["warmup"]
    for row in list(app.session_state["active"]["reviews"]):
        cid = row["card"]["id"]
        lesson_id = app.session_state["active"]["lesson"]["id"]
        app.text_input(key=f"answer_{lesson_id}_{cid}").input(row["card"]["answers"][0])
        app.button(key="check_" + cid).click().run()
        app.button(key="save_" + cid).click().run()
        assert not app.exception
    click(app, "Weiter zu Feedback")
    assert any("nicht automatisch korrigiert" in info.value for info in app.info)
    click(app, "Lektion abschließen")
    assert app.session_state["active"] is None
    assert any("gespeichert" in success.value for success in app.success)


def test_progress_page_and_profile_restore(app):
    app.button(key="start_B1").click().run()
    click(app, "Durchgang abgeschlossen")
    code = app.session_state["code"]
    app.switch_page("pages/progress.py").run()
    assert not app.exception
    app.switch_page("pages/profile.py").run()
    assert not app.exception
    click(app, "Neues leeres Profil")
    assert app.session_state["code"] != code
    app.text_input[0].input(code)
    click(app, "Profil wiederherstellen")
    assert app.session_state["code"] == code
    assert app.session_state["active"]["passes"] == 1
    assert app.session_state["active"]["timers"][0]["started"] is None
