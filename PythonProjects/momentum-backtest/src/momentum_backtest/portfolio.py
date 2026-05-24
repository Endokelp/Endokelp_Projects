import pandas as pd


def form_weights_long_only(
    signal: pd.Series,
    n_longs: int,
) -> pd.Series:
    """
    Equal-weight the top-n assets by signal value.

    Assets with NaN signal are excluded from ranking.  If fewer than n_longs
    non-NaN assets exist, all non-NaN assets are held equally.
    Weights sum to 1.0 (or 0.0 if signal is all NaN).
    """
    clean = signal.dropna()
    n = min(n_longs, len(clean))
    weights = pd.Series(0.0, index=signal.index)
    if n == 0:
        return weights
    top = clean.nlargest(n).index
    weights[top] = 1.0 / n
    return weights


def form_weights_long_short(
    signal: pd.Series,
    n_longs: int,
    n_shorts: int,
) -> pd.Series:
    """
    Equal-weight long top-n, equal-weight short bottom-n.

    Weights sum to 0.  Each leg sums to +1 (long) / -1 (short), giving
    gross exposure of 2.0.  Assets with NaN signal are excluded.
    If too few assets exist, each leg shrinks to half of available.
    """
    clean = signal.dropna()
    half = len(clean) // 2
    n_l = min(n_longs, half)
    n_s = min(n_shorts, half)

    weights = pd.Series(0.0, index=signal.index)
    if n_l == 0 and n_s == 0:
        return weights

    top = clean.nlargest(n_l).index
    bottom = clean.nsmallest(n_s).index
    if n_l:
        weights[top] = 1.0 / n_l
    if n_s:
        weights[bottom] = -1.0 / n_s
    return weights
