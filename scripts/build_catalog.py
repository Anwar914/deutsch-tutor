"""Build the original, hand-authored 30-lesson catalogue (no external content)."""

import json
from pathlib import Path

# Each row: term | plain German explanation | Arabic meaning | example | cloze answer.
# Arabic translations below are separate recall sentences, not dialogue translations.
TOPICS = [
    {
        "slug": "vorstellen",
        "title": "Neue Menschen kennenlernen",
        "goal": "Du stellst dich vor und fragst nach Namen und Wohnort.",
        "a1": [
            "Ich heiße Samira.",
            "Wie heißen Sie?",
            "Ich heiße Jonas.",
            "Ich wohne in Berlin.",
            "Wo wohnen Sie?",
            "Ich wohne auch hier.",
            "Wir lernen zusammen Deutsch.",
        ],
        "a2": [
            "Ich heiße Samira und besuche seit einem Monat einen Deutschkurs.",
            "Früher habe ich in Bonn gewohnt.",
            "Jetzt wohne ich in Berlin, weil ich hier arbeite.",
            "Mein Nachbar heißt Jonas.",
            "Wir sprechen nach dem Kurs oft miteinander.",
            "Manchmal verstehe ich ein Wort nicht.",
            "Dann bitte ich ihn um eine Erklärung.",
        ],
        "b1": [
            "Als Samira nach Berlin gezogen ist, kannte sie dort niemanden.",
            "Deshalb hat sie sich für einen Sprachkurs angemeldet.",
            "In der ersten Pause stellt sie sich ihrem Sitznachbarn Jonas vor.",
            "Sie erzählt, dass sie früher in Bonn gewohnt hat.",
            "Jonas interessiert sich dafür, welche Sprachen sie spricht.",
            "Samira erklärt, dass sie Arabisch spricht und gerade Deutsch lernt.",
            "Obwohl sie manchmal nach Wörtern suchen muss, spricht sie weiter.",
            "Jonas wartet geduldig und fragt freundlich nach.",
            "Sie vereinbaren, nach dem Kurs gemeinsam einen Kaffee zu trinken.",
        ],
        "grammar": [
            "Das Verb steht im Aussagesatz an Position zwei: Ich heiße Samira.",
            "يأتي الفعل في الموضع الثاني في الجملة الخبرية: Ich heiße Samira.",
        ],
        "speaking": "Stelle dich vor und frage eine andere Person nach Name und Wohnort.",
        "speaking_ar": "عرّف بنفسك واسأل شخصًا آخر عن اسمه ومكان سكنه.",
        "culture": "Bei einem ersten formellen Kontakt passt Sie; im Kurs kann man gemeinsam das Du vereinbaren.",
        "words": """heißen|einen Namen haben|يُدعى|Ich heiße Samira.|heiße
wohnen|an einem Ort leben|يسكن|Ich wohne in Berlin.|wohne
lernen|etwas Neues üben|يتعلم|Wir lernen Deutsch.|lernen
sprechen|mit Worten etwas sagen|يتكلم|Wir sprechen Deutsch.|sprechen
der Name|so heißt eine Person|الاسم|Mein Name ist Samira.|Name
die Stadt|ein Ort mit vielen Häusern|المدينة|Die Stadt ist groß.|Stadt
zusammen|mit anderen Personen|معًا|Wir lernen zusammen.|zusammen
fragen|eine Frage stellen|يسأل|Ich frage Jonas.|frage""",
        "translations": [
            "اسمي سميرة.",
            "أسكن في برلين.",
            "نحن نتعلم الألمانية.",
            "نحن نتحدث الألمانية.",
            "اسمي سميرة.",
            "المدينة كبيرة.",
            "نحن نتعلم معًا.",
            "أنا أسأل يوناس.",
        ],
    },
    {
        "slug": "einkaufen",
        "title": "Auf dem Wochenmarkt",
        "goal": "Du kaufst Lebensmittel und fragst nach Preisen.",
        "a1": [
            "Ich möchte zwei Äpfel kaufen.",
            "Was kosten die Äpfel?",
            "Sie kosten einen Euro.",
            "Ich brauche auch ein Brot.",
            "Das Brot kostet drei Euro.",
            "Kann ich mit Karte bezahlen?",
            "Ja, das geht.",
        ],
        "a2": [
            "Am Samstag kauft Karim auf dem Markt ein.",
            "Er braucht Äpfel und ein Brot für das Frühstück.",
            "Die Verkäuferin fragt, wie viel er möchte.",
            "Karim nimmt ein Kilo Äpfel, weil seine Familie Obst mag.",
            "Er fragt nach dem Preis für das Brot.",
            "Danach bezahlt er mit seiner Karte.",
            "Seine Einkäufe trägt er in einer eigenen Tasche nach Hause.",
        ],
        "b1": [
            "Karim kauft gern auf dem Wochenmarkt ein, weil er dort nach der Herkunft fragen kann.",
            "Heute möchte er Äpfel aus der Region kaufen.",
            "Die Verkäuferin erklärt, welche Sorten gerade verfügbar sind.",
            "Eine Sorte ist günstiger, hat aber kleine Druckstellen.",
            "Da Karim einen Kuchen backen möchte, stört ihn das nicht.",
            "Außerdem fragt er, ob er mit Karte bezahlen kann.",
            "Die Verkäuferin zeigt ihm das Kartenlesegerät.",
            "Karim legt die Lebensmittel in seine mitgebrachte Tasche.",
            "Zu Hause vergleicht er die Ausgaben mit seinem Einkaufsplan.",
        ],
        "grammar": [
            "Mit möchten formulierst du Wünsche: Ich möchte ein Brot kaufen.",
            "نستخدم möchte لطلب شيء بأدب، ويأتي الفعل الآخر في نهاية الجملة.",
        ],
        "speaking": "Kaufe Obst und Brot und frage nach Preis und Bezahlung.",
        "speaking_ar": "اشترِ فاكهة وخبزًا واسأل عن السعر وطريقة الدفع.",
        "culture": "Auf einem Markt können Zahlungsmöglichkeiten unterschiedlich sein; frage vor dem Einkauf nach.",
        "words": """kaufen|etwas gegen Geld bekommen|يشتري|Ich kaufe Brot.|kaufe
der Apfel|eine runde Frucht|التفاحة|Der Apfel ist rot.|Apfel
das Brot|ein Lebensmittel aus Mehl|الخبز|Das Brot ist frisch.|Brot
kosten|einen Preis haben|يكلّف|Die Äpfel kosten zwei Euro.|kosten
bezahlen|Geld für etwas geben|يدفع|Ich bezahle mit Karte.|bezahle
die Tasche|darin trägt man Dinge|الحقيبة|Ich habe eine Tasche.|Tasche
der Preis|so viel Geld kostet etwas|السعر|Der Preis ist gut.|Preis
brauchen|etwas nötig haben|يحتاج|Ich brauche Obst.|brauche""",
        "translations": [
            "أشتري خبزًا.",
            "التفاحة حمراء.",
            "الخبز طازج.",
            "التفاح يكلف يورويْن.",
            "أدفع بالبطاقة.",
            "لدي حقيبة.",
            "السعر جيد.",
            "أحتاج إلى فاكهة.",
        ],
    },
    {
        "slug": "termin",
        "title": "Einen Termin ändern",
        "goal": "Du vereinbarst einen Termin und schlägst eine andere Uhrzeit vor.",
        "a1": [
            "Ich möchte einen Termin.",
            "Haben Sie am Montag Zeit?",
            "Am Montag arbeite ich.",
            "Geht es am Dienstag?",
            "Ja, um zehn Uhr.",
            "Bitte bringen Sie Ihren Ausweis mit.",
            "Vielen Dank für Ihre Hilfe.",
        ],
        "a2": [
            "Ich habe am Montag einen Termin in der Sprachschule.",
            "Ich kann nicht kommen, weil ich arbeiten muss.",
            "Deshalb möchte ich meinen Termin verschieben.",
            "Passt Ihnen Dienstag um zehn Uhr?",
            "Können Sie die Uhrzeit bitte wiederholen?",
            "Dienstag um zehn Uhr passt mir gut.",
            "Ich bringe meinen Ausweis mit.",
        ],
        "b1": [
            "Samira hat einen Beratungstermin, den sie wegen ihrer Arbeit nicht wahrnehmen kann.",
            "Sie ruft in der Sprachschule an und erklärt die Situation.",
            "Die Mitarbeiterin schlägt ihr Dienstagvormittag vor.",
            "Samira antwortet, dass sie an diesem Tag erst ab elf Uhr Zeit hat.",
            "Gemeinsam finden sie einen passenden Termin am Nachmittag.",
            "Samira wiederholt das Datum und die Uhrzeit, damit kein Missverständnis entsteht.",
            "Außerdem fragt sie, welche Unterlagen sie mitbringen soll.",
            "Die Mitarbeiterin bittet sie um ihren Ausweis.",
            "Zum Schluss bittet Samira um eine kurze Bestätigung per E-Mail.",
        ],
        "grammar": [
            "Nach weil steht das konjugierte Verb am Ende: weil ich arbeiten muss.",
            "بعد weil يأتي الفعل المصرف في النهاية: weil ich arbeiten muss.",
        ],
        "speaking": "Rufe in der Sprachschule an und vereinbare einen passenden Termin.",
        "speaking_ar": "اتصل بمدرسة اللغة واتفق على موعد مناسب.",
        "culture": "Wiederhole Tag und Uhrzeit zur Sicherheit; welche Unterlagen nötig sind, hängt vom jeweiligen Termin ab.",
        "words": """der Termin|eine vereinbarte Zeit|الموعد|Ich habe einen Termin.|Termin
die Zeit|eine freie Stunde oder Minute|الوقت|Ich habe Zeit.|Zeit
arbeiten|einen Beruf ausüben|يعمل|Ich muss arbeiten.|arbeiten
verschieben|einen anderen Zeitpunkt wählen|يغيّر وقت الموعد|Ich möchte den Termin verschieben.|verschieben
wiederholen|noch einmal sagen|يكرر|Bitte wiederholen Sie die Uhrzeit.|wiederholen
der Ausweis|ein Dokument zur Identität|وثيقة الهوية|Ich bringe meinen Ausweis mit.|Ausweis
passen|geeignet sein|يناسب|Dienstag passt gut.|passt
mitbringen|etwas dabei haben|يحضر معه|Bitte bringen Sie Ihren Ausweis mit.|bringen""",
        "translations": [
            "لدي موعد.",
            "لدي وقت.",
            "يجب أن أعمل.",
            "أود تغيير موعدي.",
            "يرجى تكرار الساعة.",
            "أحضر وثيقة هويتي معي.",
            "الثلاثاء مناسب.",
            "يرجى إحضار وثيقة هويتك.",
        ],
    },
    {
        "slug": "bus",
        "title": "Mit dem Bus unterwegs",
        "goal": "Du fragst nach einer Verbindung und findest die richtige Haltestelle.",
        "a1": [
            "Wo ist die Haltestelle?",
            "Die Haltestelle ist dort.",
            "Fährt der Bus zum Bahnhof?",
            "Ja, nehmen Sie die Linie fünf.",
            "Ich brauche eine Fahrkarte.",
            "Der Bus kommt um acht Uhr.",
            "Am Bahnhof steige ich aus.",
        ],
        "a2": [
            "Nour wartet an der Haltestelle auf den Bus.",
            "Sie möchte zum Bahnhof fahren.",
            "Auf der Anzeige steht, dass der Bus später kommt.",
            "Nour fragt einen anderen Fahrgast nach einer Verbindung.",
            "Er empfiehlt ihr die Linie fünf.",
            "Sie kauft eine Fahrkarte und steigt ein.",
            "Am Bahnhof muss sie in einen Zug umsteigen.",
        ],
        "b1": [
            "Nour möchte rechtzeitig am Bahnhof sein, weil sie einen Zug erreichen muss.",
            "An der Haltestelle erfährt sie, dass ihr Bus Verspätung hat.",
            "Sie prüft auf der Anzeige, ob es eine andere Verbindung gibt.",
            "Ein Fahrgast empfiehlt ihr, eine andere Linie zu nehmen.",
            "Diese fährt häufiger, hält aber weiter vom Bahnhof entfernt.",
            "Nour entscheidet sich trotzdem dafür, weil sie noch genug Zeit hat.",
            "Während der Fahrt kontrolliert sie die nächsten Haltestellen.",
            "Als sie aussteigt, fragt sie nach dem kürzesten Fußweg.",
            "Beim nächsten Mal möchte sie etwas mehr Zeit einplanen.",
        ],
        "grammar": [
            "Trennbare Verben: Ich steige am Bahnhof aus. Mit müssen: Ich muss aussteigen.",
            "الفعل القابل للانفصال: Ich steige aus. ومع müssen يبقى كاملًا: Ich muss aussteigen.",
        ],
        "speaking": "Frage nach einem Bus zum Bahnhof und erkläre, wo du aussteigen möchtest.",
        "speaking_ar": "اسأل عن حافلة إلى محطة القطار واذكر أين تريد النزول.",
        "culture": "Tickets und Entwertung unterscheiden sich je nach Verkehrsverbund; lies die Hinweise am Automaten.",
        "words": """die Haltestelle|hier hält der Bus|موقف الحافلة|Die Haltestelle ist dort.|Haltestelle
der Bahnhof|hier fahren Züge ab|محطة القطار|Ich fahre zum Bahnhof.|Bahnhof
die Fahrkarte|ein Ticket für die Fahrt|تذكرة السفر|Ich kaufe eine Fahrkarte.|Fahrkarte
fahren|mit einem Fahrzeug unterwegs sein|يذهب بوسيلة نقل|Wir fahren mit dem Bus.|fahren
einsteigen|in ein Fahrzeug gehen|يركب|Ich steige hier ein.|steige
aussteigen|ein Fahrzeug verlassen|ينزل|Am Bahnhof steige ich aus.|aus
umsteigen|das Fahrzeug wechseln|يبدّل وسيلة النقل|Ich muss umsteigen.|umsteigen
die Verspätung|später als geplant|التأخير|Der Bus hat Verspätung.|Verspätung""",
        "translations": [
            "موقف الحافلة هناك.",
            "أذهب إلى محطة القطار.",
            "أشتري تذكرة.",
            "نذهب بالحافلة.",
            "أركب هنا.",
            "أنزل عند محطة القطار.",
            "علي تبديل وسيلة النقل.",
            "الحافلة متأخرة.",
        ],
    },
    {
        "slug": "wohnen",
        "title": "Ein Problem in der Wohnung",
        "goal": "Du beschreibst eine Wohnung und meldest einen Defekt.",
        "a1": [
            "Meine Wohnung hat zwei Zimmer.",
            "Die Küche ist klein.",
            "Das Fenster ist kaputt.",
            "Ich rufe die Vermieterin an.",
            "Können Sie bitte kommen?",
            "Am Freitag bin ich zu Hause.",
            "Vielen Dank für Ihre Hilfe.",
        ],
        "a2": [
            "Seit gestern lässt sich das Fenster in der Küche nicht schließen.",
            "Leila ruft ihre Vermieterin an, weil es in der Wohnung kalt ist.",
            "Sie beschreibt das Problem möglichst genau.",
            "Die Vermieterin möchte einen Handwerker schicken.",
            "Leila ist am Freitag zu Hause und hat Zeit.",
            "Sie vereinbaren einen Termin am Vormittag.",
            "Leila schreibt sich die Uhrzeit auf.",
        ],
        "b1": [
            "Leila bemerkt, dass sich das Küchenfenster nicht mehr richtig schließen lässt.",
            "Zuerst prüft sie vorsichtig, ob etwas im Rahmen liegt.",
            "Da das Problem bestehen bleibt, schreibt sie ihrer Vermieterin eine Nachricht.",
            "Sie beschreibt den Defekt und fügt ein Foto hinzu.",
            "Außerdem nennt sie zwei Zeiten, zu denen sie zu Hause ist.",
            "Die Vermieterin antwortet, dass ein Handwerker kommen wird.",
            "Leila bittet um eine Bestätigung des vereinbarten Termins.",
            "Sie bewahrt die Nachrichten auf, damit sie die Absprachen später nachlesen kann.",
            "Nach der Reparatur bedankt sie sich für die schnelle Rückmeldung.",
        ],
        "grammar": [
            "Beschreibe mit sein und einem Adjektiv: Das Fenster ist kaputt; die Küche ist klein.",
            "نصف الأشياء باستخدام sein وصفة: Das Fenster ist kaputt.",
        ],
        "speaking": "Beschreibe deine Wohnung und melde ein kaputtes Fenster.",
        "speaking_ar": "صف مسكنك وأبلغ عن نافذة معطلة.",
        "culture": "Eine konkrete Beschreibung und ein vereinbarter Termin erleichtern die Kommunikation mit der Hausverwaltung.",
        "words": """die Wohnung|Räume zum Wohnen|الشقة|Meine Wohnung ist hell.|Wohnung
das Zimmer|ein Raum|الغرفة|Das Zimmer ist groß.|Zimmer
die Küche|hier kocht man|المطبخ|Die Küche ist klein.|Küche
das Fenster|eine Öffnung mit Glas|النافذة|Das Fenster ist kaputt.|Fenster
kaputt|nicht mehr in Ordnung|معطل|Die Lampe ist kaputt.|kaputt
die Vermieterin|sie vermietet die Wohnung|المؤجرة|Ich rufe die Vermieterin an.|Vermieterin
die Reparatur|etwas wieder in Ordnung bringen|الإصلاح|Die Reparatur ist am Freitag.|Reparatur
zu Hause|in der eigenen Wohnung|في المنزل|Ich bin zu Hause.|zu Hause""",
        "translations": [
            "شقتي مضيئة.",
            "الغرفة كبيرة.",
            "المطبخ صغير.",
            "النافذة معطلة.",
            "المصباح معطل.",
            "أتصل بالمؤجرة.",
            "الإصلاح يوم الجمعة.",
            "أنا في المنزل.",
        ],
    },
    {
        "slug": "arzt",
        "title": "In der Arztpraxis anrufen",
        "goal": "Du beschreibst dein Befinden und fragst nach einem Termin.",
        "a1": [
            "Guten Tag, ich brauche einen Termin.",
            "Ich habe seit heute Husten.",
            "Haben Sie auch Fieber?",
            "Das weiß ich nicht.",
            "Können Sie am Nachmittag kommen?",
            "Ja, ich habe Zeit.",
            "Bitte nennen Sie mir Ihren Namen.",
        ],
        "a2": [
            "Omar fühlt sich seit zwei Tagen nicht gut.",
            "Er ruft in der Praxis an und beschreibt seinen Husten.",
            "Die Mitarbeiterin fragt, seit wann er die Beschwerden hat.",
            "Omar antwortet langsam und nennt seinen Namen.",
            "Er bekommt einen Termin am Nachmittag.",
            "Er fragt, was er mitbringen soll.",
            "Zum Schluss wiederholt er die Uhrzeit.",
        ],
        "b1": [
            "Omar möchte einen Termin vereinbaren, weil er seit zwei Tagen Beschwerden hat.",
            "Am Telefon beschreibt er möglichst genau, wie er sich fühlt.",
            "Die Mitarbeiterin fragt nach seinem Namen und dem Beginn der Beschwerden.",
            "Omar versteht eine Frage nicht und bittet um eine einfachere Formulierung.",
            "Anschließend erklärt er, dass er am Vormittag arbeiten muss.",
            "Die Mitarbeiterin nennt ihm einen freien Termin am Nachmittag.",
            "Omar fragt, welche Unterlagen er zum Termin mitbringen soll.",
            "Er notiert sich die Antwort und wiederholt die Uhrzeit.",
            "Die medizinische Beurteilung überlässt er dem Praxisteam.",
        ],
        "grammar": [
            "Mit seit nennst du einen Beginn oder eine Dauer: seit heute; seit zwei Tagen.",
            "نستخدم seit لبداية حالة مستمرة أو مدتها: seit heute، seit zwei Tagen.",
        ],
        "speaking": "Rufe in einer Praxis an und bitte wegen Husten um einen Termin.",
        "speaking_ar": "اتصل بعيادة واطلب موعدًا بسبب السعال.",
        "culture": "Dies ist ein Sprachlern-Szenario. Über medizinische Dringlichkeit und Behandlung entscheidet medizinisches Fachpersonal.",
        "words": """die Praxis|Arbeitsort eines Arztes|العيادة|Ich rufe in der Praxis an.|Praxis
der Husten|ein häufiges Krankheitszeichen|السعال|Ich habe Husten.|Husten
das Fieber|eine erhöhte Körpertemperatur|الحمى|Haben Sie Fieber?|Fieber
krank|nicht gesund|مريض|Ich bin krank.|krank
seit|nennt den Beginn einer Dauer|منذ|Ich bin seit gestern krank.|seit
der Nachmittag|die Zeit nach Mittag|بعد الظهر|Ich komme am Nachmittag.|Nachmittag
der Name|so heißt eine Person|الاسم|Mein Name ist Omar.|Name
verstehen|die Bedeutung erkennen|يفهم|Ich verstehe die Frage nicht.|verstehe""",
        "translations": [
            "أتصل بالعيادة.",
            "لدي سعال.",
            "هل لديك حمى؟",
            "أنا مريض.",
            "أنا مريض منذ أمس.",
            "آتي بعد الظهر.",
            "اسمي عمر.",
            "لا أفهم السؤال.",
        ],
    },
    {
        "slug": "arbeit",
        "title": "Am Arbeitsplatz nachfragen",
        "goal": "Du klärst Aufgaben und Arbeitszeiten.",
        "a1": [
            "Heute ist mein erster Arbeitstag.",
            "Meine Kollegin heißt Eva.",
            "Wann beginnt die Arbeit?",
            "Wir beginnen um acht Uhr.",
            "Wo ist mein Arbeitsplatz?",
            "Ihr Tisch ist am Fenster.",
            "Bitte fragen Sie bei Problemen nach.",
        ],
        "a2": [
            "Heute beginnt Farid seine neue Arbeit.",
            "Seine Kollegin Eva zeigt ihm den Arbeitsplatz.",
            "Sie erklärt, welche Aufgabe er zuerst erledigen soll.",
            "Farid fragt nach, weil er ein Wort nicht versteht.",
            "Eva zeigt ihm ein Beispiel.",
            "Danach kann er die Aufgabe selbst machen.",
            "In der Pause sprechen sie über ihre Arbeitszeiten.",
        ],
        "b1": [
            "Farid möchte an seinem ersten Arbeitstag einen guten Überblick bekommen.",
            "Seine Kollegin erklärt ihm zuerst die wichtigsten Aufgaben.",
            "Da einige Begriffe neu für ihn sind, macht er sich Notizen.",
            "Er bittet Eva, einen Arbeitsschritt noch einmal zu zeigen.",
            "Anschließend erklärt er mit eigenen Worten, was er verstanden hat.",
            "So können beide mögliche Missverständnisse früh erkennen.",
            "Farid fragt außerdem, welche Aufgabe heute besonders dringend ist.",
            "Eva nennt ihm eine Reihenfolge und bietet ihre Unterstützung an.",
            "Am Ende des Tages besprechen sie, was bereits gut geklappt hat.",
        ],
        "grammar": [
            "Fragen mit W-Wort: Wann beginnt die Arbeit? Ohne W-Wort: Beginnt die Arbeit um acht Uhr?",
            "في سؤال أداة الاستفهام يأتي الفعل بعدها؛ وفي سؤال نعم أو لا يبدأ السؤال بالفعل.",
        ],
        "speaking": "Frage eine Kollegin nach einer Aufgabe und deiner Arbeitszeit.",
        "speaking_ar": "اسأل زميلة عن مهمة وعن وقت عملك.",
        "culture": "Nachfragen und Absprachen helfen im Team; konkrete Arbeitszeiten hängen vom jeweiligen Arbeitsplatz ab.",
        "words": """die Arbeit|berufliche Tätigkeit|العمل|Die Arbeit beginnt um acht Uhr.|Arbeit
die Kollegin|eine Frau im selben Team|الزميلة|Meine Kollegin heißt Eva.|Kollegin
die Aufgabe|etwas, das man erledigen soll|المهمة|Ich verstehe die Aufgabe.|Aufgabe
die Pause|eine Unterbrechung|الاستراحة|Die Pause beginnt jetzt.|Pause
beginnen|anfangen|يبدأ|Wir beginnen um acht Uhr.|beginnen
erklären|etwas verständlich machen|يشرح|Eva erklärt die Aufgabe.|erklärt
helfen|jemanden unterstützen|يساعد|Können Sie mir helfen?|helfen
nachfragen|um weitere Erklärung bitten|يستفسر|Ich frage noch einmal nach.|nach""",
        "translations": [
            "يبدأ العمل الساعة الثامنة.",
            "اسم زميلتي إيفا.",
            "أفهم المهمة.",
            "تبدأ الاستراحة الآن.",
            "نبدأ الساعة الثامنة.",
            "تشرح إيفا المهمة.",
            "هل يمكنك مساعدتي؟",
            "أستفسر مرة أخرى.",
        ],
    },
    {
        "slug": "schule",
        "title": "Kontakt mit der Schule",
        "goal": "Du fragst nach einem Gespräch und Informationen für den Schulalltag.",
        "a1": [
            "Mein Sohn geht in die Schule.",
            "Seine Lehrerin heißt Frau Weber.",
            "Ich möchte mit ihr sprechen.",
            "Haben Sie am Freitag Zeit?",
            "Ja, nach dem Unterricht.",
            "Ich habe eine Frage zu den Hausaufgaben.",
            "Wir sprechen um ein Uhr.",
        ],
        "a2": [
            "Rana möchte mit der Lehrerin ihres Sohnes sprechen.",
            "Sie schreibt eine kurze Nachricht und bittet um einen Termin.",
            "Ihr Sohn versteht die Hausaufgaben manchmal nicht.",
            "Frau Weber schlägt ein Gespräch nach dem Unterricht vor.",
            "Rana bestätigt den Termin am Freitag.",
            "Sie notiert vorher ihre Fragen.",
            "Beim Gespräch bittet sie um ein Beispiel für die Aufgabe.",
        ],
        "b1": [
            "Rana hat bemerkt, dass ihr Sohn bei den Hausaufgaben oft unsicher ist.",
            "Deshalb bittet sie seine Lehrerin um ein persönliches Gespräch.",
            "In ihrer Nachricht beschreibt sie kurz, welche Schwierigkeiten ihr aufgefallen sind.",
            "Die Lehrerin schlägt einen Termin nach dem Unterricht vor.",
            "Rana bereitet einige Fragen vor, damit sie nichts Wichtiges vergisst.",
            "Im Gespräch möchte sie erfahren, wie sie ihr Kind unterstützen kann.",
            "Frau Weber erklärt eine Aufgabe und nennt ein passendes Übungsangebot.",
            "Gemeinsam vereinbaren sie, nach zwei Wochen noch einmal zu sprechen.",
            "Rana hält die Absprachen in eigenen Worten fest.",
        ],
        "grammar": [
            "Mit mit steht der Dativ: mit der Lehrerin; mit dem Lehrer.",
            "بعد mit نستخدم الداتيف: mit der Lehrerin وmit dem Lehrer.",
        ],
        "speaking": "Bitte eine Lehrerin um ein Gespräch über die Hausaufgaben.",
        "speaking_ar": "اطلب من معلمة موعدًا للحديث عن الواجبات المنزلية.",
        "culture": "Schulen nutzen unterschiedliche Kontaktwege; frage nach, ob Nachrichten per App, E-Mail oder Heft gewünscht sind.",
        "words": """die Schule|ein Ort zum Lernen|المدرسة|Die Schule ist hier.|Schule
die Lehrerin|sie unterrichtet eine Klasse|المعلمة|Die Lehrerin heißt Frau Weber.|Lehrerin
der Unterricht|gemeinsames Lernen in der Klasse|الدرس|Der Unterricht beginnt jetzt.|Unterricht
die Hausaufgaben|Aufgaben für zu Hause|الواجبات المنزلية|Ich habe eine Frage zu den Hausaufgaben.|Hausaufgaben
das Gespräch|mehrere Menschen sprechen miteinander|المحادثة|Das Gespräch ist am Freitag.|Gespräch
die Nachricht|eine kurze Mitteilung|الرسالة|Ich schreibe eine Nachricht.|Nachricht
bestätigen|sagen, dass etwas richtig oder vereinbart ist|يؤكد|Ich bestätige den Termin.|bestätige
die Frage|man möchte etwas wissen|السؤال|Ich habe eine Frage.|Frage""",
        "translations": [
            "المدرسة هنا.",
            "اسم المعلمة السيدة فيبر.",
            "يبدأ الدرس الآن.",
            "لدي سؤال عن الواجبات المنزلية.",
            "المحادثة يوم الجمعة.",
            "أكتب رسالة.",
            "أؤكد الموعد.",
            "لدي سؤال.",
        ],
    },
    {
        "slug": "behoerde",
        "title": "Informationen im Bürgerbüro",
        "goal": "Du fragst nach einem Formular und den benötigten Unterlagen.",
        "a1": [
            "Ich habe einen Termin im Bürgerbüro.",
            "Wo ist der Eingang?",
            "Der Eingang ist rechts.",
            "Bitte warten Sie hier.",
            "Ich brauche ein Formular.",
            "Welche Unterlagen brauche ich?",
            "Bitte schauen Sie auf Ihre Terminbestätigung.",
        ],
        "a2": [
            "Yasin hat einen Termin im Bürgerbüro vereinbart.",
            "Vor dem Besuch liest er seine Terminbestätigung.",
            "Er versteht nicht genau, welche Unterlagen er braucht.",
            "Deshalb fragt er beim Büro nach.",
            "Eine Mitarbeiterin erklärt ihm die Liste.",
            "Yasin legt seine Dokumente in eine Mappe.",
            "Beim Termin bittet er um Hilfe mit einem Formular.",
        ],
        "b1": [
            "Yasin bereitet sich auf einen Termin im Bürgerbüro vor.",
            "Er hat eine Bestätigung erhalten, in der die benötigten Unterlagen stehen.",
            "Da ihm ein Begriff unklar ist, fragt er vor dem Termin nach.",
            "Die Mitarbeiterin erläutert, welches Dokument damit gemeint ist.",
            "Yasin möchte außerdem wissen, ob er eine Kopie mitbringen soll.",
            "Er notiert die Auskunft und kontrolliert seine Mappe.",
            "Vor Ort liest er das Formular zunächst in Ruhe durch.",
            "Bei einer unklaren Frage bittet er um eine Erklärung.",
            "Bevor er unterschreibt, prüft er seine Angaben noch einmal.",
        ],
        "grammar": [
            "Frage nach Dingen im Plural mit welche: Welche Unterlagen brauche ich?",
            "للسؤال عن أشياء بالجمع نستخدم welche: Welche Unterlagen brauche ich?",
        ],
        "speaking": "Frage im Bürgerbüro nach einem Formular und den erforderlichen Unterlagen.",
        "speaking_ar": "اسأل في مكتب المواطنين عن استمارة والوثائق المطلوبة.",
        "culture": "Anforderungen unterscheiden sich nach Anliegen und Ort; maßgeblich ist die Auskunft der zuständigen Stelle.",
        "words": """das Bürgerbüro|eine kommunale Anlaufstelle|مكتب خدمات المواطنين|Ich gehe zum Bürgerbüro.|Bürgerbüro
das Formular|ein Blatt mit Feldern zum Ausfüllen|الاستمارة|Ich brauche ein Formular.|Formular
die Unterlagen|benötigte Dokumente|الوثائق|Meine Unterlagen sind hier.|Unterlagen
der Eingang|hier geht man hinein|المدخل|Der Eingang ist rechts.|Eingang
warten|bleiben, bis etwas geschieht|ينتظر|Bitte warten Sie hier.|warten
ausfüllen|Informationen in Felder schreiben|يملأ|Ich fülle das Formular aus.|fülle
unterschreiben|den eigenen Namen zur Bestätigung schreiben|يوقّع|Ich unterschreibe hier.|unterschreibe
die Kopie|eine zweite gleiche Fassung|النسخة|Ich brauche eine Kopie.|Kopie""",
        "translations": [
            "أذهب إلى مكتب خدمات المواطنين.",
            "أحتاج إلى استمارة.",
            "وثائقي هنا.",
            "المدخل على اليمين.",
            "يرجى الانتظار هنا.",
            "أملأ الاستمارة.",
            "أوقّع هنا.",
            "أحتاج إلى نسخة.",
        ],
    },
    {
        "slug": "nachbarschaft",
        "title": "Gemeinsam etwas planen",
        "goal": "Du lädst jemanden ein und vereinbarst einen Treffpunkt.",
        "a1": [
            "Am Samstag habe ich frei.",
            "Möchtest du mit mir spazieren gehen?",
            "Ja, gern.",
            "Wir treffen uns im Park.",
            "Passt dir drei Uhr?",
            "Ich bringe Wasser mit.",
            "Bis Samstag!",
        ],
        "a2": [
            "Am Samstag möchte Hana ihre Nachbarin treffen.",
            "Sie schlägt einen Spaziergang im Park vor.",
            "Die Nachbarin hat erst am Nachmittag Zeit.",
            "Deshalb treffen sie sich um drei Uhr am Eingang.",
            "Hana bringt Wasser für beide mit.",
            "Wenn es regnet, gehen sie in ein Café.",
            "Sie freuen sich auf den gemeinsamen Nachmittag.",
        ],
        "b1": [
            "Hana möchte ihre Nachbarin besser kennenlernen und schlägt einen gemeinsamen Ausflug vor.",
            "Zuerst überlegen sie, welches Ziel für beide gut erreichbar ist.",
            "Da sie nicht viel Geld ausgeben möchten, entscheiden sie sich für einen Spaziergang.",
            "Sie vereinbaren einen Treffpunkt am Eingang des Parks.",
            "Hana schlägt vor, etwas zu trinken mitzubringen.",
            "Ihre Nachbarin fragt, was sie bei schlechtem Wetter machen sollen.",
            "Gemeinsam einigen sie sich auf ein Café als Alternative.",
            "Falls sich ihre Pläne ändern, wollen sie sich rechtzeitig eine Nachricht schicken.",
            "Hana findet es angenehm, dass beide ihre Wünsche offen nennen können.",
        ],
        "grammar": [
            "Mit wenn formulierst du eine Bedingung: Wenn es regnet, gehen wir ins Café.",
            "نستخدم wenn للشرط، ويأتي الفعل في نهاية جملتها: Wenn es regnet, gehen wir ins Café.",
        ],
        "speaking": "Lade eine Nachbarin zu einem Spaziergang ein und vereinbare Zeit und Treffpunkt.",
        "speaking_ar": "ادعُ جارة إلى نزهة واتفقا على الوقت ومكان اللقاء.",
        "culture": "Einladungen darf man freundlich annehmen oder ablehnen; eine Alternative hilft beim gemeinsamen Planen.",
        "words": """frei haben|an diesem Tag nicht arbeiten|لديه إجازة|Am Samstag habe ich frei.|frei
der Park|eine öffentliche Grünanlage|الحديقة|Wir treffen uns im Park.|Park
treffen|mit jemandem zusammenkommen|يلتقي|Wir treffen uns morgen.|treffen
mitbringen|etwas dabei haben|يحضر معه|Ich bringe Wasser mit.|Wasser
der Treffpunkt|der vereinbarte Ort|مكان اللقاء|Der Treffpunkt ist am Eingang.|Treffpunkt
einladen|jemanden zu etwas bitten|يدعو|Ich lade meine Nachbarin ein.|lade
der Spaziergang|zu Fuß unterwegs sein|النزهة سيرًا|Der Spaziergang beginnt um drei Uhr.|Spaziergang
regnen|Wasser fällt aus Wolken|تمطر|Heute regnet es.|regnet""",
        "translations": [
            "لدي إجازة يوم السبت.",
            "نلتقي في الحديقة.",
            "نلتقي غدًا.",
            "أحضر ماء معي.",
            "مكان اللقاء عند المدخل.",
            "أدعو جارتي.",
            "تبدأ النزهة الساعة الثالثة.",
            "تمطر اليوم.",
        ],
    },
]

A1_GRAMMAR = {
    "termin": (
        "Mit am nennst du den Tag, mit um die Uhrzeit: am Dienstag um zehn Uhr.",
        "نستخدم am مع اليوم وum مع الساعة: am Dienstag um zehn Uhr.",
    ),
    "bus": (
        "Ich fahre mit dem Bus. Das Verb steht an Position zwei.",
        "يأتي الفعل في الموضع الثاني: Ich fahre mit dem Bus.",
    ),
    "nachbarschaft": (
        "Frage mit möchten: Möchtest du mitkommen? Antwort: Ja, gern.",
        "للدعوة نقول: Möchtest du mitkommen? وللموافقة: Ja, gern.",
    ),
}


def build() -> None:
    """Write complete JSON lessons, with no runtime generation dependency."""
    target = Path(__file__).resolve().parent.parent / "data"
    target.mkdir(exist_ok=True)
    for level in ("A1", "A2", "B1"):
        lessons = []
        for number, topic in enumerate(TOPICS, 1):
            vocabulary = []
            for row, arabic in zip(topic["words"].splitlines(), topic["translations"], strict=True):
                term, explanation, meaning, example, answer = row.split("|")
                vocabulary.append(
                    {
                        "term": term,
                        "explanation_de": explanation,
                        "meaning_ar": meaning,
                        "example": example,
                        "answer": answer,
                        "translation_de": example,
                        "translation_ar": arabic,
                    }
                )
            grammar = (
                A1_GRAMMAR.get(topic["slug"], topic["grammar"])
                if level == "A1"
                else topic["grammar"]
            )
            if level == "B1":
                grammar = (
                    "Verbinde Aussagen und Gründe: Ich frage nach, weil ich sicher sein möchte. "
                    "In Nebensätzen mit weil, dass oder obwohl steht das konjugierte Verb am Ende.",
                    "اربط الأفكار والأسباب. في الجمل التابعة مع weil أو dass يأتي الفعل المصرف في النهاية.",
                )
            lessons.append(
                {
                    "id": f"{level.lower()}-{number:02d}-{topic['slug']}",
                    "level": level,
                    "title": topic["title"],
                    "goal": topic["goal"],
                    "dialogue": topic[level.lower()],
                    "vocabulary": vocabulary,
                    "grammar_de": grammar[0],
                    "grammar_ar": grammar[1],
                    "speaking": topic["speaking"],
                    "speaking_ar": topic["speaking_ar"],
                    "culture": topic["culture"],
                }
            )
        (target / f"lessons_{level.lower()}.json").write_text(
            json.dumps(lessons, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    build()
