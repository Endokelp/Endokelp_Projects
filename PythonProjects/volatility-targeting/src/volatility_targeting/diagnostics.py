from __future__ import annotations

import numpy as np
import pandas as pd


def max_drawdown(returns: pd.Series) -> float:
    r = returns.dropna()
    if r.empty:
        return 0.0
    # prepend 1.0 so the peak-to-trough drawdown starts from full capital
    eq = pd.concat([pd.Series([1.0]), (1 + r).cumprod()], ignore_index=True)
    dd = eq / eq.cummax() - 1
    return float(dd.min())


def turnover_proxy(scale: pd.Series) -> float:
    s = scale.dropna()
    if len(s) < 2:
        return 0.0
    return float(s.diff().abs().mean())


def summary_stats(returns: pd.Series, *, periods_per_year: int = 252) -> dict[str, float]:
    r = returns.dropna()
    mean_ann = float(r.mean() * periods_per_year)
    vol_ann = float(r.std() * np.sqrt(periods_per_year))
    sharpe = mean_ann / vol_ann if vol_ann != 0.0 else 0.0
    dd = max_drawdown(r)
    return {
        "mean_ann": mean_ann,
        "vol_ann": vol_ann,
        "sharpe": sharpe,
        "max_drawdown": dd,
        "skew": float(r.skew()),
        "kurtosis": float(r.kurtosis()),
        "n_obs": float(len(r)),
    }
