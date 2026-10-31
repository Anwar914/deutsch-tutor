# Deutsch-Tutor · A1 / A2 / B1

Eine ausführbare Streamlit-App für arabischsprachige Erwachsene: **Input → Output → Wiederholung**. Python 3.11, 30 eigenständige lokale Lektionen, optionale OpenAI-Lektionsgenerierung und Schreibkorrektur, SQLite-Lernprofile und ein 45-Minuten-Tagesprotokoll.

Das Lernkonzept folgt der vom Auftraggeber beschriebenen Input-Output-Schleife. Keine offizielle Verbindung zu Anwar Algassab oder Deutsche Welle. Alle mitgelieferten Dialoge wurden für dieses Repository neu formuliert. [DW Learn German](https://learngerman.dw.com/ar/) dient ausschließlich als Themen-/Niveauorientierung; keine Inhalte werden gescrapt oder kopiert.

## Sofort starten

Voraussetzung: Python **3.11** und Git. Im entpackten Repository:

### Windows / PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

Im Browser [localhost:8501](http://localhost:8501) öffnen und **A1**, **A2** oder **B1** wählen. Sofort erscheint die erste noch nicht abgeschlossene Lektion. Alle zehn Themen pro Niveau sind zusätzlich manuell auswählbar. Nach zehn abgeschlossenen lokalen Lektionen ist Wiederholung möglich. Es wird keine bestandene Niveauprüfung behauptet.

Ohne API-Schlüssel funktioniert der komplette Lernablauf mit lokalen Inhalten, Aufnahme, Selbstkontrolle, Wiederholung und Fortschritt. **KI-Korrektur und KI-Lektionsgenerierung sind dann ausdrücklich nicht verfügbar.** gTTS benötigt eine Internetverbindung; beim Ausfall bleibt lautes Lesen möglich.

## Architektur

```text
app.py                       Navigation, Profilinitialisierung, RTL
pages/
  lesson.py                  Alle vier Lernphasen
  progress.py                Lernserie, Diagramm, Wiederholungsplan, Tagesziel
  profile.py                 Lerncode, Export/Import, Löschung
core/
  models.py                  Pydantic-Verträge und Inhaltsvalidierung
  lesson_engine.py           Lokaler Katalog und OpenAI-Generierung
  spaced_repetition.py       Kartentypen, Auswahl, Leitner-light
  storage.py                 SQLite-Transaktionen und Profiltrennung
  timer.py                   Pausierbare Timer-Arithmetik
  tts.py                     gTTS-Sprachausgabe
  feedback.py                OpenAI-Schreibkorrektur
  ui.py                      Sprache, Cache, sichere Ausgabe, Zustand
data/lessons_a1.json          10 vollständige Lektionen
data/lessons_a2.json          10 vollständige Lektionen
data/lessons_b1.json          10 vollständige Lektionen
scripts/build_catalog.py     Reproduzierbarer Original-Katalog
tests/                       Domain-, API-Vertrags- und Streamlit-Tests
.github/workflows/ci.yml      Ruff und pytest auf Python 3.11 / 3.12
.streamlit/                  Hell/Dunkel-Konfiguration und Secrets-Beispiel
Dockerfile, compose.yaml     Optionaler Betrieb mit persistentem Volume
```

Streamlit-Seiten steuern die Oberfläche, `core` enthält die Fachlogik. Moderne Navigation via `st.navigation` nutzt das vom Auftraggeber gewünschte `pages/`-Verzeichnis. Öffentliche Lektionen und TTS werden begrenzt mit `st.cache_data` gecacht; private Texte werden nicht im globalen Cache abgelegt. SQLite-Verbindungen sind kurzlebig und transaktional. Nutzerwerte werden ausschließlich als SQL-Parameter übergeben.

## Tagesprotokoll und Bedienung

| Phase | Zeit | Umsetzung |
|---|---:|---|
| Verstehen | 15 Min. | 5–8 Sätze A1/A2, 8–12 B1; hervorgehobene Schlüsselwörter, Vokabelkarten, Audio, drei bestätigte Durchgänge |
| Sprechen & Schreiben | 15 Min. | `st.audio_input`, lautes Üben auch ohne Mikrofon, Selbstbewertung, fünf eigene Sätze |
| Wiederholen | 10 Min. | Lücken, Wortreihenfolge und auf A1/A2 Arabisch→Deutsch; Lösung erst nach Antwort |
| Feedback & Planung | 5 Min. | Explizit angeforderte KI-Korrektur oder klar bezeichnete Selbstkontrolle, Reflexion, nächstes Ziel |

Die Phasenuhr läuft unabhängig vom Schreibformular (`st.fragment`, Aktualisierung alle fünf Sekunden). Pause und Fortsetzen verändern keine Eingaben. Die Dauer ist ein Lernziel, keine Sperre: Nach Erledigung der Aufgaben kann man früher wechseln und nach Zeitablauf weiterarbeiten. Der Fortschrittsbalken zählt abgeschlossene Phasen; der zweite Balken zeigt die Phasenzeit. Erfasste Zeit ist verstrichene Timerzeit, kein Nachweis aktiver Aufmerksamkeit.

Formulare müssen mit **Entwurf speichern** bestätigt werden. Timer-Snapshots und Phasenwechsel werden gespeichert; nach Wiederherstellung startet der Timer **pausiert**, damit Offline-Zeit nicht als Lernzeit zählt. Der Lerncode muss separat gesichert werden. Nach einem Browser-Neustart auf **Profil & Sicherung** den Code eingeben. Ein unbekannter Code öffnet keine fremden Profile. Beim endgültigen Abschluss werden aktuelle Entwürfe entfernt; Reflexion und nächstes Tagesziel bleiben gespeichert.

### Sprache und Niveau

- A1: deutsche Anweisungen mit arabischer Unterstützung; arabische Absätze erhalten `dir="rtl"` und isolierte CSS-Regeln.
- A2: deutsche Oberfläche; kurze arabische Grammatikhilfe/Korrekturerklärung aufklappbar. Arabisch erscheint auch in expliziten Übersetzungsaufgaben.
- B1: systemseitige Lerntexte, Anweisungen und Übungen ausschließlich Deutsch; keine Übersetzungsaufgaben aus dem Arabischen. Eigene Nutzereingaben werden unverändert angezeigt.
- Keine Satz-für-Satz-Übersetzung der Dialoge. Einzelne Bedeutungen und Grammatik dienen als Unterstützung.
- Zehn Themen: Kennenlernen, Einkaufen, Termine, Bus, Wohnung, Arztpraxis, Arbeitsplatz, Schule, Bürgerbüro, Nachbarschaft.

### Wiederholungslogik

Bei Lektionsabschluss werden acht Karten aufgenommen. Wiederholte Abschlüsse legen dieselben Karten nicht doppelt an. Neue Karten sind am nächsten **Kalendertag in Europe/Berlin** fällig; „24 Stunden“ ist die didaktische Kurzbezeichnung für diesen Tagesrhythmus, kein minutengenauer Countdown.

Die Auswahl priorisiert fünf fällige Karten aus der Lektion des Vortags und drei aus der Lektion vor sieben Tagen. Fehlen passende Karten, werden verfügbare überfällige Karten nachgezogen; maximal acht pro Einheit. Es werden niemals vergangene Lektionen erfunden. Am ersten Tag gibt es stattdessen drei klar gekennzeichnete Startübungen mit neuen Inhalten. Fällige Karten können bei weniger als acht Einträgen auch eine kürzere Runde ergeben.

Leitner-light: Einführung → +1 Tag; erste erfolgreiche Wiederholung → +6 Tage (bei pünktlicher Wiederholung also Tag 7); danach +14, +30 und +60 Tage. Fehler setzen die Stufe zurück und planen +1 Tag. Pro Karte und Tag wird nur ein Ergebnis gespeichert, auch bei Doppelklick oder zwei Tabs. Überfällige Karten verfallen nicht. Ein richtiges Ergebnis kann bei gültigen Varianten ausdrücklich selbst bestätigt werden; das System behauptet keine semantische KI-Bewertung. „Gefestigt“ bedeutet drei aufeinanderfolgende Erfolge, nicht ein offiziell erreichtes Sprachniveau.

## OpenAI aktivieren

Windows:

```powershell
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

macOS/Linux:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

In der lokalen, git-ignorierten Datei `OPENAI_API_KEY` mit dem eigenen Schlüssel befüllen. `OPENAI_MODEL` ist konfigurierbar, Standard `gpt-4o-mini`. Das Modell muss für das verwendete Konto verfügbar sein und strukturierte Antworten unterstützen. Alternativ Umgebungsvariablen `OPENAI_API_KEY`, `OPENAI_MODEL`, `TUTOR_DB_PATH` setzen. Umgebungsvariablen haben Vorrang, leere Werte fallen auf Secrets zurück.

Es gibt **keine automatischen KI-Aufrufe** beim Öffnen oder bei jedem Streamlit-Neulauf. Eigene Lektionen werden nur über den entsprechenden Button erstellt. Schreibkorrektur benötigt zusätzlich Zustimmung zur Übertragung. Die Integration nutzt die [OpenAI Responses API mit strukturierten Ausgaben](https://developers.openai.com/api/docs/guides/structured-outputs) und Pydantic. Es werden `store=False`, Timeout, ein begrenzter Retry und eine Ausgabelängenbegrenzung gesetzt. Verweigerungen, Netzwerkfehler und unvollständige Rückgaben führen zu einer verständlichen Meldung, ohne gespeicherte Arbeit zu verwerfen.

`store=False` ist keine Zusage über vollständige Datenlöschung beim Anbieter. Bitte keine persönlichen, medizinischen oder vertraulichen Angaben in die Übungstexte schreiben. KI-Ergebnisse sind Lernhilfe und können Fehler enthalten. Generierte Inhalte werden strukturell geprüft, jedoch nicht extern pädagogisch zertifiziert.

## Daten und Datenschutz

- Zufälliger 192-Bit-Lerncode als **Bearer-Zugang**; in SQLite wird nur sein SHA-256-Hash gespeichert. Das ist kein E-Mail-Login und bietet keine Passwortzurücksetzung.
- Wer den Code besitzt, kann das Profil öffnen. Nicht in URLs, Screenshots oder öffentlichen Repositories teilen.
- Getrennte Datenbankabfragen je Profil; keine öffentliche Nutzerliste.
- Gespeichert werden Entwürfe während der laufenden Lektion, Timer-Snapshots, Karten, Ergebnisse, Abschlüsse und Tagesziel/Reflexion.
- Mikrofonaufnahmen gelangen zur Wiedergabe in den Streamlit-Sitzungsspeicher, werden nicht in SQLite abgelegt und nicht an OpenAI gesendet. Bei Seitenwechsel/Neustart gehen sie verloren.
- TTS überträgt den deutschen Lektionstext an den von gTTS verwendeten Google-Dienst, erst beim Klick auf **Audio laden**.
- JSON-Export enthält abgeschlossene Lektionen, Karten, Bewertungen und Tagesplan; keine Zugangscodes, Audiodateien oder laufenden Entwürfe. Import wird vollständig validiert und dann atomar zusammengeführt. Bei bestehenden Schlüsseln bleibt der aktuelle Stand erhalten.
- Profil und zugehörige Daten können mit Bestätigung gelöscht werden. Bereits heruntergeladene Backups werden dadurch nicht gelöscht.
- SQLite und Backups sind nicht anwendungsseitig verschlüsselt. Betriebssystem-/Volume-Schutz obliegt dem Betreiber.

## Tests und Qualität

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

Unter Windows ohne aktivierte Umgebung jeweils `.\.venv\Scripts\python.exe` statt `python` verwenden.

Tests prüfen Inhaltsschemata, Satzbudgets, B1-Sprachregel, Tages-/Wochenintervalle, Überfälligkeit, Doppelbewertung, Profildatentrennung, Streak, Export/Import, fehlerhafte Backups, Timer, API-Verträge und einen vollständigen Streamlit-Lektionsdurchlauf ohne API-Schlüssel. API-Vertragstests simulieren den Anbieter und kosten kein Geld. Browser-Mikrofonrechte sowie echte kostenpflichtige OpenAI-Antworten sind nicht Bestandteil der automatischen Tests.

Der handgeschriebene Katalog lässt sich neu erzeugen:

```bash
python scripts/build_catalog.py
```

## GitHub-Repository anlegen und pushen

1. Auf [GitHub](https://github.com/new) ein leeres Repository `deutsch-tutor` erstellen. Keine zusätzliche README/.gitignore erzeugen.
2. Im lokalen Projektordner ausführen:

```bash
git init
git branch -M main
git add .
git status
git commit -m "Initial implementation of Deutsch-Tutor"
```

3. Die von GitHub angezeigte Remote-URL verwenden. `DEIN-NAME` durch den eigenen GitHub-Namen ersetzen:

```bash
git remote add origin https://github.com/DEIN-NAME/deutsch-tutor.git
git push -u origin main
```

Vor dem Commit prüfen, dass weder `.streamlit/secrets.toml` noch `storage/` oder Backups enthalten sind. Der enthaltene Workflow läuft bei Push und Pull Request. Es wurde noch kein Remote-Repository angelegt oder veröffentlicht.

## Streamlit Community Cloud

1. Repository nach GitHub pushen.
2. Auf [Streamlit Community Cloud](https://share.streamlit.io/) anmelden und **Create app** wählen.
3. Repository `deutsch-tutor`, Branch `main`, Einstieg `app.py` auswählen.
4. Unter erweiterten Einstellungen **Python 3.11** wählen.
5. Optional den Inhalt der lokalen Secrets-Datei in das **Secrets**-Feld eintragen; niemals die Secrets-Datei committen.
6. **Deploy** klicken und die drei Niveau-Starts prüfen.
7. Im HTTPS-Aufruf Mikrofonzugriff erlauben; Audioaufnahme funktioniert bei lokaler Entwicklung über localhost ebenfalls.

[Offizielle Deployment-Anleitung](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

**Persistenzgrenze:** Community Cloud bietet keine Garantie für den Bestand der lokal geschriebenen SQLite-Datei über Neustarts, Neuaufbau oder Instanzwechsel. Der Lerncode allein stellt nach Dateiverlust keine Daten wieder her. Für eine Demo regelmäßig exportieren; für dauerhaften Mehrnutzerbetrieb SQLite auf ein persistentes Volume legen oder PostgreSQL integrieren. JSON-Sicherungen können in ein neues Profil importiert werden.

## Optional: Docker mit dauerhaftem Volume

```bash
docker compose up --build -d
docker compose logs -f tutor
```

Die App läuft auf [localhost:8501](http://localhost:8501). `compose.yaml` speichert SQLite im benannten Volume `tutor-data`, das einen normalen Container-Neustart überlebt. `docker compose down -v` würde das Volume löschen; für den normalen Stopp `docker compose down` verwenden. Für öffentlichen Betrieb HTTPS über einen Reverse Proxy und regelmäßige Backups einrichten. `OPENAI_API_KEY` und `OPENAI_MODEL` können vor dem Start als Umgebungsvariablen gesetzt werden.

## Offene Punkte / Erweiterungen

- E-Mail/OIDC-Login, Wiederherstellung und serverseitige Nutzungs-/Kostenlimits für einen öffentlichen Dienst.
- Dauerhaft verwaltete Datenbank und automatisierte Backups statt lokaler Cloud-Datei.
- Optionale Spracherkennung und getrennt getestetes Aussprachefeedback mit ausdrücklicher Einwilligung.
- Pädagogische Prüfung durch DaF/DaZ-Lehrkräfte und Nutzertests mit der Zielgruppe.
- Semantische Bewertung freier Antworten statt exaktem Vergleich plus Selbstbewertung.
- Genauere Zeitintervalle/FSRS, Lernstandsdiagnose und längerfristige adaptive Curricula.
- Browser-Sprachausgabe als netzunabhängigere Alternative zu gTTS (abhängig von installierten Stimmen).

---

## العربية — دليل التشغيل والاستخدام

**Deutsch-Tutor** تطبيق لتعلم الألمانية بمستويات A1 وA2 وB1. يتضمن 30 درسًا أصليًا، عشرة لكل مستوى، وفق مبدأ: **الفهم ← التطبيق ← المراجعة المتباعدة**. لا توجد علاقة رسمية بالمصادر التعليمية المذكورة، ولم تُنسخ حواراتها.

### التثبيت المحلي

ثبّت Python 3.11 ثم افتح مجلد المشروع. في Windows:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

في macOS أو Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m streamlit run app.py
```

افتح [التطبيق المحلي](http://localhost:8501) واختر المستوى، فيظهر الدرس مباشرة. لتغيير الألوان اختر الوضع الفاتح أو الداكن من إعدادات Streamlit أعلى الصفحة.

### خطة اليوم

1. **15 دقيقة للفهم:** اقرأ أو استمع ثلاث مرات، ثم اضغط زر إكمال كل مرة. ستجد الكلمات الأساسية وشرح التركيب دون ترجمة الحوار كلمة بكلمة.
2. **15 دقيقة للتطبيق:** تحدث نحو دقيقة، وسجّل صوتك اختياريًا، وقيّم وضوحك بنفسك. اكتب خمس جمل واحفظ المسودة.
3. **10 دقائق للمراجعة:** أجب دون مساعدة، ثم تحقق من الحل. في أول يوم توجد تدريبات تمهيدية بدل اختلاق مراجعات سابقة.
4. **5 دقائق للتقييم:** استخدم التصحيح بالذكاء الاصطناعي عند تفعيله أو المراجعة الذاتية، وحدد هدف الغد ثم أنهِ الدرس.

المؤقت قابل للإيقاف ولا يمنعك من التقدم مبكرًا أو إكمال المهمة بعد انتهاء الوقت. يعرض الزمن المنقضي ولا يقيس انتباهك الحقيقي. تبدأ المؤقتات متوقفة عند استعادة درس محفوظ.

### رمز التعلم والبيانات

احفظ **رمز التعلم** من الشريط الجانبي. بعد إعادة فتح المتصفح أدخله في صفحة الملف لاستعادة تقدمك. الرمز وسيلة وصول خاصة، ومن يعرفه يستطيع فتح ملفك؛ لا تشاركه. لا يوجد تسجيل دخول بالبريد الإلكتروني أو استرداد كلمة مرور في هذه النسخة.

تُحفظ البطاقات والمراجعات والإنجازات وهدف اليوم التالي في SQLite لكل ملف على حدة. لا يُحفظ الصوت في قاعدة البيانات ولا يُرسل إلى OpenAI. يمكن تصدير نسخة JSON واستيرادها لاحقًا. تتضمن النسخة الدروس المكتملة والبطاقات والنتائج والهدف، لكنها لا تتضمن التسجيلات أو المسودات الحالية. يمكن حذف الملف وبياناته من صفحة الإعدادات بعد التأكيد.

### تفعيل الذكاء الاصطناعي

انسخ `.streamlit/secrets.toml.example` إلى `.streamlit/secrets.toml` وضع مفتاحك في `OPENAI_API_KEY`. يمكن اختيار نموذج يدعم المخرجات المنظمة عبر `OPENAI_MODEL`. لا ترفع ملف المفاتيح إلى GitHub.

دون مفتاح تعمل الدروس المحلية والمراجعات والتسجيل والتقدم، لكن لا يوجد تصحيح آلي؛ يعرض التطبيق ذلك بوضوح. لا تُرسل جملك إلى OpenAI إلا عند الموافقة والضغط على زر التصحيح. إنشاء درس جديد يرسل الموضوع فقط. توليد الصوت عبر gTTS يحتاج الإنترنت ويرسل نص الدرس الألماني إلى الخدمة الصوتية عند الطلب. تجنب كتابة بيانات شخصية أو حساسة في التدريبات.

### المراجعة المتباعدة

تُضاف ثماني بطاقات عند إكمال الدرس. الأولوية لخمس بطاقات من اليوم السابق وثلاث من قبل أسبوع، مع استخدام البطاقات المتأخرة المتاحة عند نقص المجموعة. الحساب حسب أيام التقويم بتوقيت برلين، وليس مرور 24 ساعة بالدقيقة. لا تضيع البطاقات المتأخرة. الخطأ يعيد البطاقة إلى مراجعة اليوم التالي. البطاقة الراسخة هي التي حصلت على ثلاث إجابات صحيحة متتالية؛ هذا ليس شهادة مستوى لغوي.

### GitHub والنشر

أنشئ مستودعًا فارغًا باسم `deutsch-tutor` في GitHub ثم نفذ أوامر `git init` و`git add` و`git commit` و`git push` المذكورة في القسم الألماني، مع استبدال اسم المستخدم في الرابط باسم حسابك.

في [Streamlit Community Cloud](https://share.streamlit.io/) اختر إنشاء تطبيق، ثم المستودع والفرع `main` والملف `app.py`. اختر Python 3.11 وأدخل المفاتيح في حقل Secrets ثم انشر التطبيق. افتح التطبيق عبر HTTPS واسمح بالميكروفون إذا أردت التسجيل.

**مهم:** ملف SQLite المحلي في Community Cloud قد يضيع عند إعادة التشغيل أو إعادة البناء. رمز التعلم وحده لا يعيد بيانات ملف محذوف. صدّر نسخًا دورية، أو استخدم Docker مع وحدة تخزين دائمة كما في `compose.yaml`، أو انقل قاعدة البيانات إلى خدمة دائمة قبل التشغيل العام.

### التحقق والتطوير

```bash
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

تشمل الاختبارات منطق التكرار وعزل الملفات واستعادة البيانات ومسار درس كامل. اختبارات OpenAI محاكاة لا تنفذ طلبات مدفوعة. من التوسعات الممكنة: تسجيل دخول كامل، التعرف على الكلام، مراجعة تربوية للمحتوى، وقاعدة بيانات دائمة مع حدود لاستخدام الذكاء الاصطناعي.
