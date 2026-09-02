#!/usr/bin/env python3
"""Génère les fichiers de lecture de VITRINE depuis donnees.js.

donnees.js reste l'unique source de saisie. Les PDF et vignettes sont seulement
référencés ; ce script ne fabrique ni ne remplace aucune photographie.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "CATALOGUE" / "donnees.js"
OUTPUT_FILE = ROOT / "CATALOGUE" / "catalogue.json"
LEGACY_OUTPUT_FILE = ROOT / "CATALOGUE" / "vitrine.json"
PUBLIC_BASE_URL = "https://88ja88.github.io/JA-Artefacts/"

JS_STRING = r'"(?:\\.|[^"\\])*"'
OBJECT_PATTERN = re.compile(rf"\{{\s*id:\s*(?P<id>{JS_STRING})(?P<body>.*?)\n    \}}", re.DOTALL)


def read_string(body: str, field: str, *, required: bool = True) -> str | None:
    match = re.search(rf"\b{re.escape(field)}:\s*(?P<value>{JS_STRING})", body)
    if not match:
        if required:
            raise ValueError(f"Champ {field} manquant")
        return None
    return json.loads(match.group("value"))


def parse_catalogue() -> list[dict[str, object]]:
    source = DATA_FILE.read_text(encoding="utf-8")
    objects: list[dict[str, object]] = []
    for match in OBJECT_PATTERN.finditer(source):
        object_id = json.loads(match.group("id"))
        body = match.group("body")
        designation = read_string(body, "designation")
        pdf_path = read_string(body, "pdf")
        vignette_path = read_string(body, "vignette", required=False)
        if not re.fullmatch(r"OBJ-\d{4}", object_id):
            raise ValueError(f"Identifiant invalide : {object_id}")
        if not (ROOT / str(pdf_path)).exists():
            raise FileNotFoundError(ROOT / str(pdf_path))
        if vignette_path and not (ROOT / vignette_path).exists():
            raise FileNotFoundError(ROOT / vignette_path)
        objects.append({
            "id": object_id,
            "designation": designation,
            "pdf": urljoin(PUBLIC_BASE_URL, str(pdf_path)),
            "vignette": urljoin(PUBLIC_BASE_URL, vignette_path) if vignette_path else None,
        })
    if not objects:
        raise ValueError("Aucun objet trouvé dans donnees.js")
    ids = [item["id"] for item in objects]
    if len(ids) != len(set(ids)):
        raise ValueError("Identifiant OBJ dupliqué dans donnees.js")
    return objects


def main() -> None:
    objects = parse_catalogue()
    OUTPUT_FILE.write_text(
        json.dumps({"version": 1, "source": "CATALOGUE/donnees.js", "objets": objects}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    legacy_objects = []
    for item in objects:
        object_id = str(item["id"])
        vignette_url = item["vignette"] or urljoin(PUBLIC_BASE_URL, f"CATALOGUE/vignettes/{object_id}.jpg")
        legacy_objects.append({
            "numero": int(object_id.removeprefix("OBJ-")),
            "id": object_id,
            "titre": item["designation"],
            "pdf": item["pdf"],
            "photo": vignette_url,
        })
    LEGACY_OUTPUT_FILE.write_text(
        json.dumps({"version": 1, "objets": legacy_objects}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(objects)} objets publiés depuis donnees.js")


if __name__ == "__main__":
    main()
