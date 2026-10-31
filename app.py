"""Deutsch-Tutor entry point: navigation, scoped profile and native theme support."""

import sqlite3

import streamlit as st

from core.ui import arabic, get_store, init_state, label, level

st.set_page_config(
    page_title="Deutsch-Tutor · A1 / A2 / B1", page_icon=":material/school:", layout="centered"
)
st.html(
    "<style>.arabic { direction: rtl; text-align: right; line-height: 1.9; unicode-bidi: isolate; }</style>"
)

try:
    store = get_store()
    init_state(store)
except (OSError, sqlite3.Error):
    st.error("Der Lernspeicher ist gerade nicht erreichbar. Bitte versuche es später erneut.")
    st.stop()

with st.sidebar:
    st.markdown("### Deutsch-Tutor")
    st.caption(
        label(
            "Dein Alltag. Deine Sprache. Ein Schritt pro Tag.", "حياتك اليومية، لغتك، خطوة كل يوم."
        )
    )
    if st.session_state.active:
        st.badge(level())
    st.caption(
        label(
            "Hell/Dunkel: Menü oben rechts → Einstellungen.",
            "اختر الوضع الفاتح أو الداكن من الإعدادات أعلى الصفحة.",
        )
    )
    with st.expander(label("Lerncode sichern", "احفظ رمز التعلم")):
        st.code(st.session_state.code, language=None)
        st.caption(
            label(
                "Dieser private Code öffnet deinen Fortschritt. Sicher aufbewahren und nicht teilen.",
                "هذا الرمز الخاص يتيح الوصول إلى تقدمك. احفظه ولا تشاركه.",
            )
        )

page = st.navigation(
    [
        st.Page(
            "pages/lesson.py",
            title=label("Lernen", "التعلم"),
            icon=":material/menu_book:",
            default=True,
        ),
        st.Page(
            "pages/progress.py", title=label("Fortschritt", "التقدم"), icon=":material/monitoring:"
        ),
        st.Page(
            "pages/profile.py",
            title=label("Profil & Sicherung", "الملف والنسخ الاحتياطي"),
            icon=":material/person:",
        ),
    ]
)
try:
    page.run()
except (OSError, sqlite3.Error):
    st.error(
        label(
            "Speichern fehlgeschlagen. Bitte lasse diese Seite offen und versuche es erneut.",
            "تعذر الحفظ. أبقِ الصفحة مفتوحة وحاول مرة أخرى.",
        )
    )
    if level() == "A1":
        arabic("لا تغلق الصفحة قبل حفظ عملك.")
