"""Holt Rohdaten aus dem Transparenzportal Hamburg und legt sie in data/raw/ ab.

Heruntergeladene Dateien werden gecached: ein zweiter Aufruf lädt nicht erneut.
"""

import re
from pathlib import Path

import requests

CKAN_API = "https://suche.transparenz.hamburg.de/api/3/action/package_search"
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"


def _download(url: str, ziel: Path) -> Path:
    """Lädt url nach ziel, falls die Datei noch nicht existiert."""
    if ziel.exists():
        print(f"Bereits vorhanden, überspringe: {ziel.name}")
        return ziel

    ziel.parent.mkdir(parents=True, exist_ok=True)
    print(f"Lade: {ziel.name}")
    antwort = requests.get(url, timeout=120)
    antwort.raise_for_status()
    ziel.write_bytes(antwort.content)
    return ziel


def zuwendungsvorgaenge(jahr: int) -> list[Path]:
    """Lädt alle Quartalsdateien der Zuwendungsvorgänge eines Jahres.

    Die Freie und Hansestadt Hamburg veröffentlicht Zuwendungen quartalsweise
    als XLSX. Diese Funktion fragt den CKAN-Katalog des Transparenzportals ab,
    filtert auf das gewünschte Jahr und lädt die Dateien nach data/raw/.

    Args:
        jahr: Bezugsjahr, z. B. 2024.

    Returns:
        Liste der lokalen Pfade, nach Quartal sortiert.
    """
    antwort = requests.get(
        CKAN_API,
        params={"q": "title:Zuwendungsvorgänge", "rows": 300},
        timeout=120,
    )
    antwort.raise_for_status()

    treffer = []
    for paket in antwort.json()["result"]["results"]:
        gefunden = re.search(r"(\d{4}).*?Quartal\s*(\d)", paket["title"])
        if not gefunden or int(gefunden.group(1)) != jahr:
            continue
        quartal = int(gefunden.group(2))
        dateien = [
            r for r in paket.get("resources", []) if r.get("format", "").upper() == "XLSX"
        ]
        if dateien:
            treffer.append((quartal, dateien[0]["url"]))

    if not treffer:
        raise ValueError(f"Keine Zuwendungsvorgänge für {jahr} im Katalog gefunden.")

    treffer.sort()
    return [
        _download(url, RAW_DIR / f"zuwendungen_{jahr}_Q{quartal}.xlsx")
        for quartal, url in treffer
    ]
