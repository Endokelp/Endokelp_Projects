from dataclasses import dataclass
from typing import Literal


@dataclass
class BacktestConfig:
    # --- Signal ---
    lookback_months: int = 12
    # Skip the most recent month when computing momentum (standard 12-1 variant).
    # True  -> signal[t] = prices[t-1] / prices[t-1-lookback] - 1
    # False -> signal[t] = prices[t]   / prices[t-lookback]   - 1
    skip_recent_month: bool = True

    # --- Portfolio ---
    portfolio_mode: Literal["long_only", "long_short"] = "long_only"
    n_longs: int = 5
    n_shorts: int = 5  # only used in long_short mode

    # --- Rebalancing ---
    # pandas offset alias for rebalance frequency; "ME" = month-end
    rebalance_freq: str = "ME"

    # --- Transaction costs ---
    # One-way cost applied on portfolio turnover at each rebalance, in basis points.
    cost_bps: float = 10.0

    # --- Performance analytics ---
    rf_annual: float = 0.0          # annual risk-free rate (0 = no RF)
    trading_periods_per_year: int = 12  # monthly data

    # --- Synthetic-data generation ---
    n_assets: int = 20
    n_years: int = 15
    seed: int = 42
    annual_mu: float = 0.08    # mean cross-sectional drift for synthetic assets
    annual_sigma: float = 0.25  # mean cross-sectional vol for synthetic assets
