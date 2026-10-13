# Abgabe Übungsblatt 1
Gruppe closedAI; Paul Krüssel #310388, Felix Schäfer #313440

## Projektstart
Container bauen: `docker compose up --build app` \
Container starten: `docker compose up -d` \
Modelle laufen lassen: `docker compose run --rm app *Python Datei im Projekt die ausgeführt werden soll* "*Startprompot*"`

## Aufgabe 1
Die compose.yaml defniert die 3 Container, die laufen:
- ollama: Hier laufen die geladenen LLMs. Programme können über die Base URL und den Port 11434 damit kommunizieren und dem Model Prompts schicken.
- modell-laden: Falls der Container neu gebaut wird, lädt dieser Service die Modelle herunter.
- app: "Unser" Container. Hier liegen die Python Scripts, die die LLMs steuern. Die Python Scripts holen sich die wichtigen Infos aus den Umgebungsvariablen, welche vor jeder Ausführung so gesetzt werden, wie sie in der .env definiert wurden. Daher kann man dort das Modell ändern, welches genutzt wird, ohne neu bauen zu müssen.

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
