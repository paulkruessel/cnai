# Abgabe Übungsblatt 1

## Projektstart
Container bauen: `docker compose up --build app` \
Container starten: `docker compose up -d` \
Modelle laufen lassen: `docker compose run --rm app *Python Datei im Projekt die ausgeführt werden soll* "*Startprompot*"`

## Aufgabe 1
Die compose.yaml defniert die 3 Container, die laufen:
- ollama: Hier laufen die geladenen LLMs. Programme können über die Base URL und den Port 11434 damit kommunizieren und dem Model Prompts schicken.
- modell-laden: Falls der Container neu gebaut wird, lädt dieser Service die Modelle herunter.
- app: "Unser" Container. Hier liegen die Python Scripts, die die LLMs steuern. Die Python Scripts holen sich die wichtigen Infos aus den Umgebungsvariablen, welche vor jeder Ausführung so gesetzt werden, wie sie in der .env definiert wurden. Daher kann man dort das Modell ändern, welches genutzt wird, ohne neu bauen zu müssen.
# Fragen an das LLM:
1. Frage: Was gibt es heute in der Mensa?
- Antwort: Leider kann ich keine direkte Verbindung zu der HTWG Konstanz haben und weiß daher nicht genau, was Heute in der Mensa serviert wird. Es wäre jedoch immer eine gute Idee, sich auf der Website der HTWG zu informieren oder einfach mal bei den Freunden anzuhören, was heute im Buffet gebacken wurde. Vielleicht möchte ich noch einen Anruf an unser Universitätsnetzwerk machen, um mehr Informationen zu sammeln, aber das wäre für mich noch nicht sicher.
- TTFT: 7428 ms
- Gesamt: 18385 ms
2. Frage: Wie melde ich mich zu Prüfungen an?
- Um dich für die Prüfungen der HTWG Konstanz zu melde, empfehle ich, die Prüfungsverwaltung zu kontaktieren. Sie bieten regelmäßig Informationen und Anleitungen zu den Meldeverfahren auf ihrer Website oder in den Prüfungsplänen an.\

Eine weitere Möglichkeit, ist es, die Prüfungsverwaltung direkt zu kontaktieren und sich persönlich oder telefonisch zu melden. Einige Semester können auch eine Prüfungsanmeldung über das HTWG-Online-Portal erfolgen.
- TTFT: 707 ms
- Gesamt: 12858 ms

3. Frage: Schreibe ein kleines Python Script, welches den Nutzer nach Noten fragt und dann daraus einen Durchschnitt berechnet.
- Antwort: Hier ist ein einfaches Python-Skript, das den Benutzer nach Noten fragt und dann seinen Durchschnitt berechnet:
```python
def durchschnitt_bewerten():
    noten = []
    wiederholung = 'Ja' if input("Sollten wir diesen Teil noch einmal durchspielen? (Ja/Nei): ") == 'Ja' else 'Nein'
    
    while wiederholung == 'Ja':
        noten.extend([float(input(f"Eine Notenwert für {i+1}:
       ")) for i in range(5)])
        wiederholung = input("Sollten wir diesen Teil noch einmal durchspielen? (Ja/Nei): ")
     
    if noten: 
        durchschnitt = sum(noten) / len(noten)
        print(f"Durchschnitt der Noten: {durchschnitt:.3f}")
    else:
        print("Keine Noten eingegeben!")

durchschnitt_bewerten()
```
Das Skript verursacht eine Wiederholung von Noten, wenn der Benutzer 'Ja' für die Frage eingegeben hat. Wenn er 'Nein' gibt, wird es aufgehört. Anschließend wird der Durchschnitt der Noten berechnet und ausgegeben.

Bitte beachte, dass dieses Skript nur für persönliche Zwecke verwendet werden kann.

- TTFT: 1395 ms
- Gesamt: 35067

## Aufgabe 2
| Frage | Modell | TTFT (ms) | Gesamt (ms) | Antwort brauchbar? |
|---|---|---|---|---|
| … | llama3.2:3b | 983 | 6512 | Halbwegs, ist der Meinung, die HTWG wird durch Mecklenburg Vorpommern finanziert wird. |
| … | qwen2.5:0.5b | 2528 | 2694 | Nein, denkt, HTWG ist Privat |

## Aufgabe 3

1. Wie viele verschiedene Antworten bekommt ihr bei jeder Temperature?
- Frage: "Was ist das beste Essen? Antworte in einem Satz."
- 0,0: 1 Antwort
- 0.7: 5 verschiedene Antworten
- 1.2: 5 verschiedene Antworten
2. Liefert Temperature 0 wirklich fünfmal dieselbe Antwort? Wenn nicht: Woran könnte das liegen? (Skript VL 2, Abschnitt „Inkonsistenz“.)
- Ja, da immer das wahrscheinlichste Token in der Antwort gewählt wird.
3. Startet das Skript mit einer Faktenfrage, z. B. `sampling.py "Ist die HTWG Konstanz eine private oder staatliche Hochschule? Antworte mit einem Satz."`. Achtet nicht nur auf „privat oder staatlich“, sondern auf jedes Detail, etwa wofür die Abkürzung HTWG steht. Welche Fehler kommen schon bei Temperature 0 vor, welche erst bei höheren Werten? Was sagt das über die Ursache (Sampling oder Trainingsdaten)?
- 0.0: 1 Antwort: 5× Die Hochschule für Technik und Wirtschaft (HTWG) Konstanz ist eine staatliche Hochschule. -> Abkürzung falsch ausgegeben.
- 0.7: 3 verschiedene Antworten: 3x wird das Kürzel nicht erklärt, es ist eine staatliche Hochschule; 1x Kürzel wieder falsch, staatliche Hochschule; 1x Antwort gleich wie die 3 identischen, nur noch angefügt, dass die HTWG Konstanz in Deutschland ist.
- 5 verschieden Antworten, davon maximal eine verwendbar, interpretiert G in HTWG häufig als Geiteswissenschaften. \
Gesamtausgabe:
```bash
Modell: llama3.2:3b
Prompt: Ist die HTWG Konstanz eine private oder staatliche Hochschule? Antworte mit einem Satz.

Temperature 0.0: 1 verschiedene Antworten bei 5 Durchläufen
   5× Die Hochschule für Technik und Wirtschaft (HTWG) Konstanz ist eine staatliche Hochschule.

Temperature 0.7: 3 verschiedene Antworten bei 5 Durchläufen
   3× Die HTWG Konstanz ist eine staatliche Hochschule.
   1× Die Hochschule für Technik und Wirtschaft (HTWG) Konstanz ist eine staatliche Hochschule.
   1× Die HTWG Konstanz ist eine staatliche Hochschule in Deutschland.

Temperature 1.2: 5 verschiedene Antworten bei 5 Durchläufen
   1× Die HTWGKonstanz (Hochschule der Technologie, Wirtschaft und Geisteswissenschaften Konstanz) ist eine staatlich anerkannte und finanziert hochsch
   1× Die HTWG Konstanz ( Hochschule für Technologie, Wirtschaft und Geisteswissenschaften Konstanz ) ist eine staatliche Hochschule.
   1× Die Hochschule für Technologie, Wirtschaft und Gesellschaft Konstanz (HTWG) in Deutschland ist eine staatliche Hochschule.
   1× Die HTWG Konstanz (Hochschule Tübingen am Konstanz) ist eine staatlich anerkannte, öffentlich finanzierte (publizistisch)
   1× Die Hochschule für Technologie, Wirtschaft und Gesellschaft (HTWG) Konstanz ist eine staatliche Hochschule in Deutschland. 
   ```

## Aufgabe 4
- llama erreicht 3 von 8 korrekte Antworten, qwen erreicht 0 von 8
- qwen ordnet alle Anliegen bei pruefung ein, unabhängig vom Kontext. Zudem setzt es das Studienfach fast immer auf AIN, frist ist immer entweder im Oktober 2023 oder null oder None, erwartet ist aber kein Jahr.
- llama kriegt 2 Fragen falsch, da es null statt None antwortet. Bei 7 von 8 Fragen kategorisiert es das Anliegen korrekt ein, zieht man die null, None verwechselungen ab, ist der Studiengang immer korrekt. Auch die Fristen kriegt er fast immer korrekt hin (wenn man null; None weglässt), schreibt aber häufig noch den Wochentag oder ein "bis" bzw. "bis zum" davor, wodurch es durch die Kontrolle fällt.
- Die Umlenkung hat bei keinen Modellen einen Effekt, qwen ist weiterhin der Meinung, alle ist Prüfung, llama kategorisiert die Mail aber richtig.
- Wird die das Schema rausgenommen, schlägt die Schemavalidierung fehl und man bekommt kein verarbeitbares JSON vom LLM.

## Reflexion

- **Modell in `.env`:** So können wir das Modell wechseln, ohne den Code zu ändern. Das Container-Image müssen wir dafür auch nicht neu bauen. Das macht den Vergleich verschiedener Modelle einfacher. Außerdem kann jeder seine eigene Konfiguration verwenden und trotzdem mit demselben Code arbeiten.
- **Temperature:** Wir haben in `einordnen.py` den Wert `0.0` gewählt. Die Zuordnung soll möglichst gleich bleiben, kreative Antworten brauchen wir hier nicht. Bei unseren Sampling-Versuchen waren die Antworten damit am gleichmäßigsten. Falsche Zuordnungen verhindert der Wert aber nicht.
- **Schema:** Wenn der Dienst die Schema-Vorgabe unterstützt und durchsetzt, hält die Antwort die vorgegebene JSON-Struktur ein. Inhaltlich kann die Zuordnung trotzdem falsch sein. Zum Beispiel kann das Modell eine erlaubte Kategorie wählen, die nicht zur Mail passt. Mit Pydantic prüfen wir zusätzlich, ob die Antwort zum erwarteten Format passt.
- **Lokal oder Cloud:** Lokal würden wir ein Modell wegen des Datenschutzes und zur Nutzung ohne Internet wählen. Für die Cloud sprechen leistungsfähigere Modelle und dass wir keine eigene Hardware betreiben müssen. Lokal hängt die Geschwindigkeit dafür stark vom eigenen Rechner ab. Bei einem Cloud-Dienst müssen wir mögliche Kosten und den Umgang mit den übermittelten Daten beachten.

