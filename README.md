# Hamburg in Zahlen 🚀

> Offene Daten der Stadt Hamburg werden zu einer Serie von Instagram-Kacheln. Jede Kachel zeigt einen Befund, keine Zahl.

## 📊 Projektübersicht

**Problemstellung:**
Hamburg veröffentlicht große Mengen offener Daten — Zuwendungen, Wohnungsbau, Baumkataster, Sozialmonitoring. Sie liegen als CSV, PDF-Tabellen und Geodienste vor und werden kaum gelesen. Rohe Zahlen erklären nichts: „Hamburg vergab X Mio €" ist keine Aussage.

**Ziel:**
Eine Pipeline von der offenen Datenquelle bis zur fertigen Grafik (1080×1080 PNG, einheitliches Layout, als Serie erkennbar). Jede Kachel beantwortet eine Frage mit einem Befund — z. B. „3 % der Empfänger bekommen die Hälfte der Summe" statt einer Gesamtsumme. In vier Sekunden verständlich, die Analysearbeit bleibt sichtbar.

**Methoden:**
Datenbeschaffung über Transparenzportal-CSV, PDF-Tabellenextraktion aus Bürgerschafts-Drucksachen und Geodienste (WFS). Aufbereitung mit pandas, Konzentrationsanalyse (Lorenzkurve, kumulierte Anteile), räumlicher Join und Korrelationsanalyse, Normalisierung pro Kopf bzw. pro Fläche. Visualisierung mit matplotlib über eine gemeinsame Renderfunktion.

### Die vier Kacheln

| # | Thema | Frage | Quelle |
|---|-------|-------|--------|
| 01 | Sozialwohnungen | Hamburg baut — warum schrumpft der Bestand trotzdem? | Bürgerschafts-Drucksachen (PDF) |
| 02 | Zuwendungen | Welcher Anteil der Empfänger bekommt die Hälfte des Geldes? | Transparenzportal Hamburg (CSV) |
| 03 | Straßenbäume | Fällungen vs. Nachpflanzungen je Stadtteil | Straßenbaumkataster (WFS) |
| 04 | Bäume × soziale Lage | Hängt der Baumbestand mit der sozialen Lage zusammen? | Baumkataster × Sozialmonitoring |

<!-- Fertige Kacheln werden hier eingebunden, sobald sie vorliegen. -->

## Setup

Klone das Repository
```bash
git clone https://github.com/Coco1606/hamburg-in-zahlen.git
cd hamburg-in-zahlen
```

Installiere [uv](https://uv.dev) (falls noch nicht installiert) und synchronisiere die Abhängigkeiten
```bash
uv sync
```

### Ausführung

Notebooks in dieser Reihenfolge ausführen:
1. `notebooks/01_exploration.ipynb` — Sichtung aller vier Datensätze
2. `notebooks/02_zuwendungen.ipynb` — Kachel 02: Konzentration der Zuwendungen

Rohdaten liegen in `data/raw/` und sind nicht versioniert; die Notebooks laden sie bei Bedarf neu.

## Methodische Hinweise

- **Normalisieren:** Absolute Werte je Stadtteil bilden sonst nur die Einwohnerzahl ab.
- **Bezugsjahr:** Die Datensätze haben unterschiedliche Stände; das Jahr steht auf jeder Kachel.
- **Zuwendungen:** Durchleitungsstellen prüfen, bevor „X bekommt am meisten" behauptet wird.
- **Kachel 04:** Zusammenhang formulieren, nie Ursache; Drittvariablen (z. B. Bebauungsdichte) benennen.

## Datenquellen

- [Transparenzportal Hamburg](https://transparenz.hamburg.de/)
- [Hamburger Bürgerschaft — Parlamentsdatenbank](https://www.buergerschaft-hh.de/parldok/)
- [Geoportal Hamburg / Geodienste](https://geoportal-hamburg.de/)
