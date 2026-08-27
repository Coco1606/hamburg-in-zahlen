"""Analysen je Thema. Jede Funktion gibt einen Befund zurück.

Ein Befund ist die einzige Schnittstelle zwischen Analyse und Gestaltung:
render.py kennt keine Zuwendungen, analyse.py kennt kein matplotlib.
"""

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from core.traeger import FREI, OEFFENTLICH, klassifiziere

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"

# Bescheidarten, die keinen ausgezahlten Betrag begründen.
KEINE_ZUWENDUNG = {
    "Ablehnungsbescheid",
    "Aufhebungsbescheid",
    "Aufhebungs- und Rückforderungsbescheid",
}


@dataclass
class Reihe:
    """Eine Datenreihe der Kachel, z. B. eine Lorenzkurve."""

    name: str
    x: np.ndarray
    y: np.ndarray
    hinweis: str = ""


@dataclass
class Befund:
    """Das Ergebnis einer Analyse, fertig zum Rendern."""

    ueberschrift: str
    kernzahl: str
    kernzahl_erklaerung: str
    reihen: list[Reihe]
    quelle: str
    jahr: int
    x_titel: str = ""
    y_titel: str = ""
    fussnote: str = ""
    kennzahlen: dict = field(default_factory=dict)


def lade_zuwendungsvorgaenge(jahr: int) -> pd.DataFrame:
    """Liest die Zuwendungsvorgänge eines Jahres auf Vorgangsebene ein.

    Zwei Eigenheiten der Quelle machen das nötig:

    1. Jede Quartalsdatei ist ein kumulativer Auszug der letzten rund zehn
       Jahre, kein Quartalszuwachs. Es genügt daher die Datei zu Q4.
    2. Die Spalte "Zuwendungssumme" nennt auf jedem Bescheid den aktuellen
       Gesamtbetrag des Vorgangs, nicht eine Veränderung. Ein Vorgang hat bis
       zu 23 Bescheide; die Zeilen zu summieren würde vielfach zählen.

    Deshalb wird auf die INEZ-Nummer gruppiert und je Vorgang der jüngste
    Bescheid behalten. Das Jahr eines Vorgangs ist das seines ersten
    Bescheids — also das Jahr, in dem die Zuwendung bewilligt wurde.

    Args:
        jahr: Bewilligungsjahr, z. B. 2024.

    Returns:
        Ein DataFrame mit einer Zeile je Vorgang, gefiltert auf das Jahr.
    """
    datei = RAW_DIR / f"zuwendungen_{jahr}_Q4.xlsx"
    if not datei.exists():
        raise FileNotFoundError(
            f"{datei} fehlt. Erst core.fetch.zuwendungsvorgaenge({jahr}) aufrufen."
        )

    df = pd.read_excel(datei, sheet_name="Zuwendungsbescheide")

    # Zwei Datensätze nutzen das deutsche Dezimalkomma.
    df["Zuwendungssumme"] = pd.to_numeric(
        df["Zuwendungssumme"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df["Bescheiddatum"] = pd.to_datetime(df["Bescheiddatum"], errors="coerce")
    df = df.sort_values("Bescheiddatum")

    gruppen = df.groupby("INEZ-Nummer")
    vorgaenge = gruppen.tail(1).set_index("INEZ-Nummer")
    vorgaenge["bewilligt"] = gruppen["Bescheiddatum"].min().dt.year

    vorgaenge = vorgaenge[
        (vorgaenge["bewilligt"] == jahr)
        & (~vorgaenge["Bescheidart"].isin(KEINE_ZUWENDUNG))
        & (vorgaenge["Zuwendungssumme"] > 0)
    ]
    return vorgaenge


def de(wert: float, nachkomma: int = 0) -> str:
    """Formatiert eine Zahl deutsch: Punkt als Tausender-, Komma als Dezimaltrenner."""
    return f"{wert:,.{nachkomma}f}".translate(str.maketrans(",.", ".,"))


def _lorenz(betraege: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Kumulierte Anteile: x = Empfänger, y = Geld, jeweils von klein nach groß."""
    sortiert = np.sort(betraege)
    x = np.arange(1, len(sortiert) + 1) / len(sortiert)
    y = sortiert.cumsum() / sortiert.sum()
    return np.insert(x, 0, 0.0), np.insert(y, 0, 0.0)


def _gini(betraege: np.ndarray) -> float:
    x, y = _lorenz(betraege)
    return float(1 - 2 * np.trapezoid(y, x))


def _empfaenger_bis_haelfte(betraege: np.ndarray) -> int:
    """Wie viele der größten Empfänger zusammen die Hälfte der Summe bekommen."""
    absteigend = np.sort(betraege)[::-1]
    kumuliert = absteigend.cumsum() / absteigend.sum()
    return int((kumuliert < 0.5).sum()) + 1


def zuwendungskonzentration(jahr: int = 2024) -> Befund:
    """Kachel 02: Wie ungleich verteilt Hamburg seine Zuwendungen?

    Getrennt nach öffentlichen und freien Trägern, weil die Spitze der
    Rangliste fast vollständig aus städtischen Eigenbetrieben, Staatstheatern
    und Forschungsorganisationen besteht. Ohne die Trennung entstünde der
    Eindruck, wenige Vereine bekämen fast alles.

    Args:
        jahr: Bewilligungsjahr.

    Returns:
        Ein Befund mit je einer Lorenzkurve pro Trägergruppe.
    """
    vorgaenge = lade_zuwendungsvorgaenge(jahr)

    je_empfaenger = (
        vorgaenge.assign(empfaenger=vorgaenge["Zuwendungsempfänger"].str.strip())
        .groupby("empfaenger", as_index=False)["Zuwendungssumme"]
        .sum()
    )
    je_empfaenger["gruppe"] = je_empfaenger["empfaenger"].map(klassifiziere)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    je_empfaenger.sort_values("Zuwendungssumme", ascending=False).to_csv(
        PROCESSED_DIR / f"zuwendungen_{jahr}_je_empfaenger.csv", index=False
    )

    gesamt = je_empfaenger["Zuwendungssumme"].sum()
    reihen, kennzahlen = [], {}

    beschriftung = {
        OEFFENTLICH: "öffentliche Träger",
        FREI: "freie Träger",
    }
    for gruppe in (OEFFENTLICH, FREI):
        teil = je_empfaenger.loc[je_empfaenger["gruppe"] == gruppe, "Zuwendungssumme"]
        betraege = teil.to_numpy()
        x, y = _lorenz(betraege)
        anzahl_haelfte = _empfaenger_bis_haelfte(betraege)

        kennzahlen[gruppe] = {
            "empfaenger": len(betraege),
            "summe": float(betraege.sum()),
            "anteil_an_gesamt": float(betraege.sum() / gesamt),
            "gini": _gini(betraege),
            "empfaenger_bis_haelfte": anzahl_haelfte,
        }
        reihen.append(
            Reihe(
                name=beschriftung[gruppe],
                x=x,
                y=y,
                hinweis=f"{de(len(betraege))} Empfänger\n{de(betraege.sum() / 1e6)} Mio €",
            )
        )

    oeff, frei = kennzahlen[OEFFENTLICH], kennzahlen[FREI]
    kennzahlen["gesamt"] = {
        "summe": float(gesamt),
        "empfaenger": int(len(je_empfaenger)),
        "vorgaenge": int(len(vorgaenge)),
    }

    return Befund(
        ueberschrift=(
            "Hamburgs Zuwendungen sind extrem\n"
            "ungleich verteilt — aber die Spitze\n"
            "gehört der Stadt selbst."
        ),
        kernzahl=f"{oeff['anteil_an_gesamt'] * 100:.0f} %",
        kernzahl_erklaerung=(
            f"der {de(gesamt / 1e9, 2)} Mrd € gehen an nur\n"
            f"{oeff['empfaenger']} von {de(len(je_empfaenger))} Empfängern:\n"
            f"Eigenbetriebe, Theater, Museen, Forschung."
        ),
        reihen=reihen,
        quelle="Transparenzportal Hamburg, Zuwendungsvorgänge",
        jahr=jahr,
        x_titel="Empfänger, kumuliert (klein → groß)",
        y_titel="Zuwendungen, kumuliert",
        fussnote=(
            f"Bewilligungsjahr {jahr} · {de(len(vorgaenge))} Vorgänge · "
            f"je Vorgang der jüngste Bescheid\n"
            f"Gini: öffentlich {de(oeff['gini'], 2)} · frei {de(frei['gini'], 2)}"
        ),
        kennzahlen=kennzahlen,
    )
