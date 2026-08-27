"""Ordnet Zuwendungsempfänger in öffentlich/staatsnah oder freie Träger ein.

Warum das nötig ist: Die Zuwendungen der Stadt Hamburg sind stark konzentriert,
aber an der Spitze stehen keine Vereine, sondern städtische Eigenbetriebe,
Staatstheater, Landesmuseen und Forschungsorganisationen. Ohne diese Trennung
liest sich der Befund falsch.

Methode: Die 100 größten Empfänger des Jahres 2024 (82 % der Summe) sind
einzeln geprüft und unten namentlich eingetragen. Der lange Rest wird über
Rechtsform- und Namensregeln eingeordnet; wo keine Regel greift, gilt "frei".
Das ist die konservative Annahme — die tausenden Kleinempfänger sind ganz
überwiegend Vereine, und im Zweifel wird die öffentliche Seite eher zu klein
als zu groß geschätzt.
"""

import re

OEFFENTLICH = "öffentlich"
FREI = "frei"

# Namensfragmente der handgeprüften Top-100. Teilstring-Vergleich, damit
# Schreibvarianten und Zusätze nicht zu Fehlzuordnungen führen.
_OEFFENTLICH_NAMEN = [
    # Gesundheit und Wissenschaft
    "Universitätsklinikum Hamburg-Eppendorf",
    "Deutsches Elektronen-Synchrotron",
    "Deutsche Forschungsgemeinschaft",
    "Bernhard-Nocht-Institut",
    "Institut für Friedensforschung",
    "Hamburg Innovation",
    # Verkehr, Hafen, Infrastruktur, Wohnen
    "Hamburg Port Authority",
    "Hamburger Hochbahn",
    "Hochbahn-Wache",
    "HVV Hamburger Verkehrsverbund",
    "P + R-Betriebsgesellschaft",
    "NMS New Mobility Solutions",
    "SAGA Siedlungs-Aktiengesellschaft",
    "Bäderland Hamburg",
    # Kultur in städtischer Trägerschaft
    "Historische Museen Hamburg",
    "Stiftung Hamburger Öffentliche Bücherhallen",
    "Neue Schauspielhaus",
    "Hamburgische Staatsoper",
    "Thalia Theater",
    "Hamburger Kunsthalle",
    "Elbphilharmonie und Laeiszhalle",
    "Museum für Kunst und Gewerbe",
    "Kampnagel",
    "Deichtorhallen",
    "Museum am Rothenbaum",
    "HamburgMusik",
    "Archäologisches Museum Hamburg",
    "Stiftung Hamburger Gedenkstätten",
    "CCH Immobilien",
    # Wirtschaftsförderung und Marketing der Stadt
    "Hamburg Tourismus",
    "Hamburg Marketing",
    "HIW Hamburg Invest",
    "Hamburg Kreativ",
    "hamburger arbeit GmbH",
    "ZEBAU",
    # Sonstige Anstalten und Kammern
    "Studierendenwerk Hamburg",
    "Handwerkskammer Hamburg",
]

# Rechtsform- und Institutionsregeln für den langen Rest der Verteilung.
_OEFFENTLICH_REGELN = [
    r"AöR|A\.ö\.R|Anstalt des öffentlichen Rechts",
    r"Stiftung öffentlichen Rechts|Stiftung des öffentlichen Rechts",
    r"Körperschaft des öffentlichen Rechts",
    r"^Behörde für|^Bezirksamt|^Landesbetrieb|^Freie und Hansestadt Hamburg",
    r"Max-Planck|Fraunhofer|Helmholtz|Leibniz-Institut|Leibniz-Zentrum",
    r"Universität Hamburg|Technische Universität|Hochschule für",
]

_REGELN = [re.compile(muster, re.IGNORECASE) for muster in _OEFFENTLICH_REGELN]


def klassifiziere(name: str) -> str:
    """Ordnet einen Empfängernamen einer der beiden Gruppen zu.

    Args:
        name: Empfängername aus der Spalte "Zuwendungsempfänger".

    Returns:
        "öffentlich" für städtische Eigenbetriebe, Anstalten, Staatstheater,
        Landesmuseen und staatliche Forschungsorganisationen, sonst "frei".
    """
    if not isinstance(name, str):
        return FREI

    sauber = name.strip().strip('"')

    for fragment in _OEFFENTLICH_NAMEN:
        if fragment.casefold() in sauber.casefold():
            return OEFFENTLICH

    for regel in _REGELN:
        if regel.search(sauber):
            return OEFFENTLICH

    return FREI
