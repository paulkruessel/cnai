# Abgabe Übungsblatt 1

## Projektstart
Container bauen: `docker compose up --build app` \
Container starten: `docker compose up -d` \
Modelle laufen lassen: `docker compose run --rm app *Python Datei im Projekt die ausgeführt werden soll* "*Startprompot*"`

## Teil 1:
### 1.1
`nachrichten()` liest die Prompts aus app/prompts/ ein. Wenn das passiert, wird aus dem Prompt ein Objekt. Dieses wird dann dem LLM als JSON gegeben. Da JSON viele geschweifte Klammern hat, kann das dazu führen, dass `format()` diese als Platzhalter interpretieren könnte, was zu einem Fehler führen würde.

### 1.2
Das Problem an einem Überschreiben ist, dass jede kleinste Veränderung im Prompt sich massiv auf den Output des LLMs auswirken kann. Wenn wir spezifische Prompts zur Messung oder zum Vergleich von Modellen verwenden wollen, ist es wichtig, zu Versionieren, um vorherige Messungen nicht zu verfälschen.  Z.B.: Ich messe die Time to first Token (TTFT) mit einem Prompt. Eine spätere Messung erfordert, dass ich den Prompt leicht abändere. Wenn ich nun überschreibe anstatt zu versionieren, ist nicht mehr nachvollziehbar, auf was sich die erste Messung bezieht. Ist zudem die Performance eines neuen Prompts schlechter als die vorherige Version, kann man mit simpler Versionierung leicht wieder zurückgehen, was nur durch eine Git Historie beim Überschreiben möglich wäre (wobei das dann ja technisch gesehen wieder eine Form von Versionierung ist).

### 1.3
Command: `docker compose run --rm app einordnen.py`
- Anliegen richtig:   13 von 16
- Alle Felder richtig: 8 von 16