import pytest

from overfit_aware_signals.backtest import run_backtest
from overfit_aware_signals.config import BacktestConfig, SignalConfig
from overfit_aware_signals.data import make_synthetic_prices
from overfit_aware_signals.signals import SIGNAL_REGISTRY, compute_momentum


def test_portfolio_returns_by_hand(toy_prices_3x6):
    # parity vs momentum-backtest: lookback=2, skip=1, long_only top-1, zero costs
    sig_cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    signals = compute_momentum(toy_prices_3x6, sig_cfg)
    bt_cfg = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, signals, bt_cfg)

    r1 = 140.0 / 130.0 - 1.0
    r2 = 150.0 / 140.0 - 1.0

    assert len(result.returns) == 2
    assert result.returns.iloc[0] == pytest.approx(r1, rel=1e-12)
    assert result.returns.iloc[1] == pytest.approx(r2, rel=1e-12)


def test_equity_curve_consistent_with_returns(toy_prices_3x6):
    sig_cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    signals = compute_momentum(toy_prices_3x6, sig_cfg)
    bt_cfg = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, signals, bt_cfg)

    r1 = result.returns.iloc[0]
    r2 = result.returns.iloc[1]
    assert result.equity_curve.iloc[0] == pytest.approx(1.0 + r1, rel=1e-12)
    assert result.equity_curve.iloc[1] == pytest.approx((1.0 + r1) * (1.0 + r2), rel=1e-12)


def test_transaction_cost_reduces_return(toy_prices_3x6):
    sig_cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    signals = compute_momentum(toy_prices_3x6, sig_cfg)
    base = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    costly = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=200.0)

    r_base = run_backtest(toy_prices_3x6, signals, base).returns.sum()
    r_costly = run_backtest(toy_prices_3x6, signals, costly).returns.sum()
    assert r_costly < r_base


def test_first_rebalance_turnover_equals_half_long_weight(toy_prices_3x6):
    sig_cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    signals = compute_momentum(toy_prices_3x6, sig_cfg)
    bt_cfg = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, signals, bt_cfg)
    assert result.turnovers.iloc[0] == pytest.approx(0.5, rel=1e-9)


def test_weights_on_toy_panel(toy_prices_3x6):
    sig_cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    signals = compute_momentum(toy_prices_3x6, sig_cfg)
    bt_cfg = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, signals, bt_cfg)

    first_weights = result.weights.iloc[0]
    assert first_weights["A"] == pytest.approx(1.0)
    assert first_weights["B"] == pytest.approx(0.0)
    assert first_weights["C"] == pytest.approx(0.0)


def test_lookahead_changes_backtest_returns(reversal_prices):
    prices = reversal_prices
    sig_correct = compute_momentum(
        prices, SignalConfig(lookback_months=3, skip_recent_month=True)
    )
    sig_lookahead = compute_momentum(
        prices, SignalConfig(lookback_months=3, skip_recent_month=False)
    )
    bt_cfg = BacktestConfig(portfolio_mode="long_only", n_longs=1, cost_bps=0.0)

    r_correct = run_backtest(prices, sig_correct, bt_cfg).returns
    r_lookahead = run_backtest(prices, sig_lookahead, bt_cfg).returns

    assert not r_correct.equals(r_lookahead)

    assert len(r_correct) == 1
    assert r_correct.iloc[0] == pytest.approx(55.0 / 50.0 - 1, rel=1e-12)

    assert len(r_lookahead) == 2
    assert r_lookahead.iloc[0] == pytest.approx(50.0 / 115.0 - 1, rel=1e-12)
    assert r_lookahead.iloc[1] == pytest.approx(180.0 / 200.0 - 1, rel=1e-12)


def test_long_short_weights_sum_to_zero_in_backtest():
    prices = make_synthetic_prices(n_assets=10, n_years=3, seed=7)
    signals = compute_momentum(
        prices, SignalConfig(lookback_months=6, skip_recent_month=True)
    )
    bt_cfg = BacktestConfig(
        portfolio_mode="long_short", n_longs=2, n_shorts=2, cost_bps=0.0
    )
    result = run_backtest(prices, signals, bt_cfg)
    row_sums = result.weights.sum(axis=1)
    assert (row_sums.abs() < 1e-10).all()


def test_all_registry_signals_run():
    prices = make_synthetic_prices(n_assets=15, n_years=5, seed=99)
    sig_cfg = SignalConfig()
    bt_cfg = BacktestConfig(n_longs=3, cost_bps=0.0)
    for name, fn in SIGNAL_REGISTRY.items():
        signals = fn(prices, sig_cfg)
        result = run_backtest(prices, signals, bt_cfg)
        assert len(result.returns) > 0, name
