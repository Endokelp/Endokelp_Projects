from dataclasses import dataclass

import numpy as np

from .backtest import BacktestResult


@dataclass
class PerformanceMetrics:
    cagr: float
    annual_vol: float
    sharpe: float
    max_drawdown: float
    avg_monthly_turnover: float
    skew: float
    kurtosis: float
    n_months: int
    rf_annual: float


def compute_metrics(result: BacktestResult) -> PerformanceMetrics:
    rets = result.returns
    ppy = result.config.trading_periods_per_year
    rf = result.config.rf_annual

    if len(rets) < 2:
        raise ValueError("Need at least 2 return observations to compute metrics.")

    n = len(rets)
    n_years = n / ppy
    final_equity = float(result.equity_curve.iloc[-1])
    cagr = final_equity ** (1.0 / n_years) - 1.0

    monthly_rf = rf / ppy
    excess = rets - monthly_rf
    std_monthly = float(rets.std())
    ann_vol = std_monthly * np.sqrt(ppy)

    if std_monthly > 0:
        sharpe = float(excess.mean() / std_monthly * np.sqrt(ppy))
    else:
        sharpe = 0.0

    equity = result.equity_curve
    running_max = equity.cummax()
    drawdowns = (equity - running_max) / running_max
    max_dd = float(drawdowns.min())

    avg_turnover = float(result.turnovers.mean()) if len(result.turnovers) else 0.0

    return PerformanceMetrics(
        cagr=cagr,
        annual_vol=ann_vol,
        sharpe=sharpe,
        max_drawdown=max_dd,
        avg_monthly_turnover=avg_turnover,
        skew=float(rets.skew()),
        kurtosis=float(rets.kurt()),
        n_months=n,
        rf_annual=rf,
    )
