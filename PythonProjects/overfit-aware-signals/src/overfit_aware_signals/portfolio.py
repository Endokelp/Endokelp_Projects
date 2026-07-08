import pandas as pd


def form_weights_long_only(signal: pd.Series, n_longs: int) -> pd.Series:
    clean = signal.dropna()
    n = min(n_longs, len(clean))
    w = pd.Series(0.0, index=signal.index)
    if n == 0:
        return w
    top = clean.nlargest(n).index
    w[top] = 1.0 / n
    return w


def form_weights_long_short(signal: pd.Series, n_longs: int, n_shorts: int) -> pd.Series:
    clean = signal.dropna()
    half = len(clean) // 2
    n_l = min(n_longs, half)
    n_s = min(n_shorts, half)
    w = pd.Series(0.0, index=signal.index)
    if n_l == 0 and n_s == 0:
        return w
    top = clean.nlargest(n_l).index
    bottom = clean.nsmallest(n_s).index
    if n_l:
        w[top] = 1.0 / n_l
    if n_s:
        w[bottom] = -1.0 / n_s
    return w
