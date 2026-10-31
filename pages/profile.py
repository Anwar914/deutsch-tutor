"""Recovery, data portability and deletion without exposing other profiles."""

import streamlit as st

from core.storage import new_code, user_id
from core.ui import get_store, init_state, instruction, label, persist

store = get_store()
init_state(store)
st.title(label("Profil & Sicherung", "الملف والنسخ الاحتياطي"))
instruction(
    "Dein privater Lerncode ersetzt hier ein Passwort. Wer ihn kennt, kann auf dein Profil zugreifen.",
    "رمز التعلم الخاص يحل محل كلمة المرور هنا. من يعرفه يستطيع فتح ملفك.",
)
st.code(st.session_state.code, language=None)

with st.form("restore"):
    code = st.text_input(
        label("Vorhandener Lerncode", "رمز تعلم سابق"), type="password", max_chars=48
    )
    restore = st.form_submit_button(label("Profil wiederherstellen", "استعادة الملف"))
if restore:
    try:
        uid = user_id(code.strip())
        if not store.exists(uid):
            raise ValueError(
                "Dieses Profil wurde nicht gefunden. Prüfe den Code oder importiere eine Sicherung."
            )
        if st.session_state.active:
            persist(store)
        active = store.load_active(uid)
        st.session_state.clear()
        st.session_state.code = code.strip()
        st.session_state.uid = uid
        st.session_state.active = active
        st.session_state.level = (
            active["lesson"]["level"] if active else store.plan(uid).get("level", "A1")
        )
        st.rerun()
    except ValueError as error:
        st.error(str(error))

st.subheader(label("Datensicherung", "النسخ الاحتياطي"))
instruction(
    "Eine Sicherung enthält abgeschlossene Lektionen und Lernkarten, aber keine Audioaufnahmen oder laufenden Entwürfe. Sichere regelmäßig: Cloud-Neustarts können lokalen Speicher löschen.",
    "تحتوي النسخة على الدروس المكتملة والبطاقات، دون التسجيلات أو المسودات الحالية. احفظ نسخة بانتظام فقد يُحذف التخزين المحلي عند إعادة تشغيل الاستضافة.",
)
st.download_button(
    label("Fortschritt als JSON sichern", "تنزيل نسخة JSON"),
    data=store.export(st.session_state.uid),
    file_name="deutsch-tutor-fortschritt.json",
    mime="application/json",
)
upload = st.file_uploader(label("Sicherung importieren", "استيراد نسخة"), type=["json"])
if st.button(label("Sicherung zusammenführen", "دمج النسخة"), disabled=upload is None):
    try:
        store.import_backup(st.session_state.uid, upload.getvalue())
        st.success(
            label(
                "Sicherung importiert. Vorhandene Einträge bleiben erhalten.",
                "تم الاستيراد مع الحفاظ على البيانات الموجودة.",
            )
        )
    except (ValueError, TypeError, KeyError):
        st.error(
            label(
                "Diese Datei ist keine gültige Tutor-Sicherung.",
                "هذا الملف ليس نسخة احتياطية صالحة.",
            )
        )

with st.expander(label("Neues Profil / Daten löschen", "ملف جديد / حذف البيانات")):
    if st.button(label("Neues leeres Profil starten", "بدء ملف جديد")):
        persist(store)
        st.session_state.clear()
        st.session_state.code = new_code()
        st.rerun()
    confirmed = st.checkbox(
        label(
            "Ich möchte alle Daten dieses Profils unwiderruflich löschen.",
            "أريد حذف جميع بيانات هذا الملف نهائيًا.",
        )
    )
    if st.button(label("Dieses Profil löschen", "حذف هذا الملف"), disabled=not confirmed):
        store.delete_profile(st.session_state.uid)
        st.session_state.clear()
        st.rerun()
