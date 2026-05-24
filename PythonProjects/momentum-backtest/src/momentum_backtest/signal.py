import pandas as pd


def compute_momentum_signal(
    prices: pd.DataFrame,
    lookback: int,
    skip: int,
) -> pd.DataFrame:
    """
    Cross-sectional momentum signal at each date t:

        signal[t] = prices[t - skip] / prices[t - skip - lookback] - 1

    No-lookahead guarantee: the numerator uses prices.shift(skip), which at
    time t contains the price from `skip` periods ago — always available before
    the rebalance decision is made.  skip=0 would use the current period's
    price, which is lookahead if that price is not yet realised.  The backtest
    engine sets skip=1 when skip_recent_month=True.

    NaN propagation: rows where history is insufficient are NaN; the portfolio
    layer excludes assets with NaN signal at a given rebalance date.
    """
    if skip < 0:
        raise ValueError(f"skip must be >= 0, got {skip}")
    if lookback < 1:
        raise ValueError(f"lookback must be >= 1, got {lookback}")

    numerator = prices.shift(skip)
    denominator = prices.shift(skip + lookback)
    return numerator / denominator - 1
