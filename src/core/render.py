"""Rendert einen Befund als Instagram-Kachel.

Eine einzige Renderfunktion für alle Kacheln — nur so wird aus vier Bildern
eine Serie. render_tile kennt keine Zuwendungen und keine Bäume, sondern nur
das Befund-Objekt aus analyse.py.

figsize=(10.8, 10.8) bei dpi=100 ergibt exakt 1080×1080 Pixel. Deshalb darf
beim Speichern kein bbox_inches="tight" gesetzt werden — das würde die
Bildgröße verändern und die Serie uneinheitlich machen.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "output"

# Palette, geprüft gegen den dunklen Kachelgrund: Helligkeitsband, Chroma,
# Farbfehlsichtigkeit (ΔE 14,0 bei Protanopie) und Kontrast bestehen alle.
GRUND = "#14181b"
INK = "#f4f6f7"
INK_LEISE = "#a3aeb3"
INK_STILL = "#78848b"
RASTER = "#2b3235"
SERIEN = ["#e4694f", "#1f9cb0"]

SCHRIFT = ["DejaVu Sans", "Arial", "sans-serif"]


def render_tile(befund, dateiname: str) -> Path:
    """Zeichnet einen Befund als 1080×1080-PNG nach output/.

    Args:
        befund: Ein Befund aus core.analyse.
        dateiname: Dateiname innerhalb von output/, z. B. "kachel_02.png".

    Returns:
        Pfad der geschriebenen Datei.
    """
    fig = plt.figure(figsize=(10.8, 10.8), dpi=100, facecolor=GRUND)

    fig.text(
        0.075, 0.965, befund.ueberschrift,
        fontsize=29, fontweight="bold", color=INK, family=SCHRIFT,
        va="top", ha="left", linespacing=1.4,
    )

    fig.text(
        0.075, 0.755, befund.kernzahl,
        fontsize=70, fontweight="bold", color=SERIEN[0], family=SCHRIFT,
        va="center", ha="left",
    )
    fig.text(
        0.37, 0.755, befund.kernzahl_erklaerung,
        fontsize=16, color=INK_LEISE, family=SCHRIFT,
        va="center", ha="left", linespacing=1.6,
    )

    # Quadratisch: eine gestauchte Lorenzkurve lässt sich nicht gegen die
    # Diagonale lesen.
    ax = fig.add_axes([0.135, 0.215, 0.46, 0.46])
    ax.set_facecolor(GRUND)

    # Bezugslinie: völlige Gleichverteilung. Recessive, damit sie die Kurven
    # nicht überstimmt.
    ax.plot([0, 1], [0, 1], color=RASTER, linewidth=2, linestyle=(0, (5, 5)), zorder=1)
    ax.text(
        0.52, 0.55, "Gleichverteilung",
        fontsize=12, color=INK_STILL, family=SCHRIFT,
        rotation=45, rotation_mode="anchor", ha="center", va="bottom",
    )

    for i, reihe in enumerate(befund.reihen):
        farbe = SERIEN[i % len(SERIEN)]
        ax.plot(reihe.x, reihe.y, color=farbe, linewidth=3.4, zorder=3, solid_capstyle="round")
        ax.fill_between(reihe.x, reihe.y, color=farbe, alpha=0.10, zorder=2)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "25", "50", "75", "100 %"])
    ax.set_yticklabels(["0", "25", "50", "75", "100 %"])
    ax.tick_params(colors=INK_STILL, labelsize=13, length=0, pad=6)
    ax.grid(True, color=RASTER, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    for rand in ax.spines.values():
        rand.set_visible(False)

    ax.set_xlabel(befund.x_titel, fontsize=13, color=INK_STILL, family=SCHRIFT, labelpad=10)
    ax.set_ylabel(befund.y_titel, fontsize=13, color=INK_STILL, family=SCHRIFT, labelpad=10)

    # Legende rechts neben dem Plot. Die Farbe trägt die Identität, der Text
    # bleibt in Textfarben.
    griffe = [
        Line2D([], [], color=SERIEN[i % len(SERIEN)], linewidth=3.4,
               label=f"{r.name}\n{r.hinweis}")
        for i, r in enumerate(befund.reihen)
    ]
    legende = fig.legend(
        handles=griffe, loc="upper left", bbox_to_anchor=(0.645, 0.62),
        frameon=False, fontsize=15, labelcolor=INK_LEISE, handlelength=1.4,
        handletextpad=0.9, labelspacing=1.5, borderpad=0,
    )
    for text in legende.get_texts():
        text.set_family(SCHRIFT)
        text.set_linespacing(1.5)

    fig.text(
        0.075, 0.105, f"{befund.quelle} · {befund.jahr}",
        fontsize=14, color=INK_LEISE, family=SCHRIFT, ha="left", va="bottom",
    )
    fig.text(
        0.075, 0.040, befund.fussnote,
        fontsize=11, color=INK_STILL, family=SCHRIFT, ha="left", va="bottom",
    )
    fig.text(
        0.925, 0.105, "Hamburg in Zahlen",
        fontsize=13, fontweight="bold", color=INK_STILL, family=SCHRIFT,
        ha="right", va="bottom",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ziel = OUTPUT_DIR / dateiname
    fig.savefig(ziel, dpi=100, facecolor=GRUND)
    plt.close(fig)
    return ziel
