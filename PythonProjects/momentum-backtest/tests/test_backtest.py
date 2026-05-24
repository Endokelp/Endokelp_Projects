import pandas as pd
import pytest

from momentum_backtest import BacktestConfig, run_backtest
from momentum_backtest.signal import compute_momentum_signal


# ---------------------------------------------------------------------------
# Hand-computable toy-panel tests
# ---------------------------------------------------------------------------


def test_portfolio_returns_by_hand(toy_prices_3x6):
    """
    Toy panel: A trends up, B down, C flat.
    lookback=2, skip=1, long_only top-1, zero costs.

    Period 1 rebalance (index 3):
      Signal: A=0.20, B=-0.20, C=0.00  →  hold A
      Return at index 4: 140/130 - 1 = 7/91 ≈ 0.076923

    Period 2 rebalance (index 4):
      Signal: A=130/110-1≈0.1818, B=70/90-1≈-0.2222, C=0  →  hold A
      Return at index 5: 150/140 - 1 = 1/14 ≈ 0.071429
    """
    cfg = BacktestConfig(
        lookback_months=2,
        skip_recent_month=True,
        portfolio_mode="long_only",
        n_longs=1,
        cost_bps=0.0,
    )
    result = run_backtest(toy_prices_3x6, cfg)

    r1 = 140.0 / 130.0 - 1.0
    r2 = 150.0 / 140.0 - 1.0

    assert len(result.returns) == 2
    assert result.returns.iloc[0] == pytest.approx(r1, rel=1e-12)
    assert result.returns.iloc[1] == pytest.approx(r2, rel=1e-12)


def test_equity_curve_consistent_with_returns(toy_prices_3x6):
    """equity_curve[i] == product of (1 + returns[:i+1])."""
    cfg = BacktestConfig(lookback_months=2, skip_recent_month=True,
                         portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, cfg)

    r1 = result.returns.iloc[0]
    r2 = result.returns.iloc[1]
    assert result.equity_curve.iloc[0] == pytest.approx(1.0 + r1, rel=1e-12)
    assert result.equity_curve.iloc[1] == pytest.approx((1.0 + r1) * (1.0 + r2), rel=1e-12)


def test_transaction_cost_reduces_return(toy_prices_3x6):
    """Non-zero cost_bps must lower cumulative return."""
    base = BacktestConfig(lookback_months=2, skip_recent_month=True,
                          portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    costly = BacktestConfig(lookback_months=2, skip_recent_month=True,
                            portfolio_mode="long_only", n_longs=1, cost_bps=200.0)

    r_base = run_backtest(toy_prices_3x6, base).returns.sum()
    r_costly = run_backtest(toy_prices_3x6, costly).returns.sum()
    assert r_costly < r_base


def test_first_rebalance_turnover_equals_half_long_weight(toy_prices_3x6):
    """
    Starting from cash, going to one asset with weight 1.0:
      one_way_turnover = sum(|1-0|) / 2 = 0.5

    The /2 convention treats each unit of weight change as 0.5 buys + 0.5
    sells (dollar-neutral accounting), so gross turnover = 0.5 for a
    fully-invested long-only entry.
    """
    cfg = BacktestConfig(lookback_months=2, skip_recent_month=True,
                         portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, cfg)
    assert result.turnovers.iloc[0] == pytest.approx(0.5, rel=1e-9)


def test_weights_on_toy_panel(toy_prices_3x6):
    """Weights at first rebalance must be {A:1, B:0, C:0}."""
    cfg = BacktestConfig(lookback_months=2, skip_recent_month=True,
                         portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    result = run_backtest(toy_prices_3x6, cfg)

    first_weights = result.weights.iloc[0]
    assert first_weights["A"] == pytest.approx(1.0)
    assert first_weights["B"] == pytest.approx(0.0)
    assert first_weights["C"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Lookahead guardrail
# ---------------------------------------------------------------------------


def test_lookahead_inverts_signal_rankings(reversal_prices):
    """
    Guardrail proof: skip=1 (correct) vs skip=0 (lookahead) produces
    opposite rankings on the reversal panel at t=4.

    Correct  (skip=1): A=+0.15 > B=-0.15  →  A wins
    Lookahead(skip=0): B≈+1.105 > A≈-0.524  →  B wins

    Values verified to machine precision against hand calculations.
    """
    prices = reversal_prices
    lookback = 3

    sig_correct = compute_momentum_signal(prices, lookback=lookback, skip=1)
    sig_lookahead = compute_momentum_signal(prices, lookback=lookback, skip=0)

    t4 = prices.index[4]
    sc = sig_correct.loc[t4]
    sl = sig_lookahead.loc[t4]

    # exact hand-computed values
    assert sc["A"] == pytest.approx(115.0 / 100.0 - 1, rel=1e-12)   # +0.15
    assert sc["B"] == pytest.approx(85.0 / 100.0 - 1, rel=1e-12)    # -0.15
    assert sl["A"] == pytest.approx(50.0 / 105.0 - 1, rel=1e-12)    # ≈ -0.5238
    assert sl["B"] == pytest.approx(200.0 / 95.0 - 1, rel=1e-12)    # ≈ +1.1053

    # correct → A beats B; lookahead → B beats A (inversion)
    assert sc["A"] > sc["B"], "Correct signal: A should beat B"
    assert sl["B"] > sl["A"], "Lookahead signal: B should beat A"


def test_lookahead_changes_backtest_returns(reversal_prices):
    """
    Verify that skip_recent_month=True vs False produces different results.

    With skip=1 (correct), lookback=3:
      first_valid index = 1+3 = 4
      Rebalance at t=4: signal = prices[3]/prices[0]-1 → A wins (+0.15)
      Hold period → t=5: A earns 55/50 - 1 = +10%
      Only 1 return period.

    With skip=0 (lookahead), lookback=3:
      first_valid index = 0+3 = 3  (one more period available)
      Rebalance at t=3: signal = prices[3]/prices[0]-1 → A wins
        (same ranking as correct at t=4, but one period earlier)
      Hold → t=4: A earns 50/115 - 1 ≈ -56.5%  (A crashes!)
      Rebalance at t=4: signal = prices[4]/prices[1]-1 → B wins (+1.105)
      Hold → t=5: B earns 180/200 - 1 = -10%
      Two return periods; both negative.

    The earlier entry caused by drop_skip=0 captures A's crash, hurting
    performance — this is a concrete consequence of lookahead.
    """
    prices = reversal_prices
    cfg_correct = BacktestConfig(lookback_months=3, skip_recent_month=True,
                                 portfolio_mode="long_only", n_longs=1, cost_bps=0.0)
    cfg_lookahead = BacktestConfig(lookback_months=3, skip_recent_month=False,
                                   portfolio_mode="long_only", n_longs=1, cost_bps=0.0)

    r_correct = run_backtest(prices, cfg_correct).returns
    r_lookahead = run_backtest(prices, cfg_lookahead).returns

    assert not r_correct.equals(r_lookahead), "Lookahead should change returns"

    # correct: one period, A earns +10%
    assert len(r_correct) == 1
    assert r_correct.iloc[0] == pytest.approx(55.0 / 50.0 - 1, rel=1e-12)

    # lookahead: two periods; first holds A through its crash
    assert len(r_lookahead) == 2
    assert r_lookahead.iloc[0] == pytest.approx(50.0 / 115.0 - 1, rel=1e-12)  # A crash
    assert r_lookahead.iloc[1] == pytest.approx(180.0 / 200.0 - 1, rel=1e-12)  # B declining


# ---------------------------------------------------------------------------
# Synthetic / integration
# ---------------------------------------------------------------------------


def test_deterministic_with_seed():
    """Two runs with same seed must produce identical price panels."""
    from momentum_backtest import make_synthetic_prices

    p1 = make_synthetic_prices(seed=42)
    p2 = make_synthetic_prices(seed=42)
    assert (p1 == p2).all(axis=None)


def test_long_short_weights_sum_to_zero_in_backtest():
    """Long-short portfolio weights must sum to zero at each rebalance."""
    from momentum_backtest import make_synthetic_prices

    prices = make_synthetic_prices(n_assets=10, n_years=3, seed=7)
    cfg = BacktestConfig(
        portfolio_mode="long_short", n_longs=2, n_shorts=2,
        lookback_months=6, skip_recent_month=True, cost_bps=0.0,
    )
    result = run_backtest(prices, cfg)
    row_sums = result.weights.sum(axis=1)
    assert (row_sums.abs() < 1e-10).all(), f"Max net exposure: {row_sums.abs().max()}"


def test_end_to_end_long_only_runs():
    """Full pipeline on synthetic data without error."""
    from momentum_backtest import make_synthetic_prices
    from momentum_backtest.analytics import compute_metrics

    prices = make_synthetic_prices(n_assets=15, n_years=5, seed=99)
    cfg = BacktestConfig(n_assets=15, n_years=5, seed=99)
    result = run_backtest(prices, cfg)
    m = compute_metrics(result)

    assert -1.0 < m.cagr < 20.0
    assert m.annual_vol > 0
    assert m.max_drawdown <= 0.0
    assert 0.0 <= m.avg_monthly_turnover <= 1.0
