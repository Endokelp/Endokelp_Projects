from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest import BacktestResult


@dataclass
class PerformanceMetrics:
    cagr: float
    annual_vol: float
    sharpe: float           # uses rf_annual from config; 0.0 when vol=0
    max_drawdown: float     # negative number (e.g. -0.25 = -25% peak-to-trough)
    avg_monthly_turnover: float
    n_months: int
    rf_annual: float        # informational — what rf was used


def compute_metrics(result: BacktestResult) -> PerformanceMetrics:
    """
    Standard performance metrics from a BacktestResult.

    CAGR
        final_equity ^ (periods_per_year / n_periods) - 1
        Assumes equity starts at 1.0 (guaranteed by run_backtest).

    Annualised volatility
        std(monthly_returns) * sqrt(periods_per_year)

    Sharpe ratio
        mean(monthly_excess_returns) * sqrt(periods_per_year)
        ─────────────────────────────────────────────────────
                std(monthly_returns) * sqrt(periods_per_year)

        Simplifies to: mean_excess / std * sqrt(periods_per_year).
        Risk-free rate applied as rf_annual / periods_per_year per period.
        Returns 0.0 when vol is zero (constant returns, no risk).

    Max drawdown
        min( (equity - running_max) / running_max )
        Always <= 0.

    Avg monthly turnover
        mean of one-way turnovers recorded at each rebalance.
    """
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
        n_months=n,
        rf_annual=rf,
    )


def print_metrics(metrics: PerformanceMetrics) -> None:
    print(f"  CAGR:                {metrics.cagr:>8.2%}")
    print(f"  Annual Vol:          {metrics.annual_vol:>8.2%}")
    print(f"  Sharpe Ratio:        {metrics.sharpe:>8.2f}  (rf={metrics.rf_annual:.2%})")
    print(f"  Max Drawdown:        {metrics.max_drawdown:>8.2%}")
    print(f"  Avg Monthly Turnover:{metrics.avg_monthly_turnover:>8.2%}")
    print(f"  Months:              {metrics.n_months:>8d}")


def save_equity_curve(result: BacktestResult, path: str | Path) -> None:
    """Write equity curve + monthly returns to CSV."""
    df = pd.DataFrame(
        {
            "equity_curve": result.equity_curve,
            "monthly_return": result.returns,
        }
    )
    df.to_csv(path)
