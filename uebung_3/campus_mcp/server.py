"""Campus-Werkzeuge als MCP-Server.

Dieser Server läuft als eigener Container und bietet seine Werkzeuge über
das Model Context Protocol (MCP) an. Jeder MCP-Client kann sie nutzen:
unser Agent, aber genauso Claude Desktop, Cursor oder der MCP Inspector.

Transport: Streamable HTTP unter http://<host>:8000/mcp

Die Daten sind ausgedacht und liegen in belegung.json und speiseplan.json.
Buchungen landen nur im Arbeitsspeicher und sind nach einem Neustart weg.
"""

import json
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

HIER = Path(__file__).parent
BELEGUNG = json.loads((HIER / "belegung.json").read_text(encoding="utf-8"))
SPEISEPLAN = json.loads((HIER / "speiseplan.json").read_text(encoding="utf-8"))

# Zeitfenster, in denen Seminarräume belegt oder gebucht werden können
SLOTS = ["08:00", "09:45", "11:30", "14:00", "15:45", "17:30"]
WOCHENTAGE = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]

# Buchungen von Studierenden: {(raum, datum, slot): name}
buchungen: dict[tuple[str, str, str], str] = {}

mcp = FastMCP("campus", host="0.0.0.0", port=8000)


def _wochentag(datum: str) -> str:
    return WOCHENTAGE[date.fromisoformat(datum).weekday()]


def _belegt(raum: str, datum: str) -> dict[str, str]:
    """Alle belegten Slots eines Raums an einem Datum, mit Grund."""
    plan = BELEGUNG["raeume"].get(raum, {})
    belegt = dict(plan.get(_wochentag(datum), {}))
    for (r, d, slot), name in buchungen.items():
        if r == raum and d == datum:
            belegt[slot] = f"gebucht von {name}"
    return belegt


@mcp.tool()
def raeume_auflisten() -> str:
    """Listet alle Seminarräume, die Studierende zum Lernen buchen können,
    mit Gebäude und Zahl der Plätze."""
    zeilen = [f"{r}: {info['plaetze']} Plätze, {info['ausstattung']}"
              for r, info in BELEGUNG["raeume"].items()]
    return "\n".join(zeilen)


@mcp.tool()
def raum_frei(raum: str, datum: str) -> str:
    """Zeigt, in welchen Zeitfenstern ein Seminarraum an einem Tag frei ist.

    raum: Raumnummer wie O-108 (Gebäude, Bindestrich, Nummer)
    datum: Datum im Format JJJJ-MM-TT, zum Beispiel 2026-11-05
    """
    raum = raum.strip().upper()
    if raum not in BELEGUNG["raeume"]:
        return f"Fehler: Raum {raum} gibt es nicht oder er ist nicht buchbar. Nutze raeume_auflisten."
    try:
        tag = _wochentag(datum)
    except ValueError:
        return f"Fehler: '{datum}' ist kein Datum im Format JJJJ-MM-TT."
    if tag in ("samstag", "sonntag"):
        return f"{raum} ist am {tag} geschlossen."
    belegt = _belegt(raum, datum)
    frei = [s for s in SLOTS if s not in belegt]
    return (f"{raum} am {datum} ({tag}): frei um {', '.join(frei) or 'keinem Slot'}. "
            f"Belegt: {', '.join(f'{s} ({g})' for s, g in sorted(belegt.items())) or 'nichts'}.")

@mcp.tool()
def raum_buchen(raum: str, datum: str, uhrzeit: str, name: str):
    """Bucht einen angegebenen Raum an einem freien Tag zu einer freien Uhrzeit.
    
    raum: Raumnummer wie O-108 (Gebäude, Bindestrich, Nummer)
    datum: Datum im Format JJJJ-MM-TT, zum Beispiel 2026-11-05
    uhrzeit: Eine gültige Uhrzeit, zu welchem Zeitpunkt der Raum gebucht wird im Format hh:mm. Zum Beispiel: 09:45
    name: Der Name auf den gebucht werden soll, zum Beispiel 'CNAI Vorlesung'
    """

    raum = raum.strip().upper()
    if raum not in BELEGUNG["raeume"]:
        return f"Fehler: Raum {raum} gibt es nicht oder er ist nicht buchbar. Nutze raeume_auflisten."
    try:
        tag = _wochentag(datum)
    except ValueError:
        return f"Fehler: '{datum}' ist kein Datum im Format JJJJ-MM-TT."
    if tag in ("samstag", "sonntag"):
        return f"{raum} ist am {tag} geschlossen."

    uhrzeit = uhrzeit.strip()
    if len(uhrzeit) == 4 and uhrzeit[1] == ":":
        uhrzeit = "0" + uhrzeit
    if uhrzeit not in SLOTS:
        return f"Fehler: '{uhrzeit}' ist kein gültiges Zeitfenster. Gültig sind: {', '.join(SLOTS)}"

    name = name.strip()

    if not name:
        return f"Fehler: Bitte einen Namen angeben, auf den gebucht wird."

    belegt = _belegt(raum, datum)
    if uhrzeit in belegt:
        frei = [s for s in SLOTS if s not in belegt]
        return f"Fehler: {raum} ist am {datum} ({tag}) um {uhrzeit} belegt. Frei sind noch: {', '.join(frei) or 'keine'}."
    buchungen[(raum, datum, uhrzeit)] = name
    return f"Gebucht: {raum} am {datum} ({tag}) um {uhrzeit} für {name}."


@mcp.tool()
def mensa_speiseplan(datum: str) -> str:
    """Speiseplan der Mensa (Gebäude M) für einen Tag, mit Preisen für Studierende.

    datum: Datum im Format JJJJ-MM-TT, zum Beispiel 2026-11-05
    """
    try:
        tag = _wochentag(datum)
    except ValueError:
        return f"Fehler: '{datum}' ist kein Datum im Format JJJJ-MM-TT."
    gerichte = SPEISEPLAN.get(tag)
    if not gerichte:
        return f"Am {tag} ({datum}) hat die Mensa geschlossen."
    return f"Mensa am {tag}, {datum}:\n" + "\n".join(f"- {g}" for g in gerichte)


@mcp.custom_route("/zuruecksetzen", methods=["POST"])
async def zuruecksetzen(request: Request) -> PlainTextResponse:
    """Kein Werkzeug, nur für messen.py: alle Buchungen löschen,
    damit jede Messung mit derselben Raumbelegung startet."""
    buchungen.clear()
    return PlainTextResponse("ok")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
