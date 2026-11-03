"""Teil D: Anfragen an den Campus-Assistenten strukturiert einordnen.

Das Modell soll aus einer Mail drei Dinge herauslesen: das Anliegen,
den Studiengang und eine Frist. Das Ergebnis verarbeitet ein Programm
weiter, es muss also immer die gleiche Form haben.

Aufruf:
    docker compose run --rm app einordnen.py
    docker compose run --rm app einordnen.py "Eure eigene Mail"

Eure Aufgaben stehen bei den TODO-Kommentaren.
"""

import json
import sys
from typing import Literal, cast
from openai.types.shared_params.response_format_json_schema import ResponseFormatJSONSchema

from pydantic import BaseModel, ValidationError

from llm import MODEL, client

SYSTEM_PROMPT = (
    "Du ordnest Mails von Studierenden an die HTWG Konstanz ein. "
    "Antworte ausschließlich mit JSON. "
    "anliegen ist pruefung, mensa, bibliothek oder sonstiges. "
    "studiengang ist das Kürzel (z. B. AIN, WIN, MSI) oder null. "
    "frist ist die Frist aus der Mail, so wie sie dort steht, oder null."
)


class Anfrage(BaseModel):
    anliegen: Literal["pruefung", "mensa", "bibliothek", "sonstiges"]
    studiengang: str | None
    frist: str | None


def schema_von(modell: type[BaseModel]) -> dict:
    """Verpackt das JSON-Schema einer Pydantic-Klasse für response_format."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": modell.__name__.lower(),
            "schema": modell.model_json_schema(),
        },
    }


def einordnen(mail: str, versuche: int = 3) -> Anfrage:
    """Fragt das Modell und gibt eine geprüfte Anfrage zurück."""
    nachricht = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mail},
    ]
    for i in range (versuche):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mail},
            ],
            stream=False,
            temperature=0.0, # Beste Ergebnisse bei Temperature 0.0
            response_format=cast(ResponseFormatJSONSchema, schema_von(Anfrage)),
        )
        content = response.choices[0].message.content
        if content is None:
            raise RuntimeError("Leere Antwort vom LLM.")
        try:
            ergebnis = Anfrage.model_validate_json(content) # ToDo: Ergebnis nie initialisiert, aber wird im print abgerufen.
        except:
            if i == versuche - 1:
                raise RuntimeError("Could not validate Answer.")
            print(f"Error validating response: {ergebnis}") # type: ignore
            continue
        return ergebnis

    raise RuntimeError("Unreachable: Validation Loop already either returned or raised an error. But Pylance wants this ._.")
        


def auswerten() -> None:
    """Ordnet alle Test-Mails ein und vergleicht mit dem Erwarteten."""
    with open("mails.json", encoding="utf-8") as f:
        faelle = json.load(f)
    richtig = 0
    for fall in faelle:
        ergebnis = einordnen(fall["mail"])
        erwartet = fall["erwartet"]
        print(f"Mail: {fall["mail"]}")
        if ergebnis.anliegen == erwartet["anliegen"] and ergebnis.studiengang == erwartet["studiengang"] and ergebnis.frist == erwartet["frist"]:
            richtig += 1
            print(f"Falsches Ergebnis: {ergebnis.anliegen}, {ergebnis.studiengang}, {ergebnis.frist}")
            print(f"Erwartet: {erwartet["anliegen"]}, {erwartet["studiengang"]}, {erwartet["frist"]}")
            print("✓")
        else:
            print(f"Falsches Ergebnis: {ergebnis.anliegen}, {ergebnis.studiengang}, {ergebnis.frist}")
            print(f"Erwartet: {erwartet["anliegen"]}, {erwartet["studiengang"]}, {erwartet["frist"]}")
            print("✗")
    print(f"\n{richtig} von {len(faelle)} Anliegen richtig ({MODEL})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(einordnen(" ".join(sys.argv[1:])).model_dump_json(indent=2))
    else:
        auswerten()
