"""Ein Agent ohne Framework: Modell + Werkzeuge + Schleife.

Aufruf:
    docker compose run --rm app agent.py "Was gibt es heute in der Mensa?"
    docker compose run --rm app agent.py --ohne-mcp "Wo kann ich nachts lernen?"
    docker compose run --rm app agent.py --prompt prompts/agent.v2.yaml "..."

Der Ablauf ist der Thought-Action-Observation-Zyklus:
  1. Das Modell bekommt die Aufgabe und die Liste der Werkzeuge.
  2. Es antwortet entweder mit Text (fertig) oder mit Werkzeugaufrufen.
  3. Unser Code führt die Aufrufe aus und hängt die Ergebnisse als
     Nachrichten mit der Rolle "tool" an den Verlauf an.
  4. Weiter mit Schritt 2, bis das Modell antwortet oder MAX_SCHRITTE erreicht ist.
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field

from llm import MODEL, client
from prompts import Prompt, lade
from werkzeuge import LOKALE_WERKZEUGE, Werkzeug

STANDARD_PROMPT = "prompts/agent.v1.yaml"
MAX_SCHRITTE = 6  # Modellaufrufe pro Aufgabe, danach Abbruch


@dataclass
class Schritt:
    """Ein Werkzeugaufruf und was dabei herauskam."""

    werkzeug: str
    argumente: dict | str
    ergebnis: str
    fehler: str | None = None  # None, "unbekannt", "argumente", "wert" oder "abgelehnt"


@dataclass
class Ergebnis:
    antwort: str
    schritte: list[Schritt] = field(default_factory=list)
    modellaufrufe: int = 0
    eingabe_tokens: int = 0
    ausgabe_tokens: int = 0
    sekunden: float = 0.0
    abgebrochen: bool = False


def fragen(werkzeug: Werkzeug, argumente: dict) -> bool:
    """Fragt im Terminal nach, bevor ein schreibendes Werkzeug läuft."""
    if not sys.stdin.isatty():
        return False  # niemand da, der bestätigen kann: lieber nicht
    text = ", ".join(f"{k}={v!r}" for k, v in argumente.items())
    return input(f"  ? Soll ich {werkzeug.name}({text}) ausführen? [j/N] ").strip().lower() == "j"


def werkzeug_ausfuehren(aufruf, verzeichnis: dict[str, Werkzeug], bestaetigen=fragen) -> Schritt:
    """Führt einen Werkzeugaufruf des Modells aus und fängt alle Fehler ab.

    Fehler werden nicht geworfen, sondern als Text zurückgegeben. Das Modell
    liest ihn im nächsten Schritt und kann sich korrigieren.
    """
    name = aufruf.function.name
    if name not in verzeichnis:
        return Schritt(name, aufruf.function.arguments,
                       f"Fehler: Werkzeug {name} gibt es nicht. Verfügbar: {', '.join(verzeichnis)}",
                       "unbekannt")
    try:
        argumente = json.loads(aufruf.function.arguments or "{}")
        if not isinstance(argumente, dict):
            raise ValueError("keine Schlüssel-Wert-Paare")
    except ValueError as e:
        return Schritt(name, aufruf.function.arguments, f"Fehler: Argumente sind kein gültiges JSON ({e}).",
                       "argumente")

    werkzeug = verzeichnis[name]

    if werkzeug.schreibend and not bestaetigen(werkzeug, argumente):
        return Schritt(name, argumente,
                       f"ABGELEHNT: Der Nutzer hat {name} nicht bestätigt. Das Werkzeug wurde daher"
                       f"NICHT ausgeführt, es wurde also auch nichts verändert. Versuche es NICHT erneut, sondern"
                       f"sage der Person, dass die Aktion abgebrochen wurde.",
                       "abgelehnt")

    try:
        ergebnis = str(werkzeug.funktion(**argumente))
    except TypeError as e:  # fehlende oder unbekannte Parameter
        return Schritt(name, argumente, f"Fehler: falsche Parameter für {name}: {e}", "argumente")
    except Exception as e:  # noqa: BLE001  Werkzeug ist abgestürzt
        return Schritt(name, argumente, f"Fehler im Werkzeug {name}: {e}", "wert")
    return Schritt(name, argumente, ergebnis, "wert" if ergebnis.startswith("Fehler") else None)


def agent(
    aufgabe: str,
    werkzeuge: list[Werkzeug],
    prompt: Prompt,
    max_schritte: int = MAX_SCHRITTE,
    bestaetigen=fragen,
    zeigen: bool = False,
) -> Ergebnis:
    verzeichnis = {w.name: w for w in werkzeuge}
    tools = [w.als_tool() for w in werkzeuge]
    nachrichten = prompt.nachrichten(aufgabe)
    ergebnis = Ergebnis(antwort="")
    start = time.perf_counter()

    for i in range(max_schritte):
        # 1. Modell aufrufen
        antwort = client.chat.completions.create(model=MODEL, messages=nachrichten, tools=tools, temperature=prompt.temperature, max_tokens=500)
        ergebnis.modellaufrufe += 1
        # if to satisfy pylance type check
        if antwort.usage:
            ergebnis.eingabe_tokens += antwort.usage.prompt_tokens
            ergebnis.ausgabe_tokens += antwort.usage.completion_tokens

        # 2. Check for Tool Calls

        nachricht = antwort.choices[0].message

        if not nachricht.tool_calls:
            ergebnis.antwort = nachricht.content if nachricht.content is not None else ""
            ergebnis.abgebrochen = False
            ergebnis.sekunden = time.perf_counter() - start
            return ergebnis

        nachrichten.append(nachricht.model_dump(exclude_none=True))
        for call in nachricht.tool_calls:
            schritt = werkzeug_ausfuehren(call, verzeichnis, bestaetigen)
            ergebnis.schritte.append(schritt)
            if zeigen:
                zeige_schritt(schritt)
            nachrichten.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": schritt.ergebnis,
            })

    ergebnis.antwort = f"Abgebrochen nach {max_schritte} Modellaufrufen ohne Antwort."
    ergebnis.abgebrochen = True
    ergebnis.sekunden = time.perf_counter() - start
    return ergebnis


def zeige_schritt(schritt: Schritt) -> None:
    args = schritt.argumente if isinstance(schritt.argumente, str) else \
        ", ".join(f"{k}={v!r}" for k, v in schritt.argumente.items())
    marke = f"  [{schritt.fehler}]" if schritt.fehler else ""
    kurz = schritt.ergebnis.replace("\n", " ")
    print(f"  → {schritt.werkzeug}({args}){marke}")
    print(f"  ← {kurz[:160]}{'…' if len(kurz) > 160 else ''}")


def alle_werkzeuge(mit_mcp: bool = True) -> list[Werkzeug]:
    werkzeuge = list(LOKALE_WERKZEUGE)
    if mit_mcp:
        from mcp_werkzeuge import mcp_werkzeuge
        werkzeuge += mcp_werkzeuge()
    return werkzeuge


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Campus-Agent mit Werkzeugen")
    parser.add_argument("aufgabe", nargs="?", default="Was gibt es heute in der Mensa?")
    parser.add_argument("--prompt", default=STANDARD_PROMPT)
    parser.add_argument("--ohne-mcp", action="store_true", help="nur die lokalen Werkzeuge")
    parser.add_argument("--max-schritte", type=int, default=MAX_SCHRITTE)
    args = parser.parse_args()

    werkzeuge = alle_werkzeuge(not args.ohne_mcp)
    print(f"Werkzeuge: {', '.join(w.name for w in werkzeuge)}\n")
    e = agent(args.aufgabe, werkzeuge, lade(args.prompt), args.max_schritte, zeigen=True)
    print(f"\n{e.antwort}\n")
    print(f"  {len(e.schritte)} Werkzeugaufrufe · {e.modellaufrufe} Modellaufrufe · "
          f"{e.eingabe_tokens} Eingabe-Tokens · {e.sekunden:.1f} s · {MODEL}")
