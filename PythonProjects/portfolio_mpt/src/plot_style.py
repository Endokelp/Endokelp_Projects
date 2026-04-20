"""
Matplotlib styling for this project — warm paper, muted ink, hand-picked accents.
Keeps figures from looking like default seaborn/matplotlib demos.
"""
from __future__ import annotations

import matplotlib as mpl
from matplotlib import pyplot as plt

# Palette (picked to sit together; not the stock tab10 cycle)
PAPER = "#f2efe6"
INK = "#1f1f1f"
MUTED = "#5a5855"
GRID = "#c8c4bc"
FRONTIER = "#2d4a3e"
MVP = "#a63d2d"
TANGENCY = "#b8860b"
EW = "#2c5282"
CML = "#5c4a6b"
SCATTER_TICKER = "#6b6560"
ACCENT_LINE = "#4a6670"

MONTE_CMAP = "gist_earth"  # earthy, not viridis


def apply_plot_style() -> None:
    """Call once before plotting."""
    mpl.rcParams.update(
        {
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": INK,
            "axes.titlecolor": INK,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "grid.color": GRID,
            "grid.linestyle": ":",
            "grid.linewidth": 0.9,
            "grid.alpha": 0.85,
            "axes.grid": True,
            "axes.axisbelow": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Segoe UI",
                "DejaVu Sans",
                "Helvetica Neue",
                "Arial",
                "sans-serif",
            ],
            "font.size": 10.5,
            "axes.titlesize": 12.5,
            "axes.titleweight": "600",
            "axes.labelsize": 10.5,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.frameon": True,
            "legend.framealpha": 0.92,
            "legend.edgecolor": GRID,
            "legend.facecolor": "#faf8f3",
            "figure.dpi": 120,
            "savefig.dpi": 160,
            "savefig.facecolor": PAPER,
            "savefig.edgecolor": "none",
            "savefig.bbox": "tight",
        }
    )


def subtitle(ax, text: str) -> None:
    """Small caption under the title — reads like a lab notebook note."""
    ax.text(
        0.0,
        1.02,
        text,
        transform=ax.transAxes,
        fontsize=9,
        color=MUTED,
        style="italic",
        ha="left",
        va="bottom",
    )


def finish_figure(fig) -> None:
    """Tight layout with a little breathing room."""
    fig.tight_layout(pad=1.1)
