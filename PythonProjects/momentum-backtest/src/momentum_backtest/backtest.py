from dataclasses import dataclass

import pandas as pd

from .config import BacktestConfig
from .portfolio import form_weights_long_only, form_weights_long_short
from .signal import compute_momentum_signal


@dataclass
class BacktestResult:
    returns: pd.Series       # portfolio return for each holding period, indexed by period-end date
    weights: pd.DataFrame    # portfolio weights at each rebalance date (rows = rebal dates)
    turnovers: pd.Series     # one-way turnover at each rebalance date
    equity_curve: pd.Series  # cumulative wealth starting at 1.0, indexed by period-end date
    config: BacktestConfig


def run_backtest(prices: pd.DataFrame, config: BacktestConfig) -> BacktestResult:
    """
    Monthly momentum backtest with strict no-lookahead enforcement.

    Timeline convention
    -------------------
    All prices are assumed to be month-end close prices.  At each rebalance
    date (month-end t) we:
      1. Compute the momentum signal using prices available up to t.
         With skip_recent_month=True, the signal window is
         [t - 1 - lookback, t - 1], i.e. the most recent month is skipped.
      2. Form the target portfolio (weights).
      3. Compute one-way turnover vs the prior portfolio.
      4. Deduct proportional transaction costs on that turnover.
      5. The portfolio is then held until the next month-end (t+1), when
         we collect the return prices[t+1]/prices[t] - 1 for each asset.

    Missing-data rule
    -----------------
    Assets with NaN signal at a given rebalance date are excluded from
    ranking and held at zero weight.  This can happen at the start of the
    backtest (insufficient history) or when a CSV asset has gaps that
    survive forward-filling.

    Transaction cost
    ----------------
    cost = (one_way_turnover) * cost_bps / 10_000
    one_way_turnover = sum(|new_weight - old_weight|) / 2

    The first rebalance has turnover equal to the total long weight (we go
    from cash to invested).
    """
    skip = 1 if config.skip_recent_month else 0
    lookback = config.lookback_months

    signals = compute_momentum_signal(prices, lookback=lookback, skip=skip)
    monthly_returns = prices.pct_change()

    first_valid = skip + lookback  # first index with a complete signal window

    weights_prev = pd.Series(0.0, index=prices.columns)
    portfolio_rets: list[tuple[pd.Timestamp, float]] = []
    weight_records: list[tuple[pd.Timestamp, pd.Series]] = []
    turnover_records: list[tuple[pd.Timestamp, float]] = []

    for i in range(first_valid, len(prices) - 1):
        rebal_date = prices.index[i]
        next_date = prices.index[i + 1]

        sig = signals.iloc[i]

        if config.portfolio_mode == "long_only":
            weights_new = form_weights_long_only(sig, config.n_longs)
        else:
            weights_new = form_weights_long_short(sig, config.n_longs, config.n_shorts)

        turnover = float((weights_new - weights_prev).abs().sum() / 2)
        cost = turnover * config.cost_bps / 10_000

        rets = monthly_returns.iloc[i + 1]
        port_ret = float((weights_new * rets).sum()) - cost

        portfolio_rets.append((next_date, port_ret))
        weight_records.append((rebal_date, weights_new.copy()))
        turnover_records.append((rebal_date, turnover))

        weights_prev = weights_new.copy()

    returns = pd.Series(dict(portfolio_rets), name="portfolio_return", dtype=float)
    weights_df = pd.DataFrame({d: w for d, w in weight_records}).T
    weights_df.index.name = "rebal_date"
    turnovers = pd.Series(dict(turnover_records), name="turnover", dtype=float)

    equity_curve = (1 + returns).cumprod()
    equity_curve.name = "equity_curve"

    return BacktestResult(
        returns=returns,
        weights=weights_df,
        turnovers=turnovers,
        equity_curve=equity_curve,
        config=config,
    )
