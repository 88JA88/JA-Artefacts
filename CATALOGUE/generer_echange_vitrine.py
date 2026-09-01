#!/usr/bin/env python3
"""Publie les titres et photos principales du catalogue pour VITRINE.

À exécuter après chaque ajout ou modification dans donnees.js. La plus grande
image de la première page de chaque PDF devient la vignette de référence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "CATALOGUE" / "donnees.js"
OUTPUT_FILE = ROOT / "CATALOGUE" / "vitrine.json"
THUMBNAIL_DIR = ROOT / "CATALOGUE" / "vignettes"

JS_STRING = r'"(?:\\.|[^"\\])*"'
OBJECT_PATTERN = re.compile(
    rf"\{{\s*id:\s*(?P<id>{JS_STRING}).*?"
    rf"designation:\s*(?P<title>{JS_STRING}).*?"
    rf"pdf:\s*(?P<pdf>{JS_STRING})\s*\}}",
    re.DOTALL,
)


def parse_catalogue() -> list[dict[str, object]]:
    source = DATA_FILE.read_text(encoding="utf-8")
    objects: list[dict[str, object]] = []
    for match in OBJECT_PATTERN.finditer(source):
        object_id = json.loads(match.group("id"))
        title = json.loads(match.group("title"))
        pdf_path = json.loads(match.group("pdf"))
        number_match = re.search(r"(\d+)$", object_id)
        if not number_match:
            raise ValueError(f"Numéro introuvable dans {object_id}")
        objects.append({
            "numero": int(number_match.group(1)),
            "id": object_id,
            "titre": title,
            "pdf": pdf_path,
            "photo": f"CATALOGUE/vignettes/{object_id}.jpg",
        })
    if not objects:
        raise ValueError("Aucun objet trouvé dans donnees.js")
    return objects


def extract_main_photo(pdf_path: Path, destination: Path) -> None:
    page = PdfReader(pdf_path).pages[0]
    candidates = [item.image for item in page.images]
    if not candidates:
        raise ValueError(f"Aucune image trouvée dans {pdf_path.name}")
    photo = max(candidates, key=lambda image: image.width * image.height)
    photo = photo.convert("RGB")
    photo.thumbnail((700, 700), Image.Resampling.LANCZOS)
    destination.parent.mkdir(parents=True, exist_ok=True)
    photo.save(destination, "JPEG", quality=86, optimize=True)


def main() -> None:
    objects = parse_catalogue()
    THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
    for item in objects:
        pdf_path = ROOT / str(item["pdf"])
        if not pdf_path.exists():
            raise FileNotFoundError(pdf_path)
        extract_main_photo(pdf_path, THUMBNAIL_DIR / f'{item["id"]}.jpg')
    OUTPUT_FILE.write_text(
        json.dumps({"version": 1, "objets": objects}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{len(objects)} objets publiés pour VITRINE")


if __name__ == "__main__":
    main()
