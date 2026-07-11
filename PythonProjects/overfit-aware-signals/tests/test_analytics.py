import numpy as np
import pandas as pd
import pytest

from overfit_aware_signals.analytics import compute_metrics
from overfit_aware_signals.backtest import BacktestResult, run_backtest
from overfit_aware_signals.config import BacktestConfig, SignalConfig
from overfit_aware_signals.data import make_synthetic_prices
from overfit_aware_signals.signals import compute_momentum


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
    dates = pd.date_range("2020-01-31", periods=25, freq="ME")
    result = _make_result(pd.Series(0.0, index=dates))
    m = compute_metrics(result)

    assert m.cagr == pytest.approx(0.0, abs=1e-10)
    assert m.annual_vol == pytest.approx(0.0, abs=1e-10)
    assert m.sharpe == pytest.approx(0.0, abs=1e-10)
    assert m.max_drawdown == pytest.approx(0.0, abs=1e-10)
    assert m.skew == pytest.approx(0.0, abs=1e-10)
    assert m.kurtosis == pytest.approx(0.0, abs=1e-10)


def test_known_cagr_constant_return():
    dates = pd.date_range("2020-01-31", periods=13, freq="ME")
    result = _make_result(pd.Series(0.01, index=dates))
    m = compute_metrics(result)
    assert m.cagr == pytest.approx(1.01**12 - 1, rel=1e-6)


def test_max_drawdown_known_sequence():
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
    rng = np.random.default_rng(0)
    dates = pd.date_range("2020-01-31", periods=36, freq="ME")
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


def test_skew_kurtosis_known_values():
    dates = pd.date_range("2020-01-31", periods=5, freq="ME")
    rets = pd.Series([0.01, -0.02, 0.03, -0.01, 0.02], index=dates)
    m = compute_metrics(_make_result(rets))
    assert m.skew == pytest.approx(float(rets.skew()), rel=1e-12)
    assert m.kurtosis == pytest.approx(float(rets.kurt()), rel=1e-12)


def test_end_to_end_metrics():
    prices = make_synthetic_prices(n_assets=15, n_years=5, seed=99)
    signals = compute_momentum(prices, SignalConfig())
    result = run_backtest(prices, signals, BacktestConfig(n_longs=3, cost_bps=0.0))
    m = compute_metrics(result)

    assert -1.0 < m.cagr < 20.0
    assert m.annual_vol > 0
    assert m.max_drawdown <= 0.0
    assert 0.0 <= m.avg_monthly_turnover <= 1.0
    assert np.isfinite(m.skew)
    assert np.isfinite(m.kurtosis)
