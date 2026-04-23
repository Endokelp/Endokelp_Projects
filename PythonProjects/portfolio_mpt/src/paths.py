"""Project root and data paths (portable — no hard-coded drive letters)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_DATA = ROOT / "portfolio_data.xlsx"
MULTI_ASSET_DATA = ROOT / "multi_asset_data.xlsx"
