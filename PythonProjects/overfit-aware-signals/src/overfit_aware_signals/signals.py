from collections.abc import Callable

import pandas as pd

from .config import SignalConfig


def compute_momentum(prices: pd.DataFrame, cfg: SignalConfig) -> pd.DataFrame:
    if cfg.lookback_months < 1:
        raise ValueError(f"lookback_months must be >= 1, got {cfg.lookback_months}")
    skip = 1 if cfg.skip_recent_month else 0
    return prices.shift(skip) / prices.shift(skip + cfg.lookback_months) - 1


def compute_reversal(prices: pd.DataFrame, cfg: SignalConfig) -> pd.DataFrame:
    # fixed 1-month reversal; recent losers (negative last-month return) score highest
    return -(prices.shift(1) / prices.shift(2) - 1)


def compute_lowvol(prices: pd.DataFrame, cfg: SignalConfig) -> pd.DataFrame:
    rets = prices.pct_change()
    return -rets.rolling(cfg.lowvol_window_months).std()


SIGNAL_REGISTRY: dict[str, Callable] = {
    "momentum": compute_momentum,
    "reversal": compute_reversal,
    "lowvol": compute_lowvol,
}
