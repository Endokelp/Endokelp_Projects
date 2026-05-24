import pandas as pd
import pytest

from momentum_backtest import BacktestConfig
from momentum_backtest.analytics import PerformanceMetrics, compute_metrics
from momentum_backtest.backtest import BacktestResult


def _make_result(rets: pd.Series, cfg: BacktestConfig | None = None) -> BacktestResult:
    equity = (1 + rets).cumprod()
    turnovers = pd.Series(0.0, index=rets.index)
    return BacktestResult(
        returns=rets,
        weights=pd.DataFrame(),
        turnovers=turnovers,
        equity_curve=equity,
        config=cfg or BacktestConfig(),
    )


def test_flat_zero_returns():
    """All-zero returns: CAGR=0, vol=0, Sharpe=0, maxDD=0."""
    dates = pd.date_range("2020-01-31", periods=25, freq="ME")
    result = _make_result(pd.Series(0.0, index=dates))
    m = compute_metrics(result)

    assert m.cagr == pytest.approx(0.0, abs=1e-10)
    assert m.annual_vol == pytest.approx(0.0, abs=1e-10)
    assert m.sharpe == pytest.approx(0.0, abs=1e-10)
    assert m.max_drawdown == pytest.approx(0.0, abs=1e-10)


def test_known_cagr_constant_return():
    """Constant monthly return of 1%: CAGR = 1.01^12 - 1."""
    dates = pd.date_range("2020-01-31", periods=13, freq="ME")
    result = _make_result(pd.Series(0.01, index=dates))
    m = compute_metrics(result)
    assert m.cagr == pytest.approx(1.01**12 - 1, rel=1e-6)


def test_max_drawdown_known_sequence():
    """
    Returns: [+10%, -20%, +5%]
    Equity:  [1.10, 0.88, 0.924]
    Peak before trough: 1.10
    Drawdown: (0.88 - 1.10) / 1.10 = -0.20
    """
    dates = pd.date_range("2020-01-31", periods=3, freq="ME")
    rets = pd.Series([0.10, -0.20, 0.05], index=dates)
    result = _make_result(rets)
    m = compute_metrics(result)
    expected_dd = (0.88 - 1.10) / 1.10
    assert m.max_drawdown == pytest.approx(expected_dd, rel=1e-9)


def test_n_months_matches_returns():
    dates = pd.date_range("2020-01-31", periods=24, freq="ME")
    result = _make_result(pd.Series(0.005, index=dates))
    m = compute_metrics(result)
    assert m.n_months == 24


def test_rf_reduces_sharpe():
    """Higher risk-free rate lowers Sharpe for a positive-return series with non-zero vol."""
    import numpy as np

    rng = np.random.default_rng(0)
    dates = pd.date_range("2020-01-31", periods=36, freq="ME")
    # positive-drift series with non-zero variance so Sharpe is well-defined
    rets = pd.Series(0.01 + rng.normal(0, 0.02, 36), index=dates)

    cfg_rf0 = BacktestConfig(rf_annual=0.00)
    cfg_rf5 = BacktestConfig(rf_annual=0.05)
    m0 = compute_metrics(_make_result(rets, cfg_rf0))
    m5 = compute_metrics(_make_result(rets, cfg_rf5))
    assert m5.sharpe < m0.sharpe


def test_too_few_returns_raises():
    dates = pd.date_range("2020-01-31", periods=1, freq="ME")
    result = _make_result(pd.Series([0.01], index=dates))
    with pytest.raises(ValueError, match="at least 2"):
        compute_metrics(result)
