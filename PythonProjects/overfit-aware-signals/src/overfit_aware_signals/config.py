from dataclasses import dataclass, field
from typing import Literal


@dataclass
class SignalConfig:
    lookback_months: int = 12
    skip_recent_month: bool = True
    lowvol_window_months: int = 12


@dataclass
class BacktestConfig:
    portfolio_mode: Literal["long_only", "long_short"] = "long_only"
    n_longs: int = 5
    n_shorts: int = 5
    cost_bps: float = 10.0
    rf_annual: float = 0.0
    trading_periods_per_year: int = 12


@dataclass
class CVConfig:
    n_groups: int = 8
    n_test_groups: int = 2
    embargo_pct: float = 0.02


@dataclass
class UniverseConfig:
    # current constituents, not a point-in-time survivorship-bias-free panel
    tickers: list[str] = field(default_factory=lambda: [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ADBE", "CRM",
        "JNJ", "UNH", "PFE", "MRK", "ABBV", "TMO", "LLY",
        "JPM", "BAC", "WFC", "GS", "MS", "BLK",
        "HD", "MCD", "NKE", "SBUX", "TGT",
        "PG", "KO", "PEP", "WMT", "COST",
        "XOM", "CVX", "COP", "SLB",
        "BA", "CAT", "GE", "UPS", "HON",
        "NEE", "DUK", "SO",
        "LIN", "APD",
        "DIS", "CMCSA", "VZ",
        "PLD", "AMT",
    ])
    start: str = "2005-01-01"
    end: str | None = None
