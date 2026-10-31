"""Four-phase daily lesson, with explicit actions and no automatic API requests."""

import streamlit as st

from core.feedback import correct_writing, validate_sentences
from core.lesson_engine import generate_lesson
from core.models import Lesson
from core.spaced_repetition import build_cards, due_cards, matches, review
from core.storage import today
from core.timer import DURATIONS, elapsed
from core.ui import (
    PHASES,
    PHASES_AR,
    advance,
    arabic,
    catalogue,
    get_store,
    highlighted,
    instruction,
    label,
    lesson_audio,
    level,
    persist,
    phase_timer,
    setting,
    show_stats,
    start_lesson,
)

store = get_store()
uid = st.session_state.uid
st.title("Deutsch-Tutor")

if not st.session_state.active:
    if st.session_state.get("just_completed"):
        st.success(label("Lektion gespeichert. Gut gemacht!", "تم حفظ الدرس، أحسنت!"))
        st.write(st.session_state.just_completed)
    st.subheader(
        "Willkommen! Bitte wähle dein aktuelles Niveau aus, um deinen Tagesplan zu starten"
    )
    if level() == "A1":
        arabic("مرحبًا! اختر مستواك الحالي لبدء خطة اليوم.")
    with st.container(horizontal=True):
        for choice in ("A1", "A2", "B1"):
            if st.button(choice, type="primary", key=f"start_{choice}"):
                lessons = catalogue(choice)
                completed = store.completed_ids(uid, choice)
                selected = next(
                    (item for item in lessons if item["id"] not in completed), lessons[0]
                )
                start_lesson(Lesson.model_validate(selected), store)
                st.session_state.pop("just_completed", None)
                st.rerun()
    st.caption(
        "15 Minuten Verstehen · 15 Minuten Anwenden · 10 Minuten Wiederholen · 5 Minuten Feedback"
    )
    with st.expander(label("Andere Lektion oder eigenes Thema", "درس آخر أو موضوع خاص")):
        chosen_level = st.selectbox(label("Niveau", "المستوى"), ["A1", "A2", "B1"])
        lessons = catalogue(chosen_level)
        selected_index = st.selectbox(
            label("Thema", "الموضوع"),
            range(len(lessons)),
            format_func=lambda i: lessons[i]["title"],
        )
        if st.button(label("Diese Lektion starten", "ابدأ هذا الدرس")):
            start_lesson(Lesson.model_validate(lessons[selected_index]), store)
            st.rerun()
        topic = st.text_input(
            label("Eigenes Thema für eine KI-Lektion", "موضوع لدرس بالذكاء الاصطناعي"),
            max_chars=100,
        )
        st.caption(
            label(
                "Bei Erstellung wird nur dein Thema an OpenAI gesendet. Keine persönlichen Angaben eingeben.",
                "عند الإنشاء يُرسل الموضوع فقط إلى OpenAI. لا تكتب بيانات شخصية.",
            )
        )
        if st.button(
            label("KI-Lektion erstellen", "إنشاء درس"), disabled=not setting("OPENAI_API_KEY")
        ):
            try:
                with st.spinner(label("Lektion wird erstellt …", "جارٍ إنشاء الدرس…")):
                    generated = generate_lesson(
                        chosen_level,
                        topic,
                        setting("OPENAI_API_KEY"),
                        setting("OPENAI_MODEL", "gpt-4o-mini"),
                    )
                start_lesson(generated, store)
                st.rerun()
            except Exception:
                st.warning(
                    label(
                        "Die KI-Lektion konnte nicht erstellt werden. Die lokalen Lektionen bleiben verfügbar.",
                        "تعذر إنشاء الدرس. الدروس المحلية متاحة.",
                    )
                )
    st.stop()

active = st.session_state.active
lesson = Lesson.model_validate(active["lesson"])
phase = active["phase"]
st.caption(f"{lesson.level} · {lesson.title}")
st.subheader(f"{phase + 1}/4 · {label(PHASES[phase], PHASES_AR[phase])}")
st.progress(
    phase / 4, text=label(f"{phase} von 4 Phasen abgeschlossen", f"أكملت {phase} من 4 مراحل")
)
phase_timer()
st.caption(
    label(
        "45 Minuten sind dein Tagesziel. Du darfst früher wechseln oder länger üben; der Timer bewertet dich nicht.",
        "45 دقيقة هي هدفك اليومي. يمكنك الانتقال مبكرًا أو التدرب مدة أطول، والمؤقت لا يقيّمك.",
    )
)

if phase == 0:
    st.write(lesson.goal)
    instruction(
        "Höre/lies den Text 3-mal: erst den Sinn, dann die Satzstruktur, zuletzt laut mitsprechen.",
        "استمع أو اقرأ ثلاث مرات: افهم المعنى أولًا، ثم لاحظ تركيب الجملة، وأخيرًا اقرأ بصوت عالٍ.",
    )
    with st.container(border=True):
        for sentence in lesson.dialogue:
            highlighted(sentence, lesson)
    st.caption(
        label(
            "Audio laden sendet ausschließlich den deutschen Lektionstext an den Google-Sprachdienst (gTTS).",
            "تحميل الصوت يرسل نص الدرس الألماني فقط إلى خدمة Google الصوتية.",
        )
    )
    if st.button(label("Audio laden", "تحميل الصوت")):
        try:
            with st.spinner(label("Audio wird geladen …", "جارٍ تحميل الصوت…")):
                st.session_state["audio_" + lesson.id] = lesson_audio(" ".join(lesson.dialogue))
        except Exception:
            st.warning(
                label(
                    "Audio ist gerade nicht verfügbar. Lies den Text laut; du kannst später erneut laden.",
                    "الصوت غير متاح حاليًا. اقرأ بصوت عالٍ وحاول لاحقًا.",
                )
            )
    if "audio_" + lesson.id in st.session_state:
        st.audio(st.session_state["audio_" + lesson.id], format="audio/mp3")
    st.write(
        label(
            f"Durchgänge: {active['passes']}/3", f"مرات القراءة أو الاستماع: {active['passes']}/3"
        )
    )
    if st.button(label("Durchgang abgeschlossen", "أكملت مرة"), disabled=active["passes"] >= 3):
        active["passes"] = min(3, active["passes"] + 1)
        persist(store)
        st.rerun()
    with st.expander(label("Vokabelkarten & Satzstruktur", "بطاقات المفردات وتركيب الجملة")):
        for vocab in lesson.vocabulary:
            with st.container(border=True):
                st.markdown(f"**{vocab.term}** — {vocab.explanation_de}")
                st.write(vocab.example)
                if level() == "A1":
                    arabic(vocab.meaning_ar)
        st.info(lesson.grammar_de)
        if level() == "A1":
            arabic(lesson.grammar_ar)
        elif level() == "A2":
            with st.expander("Kurze Hilfe auf Arabisch"):
                arabic(lesson.grammar_ar)
    st.caption(lesson.culture)
    if st.button(
        label("Weiter zum Sprechen & Schreiben", "انتقل إلى التحدث والكتابة"),
        type="primary",
        disabled=active["passes"] < 3,
    ):
        advance(store)

elif phase == 1:
    st.info(
        label(
            "Fehler sind erlaubt – Flüssigkeit vor Perfektion.",
            "الأخطاء مسموحة، الطلاقة قبل الكمال.",
        )
    )
    instruction(lesson.speaking, lesson.speaking_ar)
    instruction(
        "Sprich etwa eine Minute. Höre dir die Aufnahme an oder übe ohne Mikrofon laut.",
        "تحدث نحو دقيقة. استمع إلى التسجيل أو تدرب بصوت عالٍ دون ميكروفون.",
    )
    recording = st.audio_input(
        label("Meine Sprechaufnahme", "تسجيل صوتي"), key=f"record_{lesson.id}"
    )
    if recording:
        st.audio(recording)
    st.caption(
        label(
            "Die Aufnahme wird nur in dieser Sitzung abgespielt, nicht in der Datenbank gespeichert oder an OpenAI gesendet.",
            "يُشغل التسجيل في هذه الجلسة فقط ولا يُحفظ في قاعدة البيانات ولا يُرسل إلى OpenAI.",
        )
    )
    with st.form(f"writing_{lesson.id}"):
        spoken = st.checkbox(
            label("Ich habe laut gesprochen.", "تدربت بصوت عالٍ."), value=active["spoken"]
        )
        rating = st.slider(
            label("Wie verständlich war ich? (Selbstbewertung)", "ما مدى وضوح كلامي؟ تقييم ذاتي"),
            1,
            5,
            active["rating"],
        )
        instruction(
            "Schreibe fünf eigene Sätze mit neuen Wörtern. Ein Satz pro Feld.",
            "اكتب خمس جمل من عندك باستخدام الكلمات الجديدة، جملة في كل حقل.",
        )
        sentences = [
            st.text_input(
                label(f"Satz {i + 1}", f"الجملة {i + 1}"),
                value=active["sentences"][i],
                max_chars=500,
                key=f"write_{lesson.id}_{i}",
            )
            for i in range(5)
        ]
        submitted = st.form_submit_button(label("Entwurf speichern", "حفظ المسودة"), type="primary")
    if submitted:
        active["sentences"] = [s[:500] for s in sentences]
        active["spoken"] = bool(spoken)
        active["rating"] = max(1, min(5, rating))
        persist(store)
        st.success(label("Entwurf gespeichert.", "تم حفظ المسودة."))
    ready = active["spoken"] and all(s.strip() for s in active["sentences"])
    st.caption(
        label(
            "Speichere deinen Entwurf vor dem Wechsel. Nicht gespeicherte Änderungen bleiben nicht erhalten.",
            "احفظ المسودة قبل الانتقال. التعديلات غير المحفوظة لن تُحفظ.",
        )
    )
    if st.button(
        label("Weiter zur Wiederholung", "انتقل إلى المراجعة"), type="primary", disabled=not ready
    ):
        validate_sentences(active["sentences"])
        advance(store)

elif phase == 2:
    instruction(
        "Antworte zuerst ohne Hilfe. Nach dem Prüfen siehst du die Lösung.",
        "أجب أولًا دون مساعدة. يظهر الحل بعد التحقق.",
    )
    if active["reviews"] is None:
        due = due_cards(store, uid, lesson.level)
        active["warmup"] = not bool(due)
        active["review_day"] = today().isoformat()
        active["reviews"] = due or [
            {"card": c, "bucket": "Startübung"} for c in build_cards(lesson)[:3]
        ]
        persist(store)
    if active["warmup"]:
        st.info(
            label(
                "Noch keine älteren Karten fällig. Heute übst du drei neue Karten; das ist keine Wiederholung von gestern.",
                "لا توجد بطاقات قديمة مستحقة. اليوم تتدرب على ثلاث بطاقات جديدة، وليست مراجعة من أمس.",
            )
        )
    else:
        st.caption(
            label(
                "Ziel: 5 Karten nach 24 Stunden und 3 nach etwa 7 Tagen. Fehlende Gruppen werden mit fälligen Karten ergänzt; Überfälliges bleibt im Plan.",
                "الهدف: خمس بطاقات بعد يوم وثلاث بعد نحو أسبوع. نستخدم البطاقات المستحقة فقط ونحتفظ بالمتأخر منها.",
            )
        )
    titles = {
        "cloze": label("Ergänze die Lücke", "أكمل الفراغ"),
        "order": label("Ordne die Wörter", "رتب الكلمات"),
        "translate": label("Übersetze ins Deutsche", "ترجم إلى الألمانية"),
    }
    for row in active["reviews"]:
        card = row["card"]
        cid = card["id"]
        with st.container(border=True):
            st.caption(titles[card["kind"]] + " · " + row["bucket"])
            if card["kind"] == "translate":
                arabic(card["prompt"])
            else:
                st.write(card["prompt"])
            if cid in active["review_done"]:
                st.success(label("Ergebnis gespeichert", "تم حفظ النتيجة"))
                continue
            answer_key = f"answer_{lesson.id}_{cid}"
            answer = st.text_input(label("Deine Antwort", "إجابتك"), key=answer_key, max_chars=500)
            check_key = "checked_" + answer_key
            if st.button(label("Prüfen", "تحقق"), key="check_" + cid, disabled=not answer.strip()):
                st.session_state[check_key] = {
                    "answer": answer,
                    "correct": matches(answer, card["answers"]),
                }
            checked = st.session_state.get(check_key)
            if checked:
                correct = checked["correct"]
                (st.success if correct else st.info)(
                    label(
                        "Passend!" if correct else "Vergleiche mit der Musterlösung.",
                        "قارن إجابتك بالحل النموذجي.",
                    )
                )
                st.write(" / ".join(card["answers"]))
                st.caption(
                    label(
                        "Bei Satzumstellungen steht das Verb im Aussagesatz an Position zwei. Weitere richtige Formulierungen sind möglich.",
                        "في الجملة الخبرية يأتي الفعل في الموضع الثاني. قد توجد صياغات صحيحة أخرى.",
                    )
                )
                alternative = False
                if not correct:
                    alternative = st.checkbox(
                        label(
                            "Meine erste Antwort war eine richtige Alternative (Selbstbewertung).",
                            "إجابتي الأولى بديل صحيح، تقييم ذاتي.",
                        ),
                        key="alt_" + cid,
                    )
                if st.button(label("Ergebnis übernehmen", "اعتماد النتيجة"), key="save_" + cid):
                    if not active["warmup"]:
                        review(store, uid, cid, bool(correct or alternative))
                    active["review_done"].append(cid)
                    persist(store)
                    st.rerun()
    if st.button(
        label("Weiter zu Feedback & Planung", "انتقل إلى التقييم والتخطيط"),
        type="primary",
        disabled=len(active["review_done"]) < len(active["reviews"]),
    ):
        advance(store)

else:
    st.subheader(label("Deine fünf Sätze", "جملك الخمس"))
    for i, sentence in enumerate(active["sentences"], 1):
        st.write(f"{i}. {sentence}")
    if not setting("OPENAI_API_KEY"):
        st.info(
            label(
                "KI-Korrektur ist hier nicht eingerichtet. Nutze die Selbstkontrolle; deine Sätze wurden nicht automatisch korrigiert.",
                "التصحيح بالذكاء الاصطناعي غير مفعّل. استخدم المراجعة الذاتية؛ لم تُصحح جملك آليًا.",
            )
        )
    else:
        consent = st.checkbox(
            label(
                "Meine fünf Sätze zur KI-Korrektur an OpenAI senden.",
                "أوافق على إرسال جملي الخمس إلى OpenAI للتصحيح.",
            )
        )
        if st.button(
            label("Konstruktive Korrektur anfordern", "طلب التصحيح"),
            disabled=not consent or active["feedback"] is not None,
        ):
            try:
                with st.spinner(label("Deine Sätze werden geprüft …", "جارٍ مراجعة جملك…")):
                    feedback = correct_writing(
                        active["sentences"],
                        lesson.level,
                        setting("OPENAI_API_KEY"),
                        setting("OPENAI_MODEL", "gpt-4o-mini"),
                    )
                active["feedback"] = feedback.model_dump()
                active["next_goal"] = feedback.next_goal
                persist(store)
            except Exception:
                st.warning(
                    label(
                        "Die KI-Korrektur ist gerade nicht verfügbar. Deine Sätze bleiben gespeichert; du kannst erneut versuchen oder die Selbstkontrolle nutzen.",
                        "التصحيح غير متاح حاليًا. جملك محفوظة؛ حاول مجددًا أو راجعها ذاتيًا.",
                    )
                )
    if active["feedback"]:
        feedback = active["feedback"]
        st.success(feedback["encouragement"])
        for correction in feedback["corrections"]:
            with st.container(border=True):
                st.write(correction["original"])
                st.markdown("**" + correction["corrected"] + "**")
                st.write(correction["explanation_de"])
                if level() == "A1":
                    arabic(correction["explanation_ar"])
                elif level() == "A2":
                    with st.expander("Kurze Erklärung auf Arabisch"):
                        arabic(correction["explanation_ar"])
    else:
        instruction(
            "Selbstkontrolle: Wo steht das Verb? Sind Nomen großgeschrieben? Passt jeder Satz zu deiner Aussage?",
            "راجع بنفسك: أين الفعل؟ هل تبدأ الأسماء بحرف كبير؟ هل تعبّر كل جملة عن المعنى المقصود؟",
        )
        st.info(lesson.grammar_de)
    if not active["next_goal"]:
        active["next_goal"] = (
            f"Morgen wiederhole ich fünf fällige Karten und spreche eine Minute zum Thema: {lesson.title}."
        )
    reflection = st.text_area(
        label(
            "Was gelingt dir schon? Was möchtest du üben?",
            "ما الذي أتقنته وما الذي تريد التدرب عليه؟",
        ),
        value=active["reflection"],
        max_chars=1000,
    )
    next_goal = st.text_input(
        label("Mein konkretes Ziel für morgen", "هدفي المحدد للغد"),
        value=active["next_goal"],
        max_chars=400,
    )
    show_stats(store)
    if st.button(
        label("Lektion abschließen & speichern", "إنهاء الدرس وحفظه"),
        type="primary",
        disabled=not next_goal.strip(),
    ):
        active["reflection"] = reflection[:1000]
        active["next_goal"] = next_goal[:400]
        persist(store)
        seconds = int(
            sum(
                min(elapsed(t), limit) for t, limit in zip(active["timers"], DURATIONS, strict=True)
            )
        )
        store.complete(uid, lesson, seconds)
        st.session_state.just_completed = next_goal
        st.session_state.active = None
        st.rerun()

with st.expander(label("Lektion pausieren", "إيقاف الدرس مؤقتًا")):
    if st.button(label("Speichern und Timer pausieren", "حفظ وإيقاف المؤقت")):
        from core.timer import pause

        pause(active["timers"][phase])
        persist(store)
        st.success(
            label(
                "Gespeichert. Mit deinem Lerncode kannst du später fortsetzen.",
                "تم الحفظ. يمكنك المتابعة لاحقًا باستخدام رمز التعلم.",
            )
        )
