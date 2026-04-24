import numpy as np
import pandas as pd

PERIODS_PER_YEAR = 252


def rolling_vol(
    returns: pd.Series,
    window: int = 20,
    *,
    annualize: bool = True,
    periods_per_year: int = 252,
) -> pd.Series:
    if returns.empty:
        raise ValueError("returns is empty")
    r = returns.rolling(window).std()
    if annualize:
        r = r * np.sqrt(periods_per_year)
    return r.rename("vol_roll")


def ewma_vol(
    returns: pd.Series,
    halflife: float = 20.0,
    *,
    annualize: bool = True,
    periods_per_year: int = 252,
) -> pd.Series:
    if returns.empty:
        raise ValueError("returns is empty")
    # adjust=False: recursive EWMA (no startup-sample correction)
    r = returns.ewm(halflife=halflife, adjust=False).std()
    if annualize:
        r = r * np.sqrt(periods_per_year)
    return r.rename("vol_ewma")
