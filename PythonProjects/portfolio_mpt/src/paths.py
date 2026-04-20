"""Project root and data paths (portable — no hard-coded drive letters)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IA_DATA = ROOT / "IA_Portfolio_Data.xlsx"
DISSERTATION_DATA = ROOT / "Dissertation_Full_Data.xlsx"
