"""Private learning overview and upcoming review schedule."""

import streamlit as st

from core.storage import today
from core.ui import get_store, init_state, label, show_stats

store = get_store()
init_state(store)
st.title(label("Dein Fortschritt", "تقدمك"))
show_stats(store)
plan = store.plan(st.session_state.uid)
if plan:
    st.subheader(label("Dein nächstes Ziel", "هدفك القادم"))
    st.write(plan["goal"])
    if plan["reflection"]:
        st.write(plan["reflection"])
with store.connect() as db:
    rows = [
        dict(row)
        for row in db.execute(
            "SELECT due AS Datum, level AS Niveau, COUNT(*) AS Karten FROM cards "
            "WHERE user_id=? GROUP BY due,level ORDER BY due",
            (st.session_state.uid,),
        )
    ]
st.subheader(label("Wiederholungsplan", "خطة المراجعة"))
if rows:
    st.dataframe(rows, hide_index=True)
    due = sum(row["Karten"] for row in rows if row["Datum"] <= today().isoformat())
    st.caption(
        label(
            f"{due} Karten sind heute oder früher fällig.",
            f"{due} بطاقة مستحقة اليوم أو من أيام سابقة.",
        )
    )
else:
    st.info(
        label(
            "Schließe deine erste Lektion ab. Danach startet dein Wiederholungsplan.",
            "أكمل أول درس لتبدأ خطة المراجعة.",
        )
    )
