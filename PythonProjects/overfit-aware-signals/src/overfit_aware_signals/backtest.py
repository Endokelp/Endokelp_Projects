from dataclasses import dataclass

import pandas as pd

from .config import BacktestConfig
from .portfolio import form_weights_long_only, form_weights_long_short


@dataclass
class BacktestResult:
    returns: pd.Series
    weights: pd.DataFrame
    turnovers: pd.Series
    equity_curve: pd.Series
    config: BacktestConfig


def run_backtest(
    prices: pd.DataFrame,
    signals: pd.DataFrame,
    cfg: BacktestConfig,
) -> BacktestResult:
    monthly_returns = prices.pct_change()

    weights_prev = pd.Series(0.0, index=prices.columns)
    portfolio_rets: list[tuple[pd.Timestamp, float]] = []
    weight_records: list[tuple[pd.Timestamp, pd.Series]] = []
    turnover_records: list[tuple[pd.Timestamp, float]] = []

    for i in range(len(prices) - 1):
        sig = signals.iloc[i]
        if sig.dropna().empty:
            continue

        rebal_date = prices.index[i]
        next_date = prices.index[i + 1]

        if cfg.portfolio_mode == "long_only":
            weights_new = form_weights_long_only(sig, cfg.n_longs)
        else:
            weights_new = form_weights_long_short(sig, cfg.n_longs, cfg.n_shorts)

        turnover = float((weights_new - weights_prev).abs().sum() / 2)
        cost = turnover * cfg.cost_bps / 10_000

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
        config=cfg,
    )
