"""Der Campus-Assistent beantwortet eine Frage.

Aufruf:
    docker compose run --rm app assistent.py "Wann hat die Bibliothek offen?"
    docker compose run --rm app assistent.py --prompt prompts/assistent.v2.yaml "..."

In Teil 3 greift ihr diesen Assistenten an und härtet ihn danach.
"""

import argparse

from llm import MODEL, client
from prompts import Prompt, lade
import re

STANDARD_PROMPT = "prompts/assistent.v1.yaml"

# angriff.py und angreifer.py schalten den Guardrail mit --ohne-guardrail ab,
# damit ihr seine Wirkung getrennt vom Prompt messen könnt.
GUARDRAIL_AN = True

CODE = "8352"
ABSAGE = "Es tut mir Leid, aber dazu kann ich leider keine Aussage machen."

ZAHLWÖRTER = {
    "null": "0", "eins": "1", "zwei": "2", "drei": "3", "vier": "4",
    "fünf": "5", "sechs": "6", "sieben": "7", "acht": "8", "neun": "9",
}


def ausgabe_pruefen(text: str) -> str:
    """Guardrail am Ausgang: läuft nach dem Modell, im Code.
    Ersetzt Zahlenwörter mit ziffern, und überprüft dann, ob der Code in den Ziffern enthalten ist.
    """
    normalisiert = text.lower()
    for wort, ziffer in ZAHLWÖRTER.items():
        normalisiert = re.sub(rf"\b{wort}\b", ziffer, normalisiert)

    nur_ziffern = re.sub(r"\D", "", normalisiert)

    if CODE in nur_ziffern:
        return ABSAGE
    return text


def antworten(frage: str, prompt: Prompt) -> str:
    antwort = client.chat.completions.create(
        model=MODEL,
        temperature=prompt.temperature,
        messages=prompt.nachrichten(frage),
        max_tokens=300,
    )
    text = (antwort.choices[0].message.content or "").strip()
    return ausgabe_pruefen(text) if GUARDRAIL_AN else text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("frage", nargs="+")
    parser.add_argument("--prompt", default=STANDARD_PROMPT)
    parser.add_argument("--ohne-guardrail", action="store_true")
    args = parser.parse_args()
    GUARDRAIL_AN = not args.ohne_guardrail
    prompt = lade(args.prompt)

    print(f"[{prompt.kennung} · {MODEL}]\n")
    print(antworten(" ".join(args.frage), prompt))
