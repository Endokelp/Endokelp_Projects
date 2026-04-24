import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import Series


def load_returns(path: str | Path, *, date_col: str = "date", ret_col: str = "ret") -> Series:
    df = pd.read_csv(path, parse_dates=[date_col])
    df = df.set_index(date_col)[ret_col].sort_index()

    n_nan = df.isna().sum()
    if n_nan:
        warnings.warn(f"Dropping {n_nan} row(s) with NaN returns", stacklevel=2)
        df = df.dropna()

    # drop dupes keeping last because yahoo sometimes double-prints the last row
    df = df[~df.index.duplicated(keep="last")]
    df.name = "ret"
    return df


def synthetic_returns(
    n_days: int = 2520,
    mu: float = 0.07,
    sigma: float = 0.18,
    *,
    seed: int = 42,
    periods_per_year: int = 252,
) -> Series:
    rng = np.random.default_rng(seed)
    mu_d = mu / periods_per_year
    s_d = sigma / np.sqrt(periods_per_year)
    r = rng.normal(mu_d, s_d, size=n_days)
    idx = pd.bdate_range(start="2015-01-02", periods=n_days)
    # TODO: handle timezone-aware input properly
    return Series(r, index=idx, name="ret")
