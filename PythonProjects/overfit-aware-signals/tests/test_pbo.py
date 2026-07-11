import numpy as np
import pytest

from overfit_aware_signals.pbo import (
    cscv_logits,
    probability_of_backtest_overfitting,
)


def test_pbo_zero_when_ranking_stable():
    # Best strategy is best in every block → IS-winner always top OOS → PBO = 0
    t = 40
    rets = np.column_stack(
        [
            np.full(t, 0.05),
            np.full(t, 0.02),
            np.full(t, 0.00),
            np.full(t, -0.01),
        ]
    )
    pbo = probability_of_backtest_overfitting(rets, n_groups=4)
    assert pbo == pytest.approx(0.0, abs=1e-12)


def test_pbo_one_when_is_winner_flips_oos():
    # Each strategy is strong in exactly one block; train-best is test-worst
    t, s, n = 40, 4, 4
    block = t // s
    rets = np.full((t, n), -1.0)
    for j in range(n):
        b = j % s
        rets[b * block : (b + 1) * block, j] = 1.0
    pbo = probability_of_backtest_overfitting(rets, n_groups=s)
    assert pbo == pytest.approx(1.0, abs=1e-12)


def test_relative_rank_uses_n_plus_one():
    # N=3, clear ranking → ω = {1,2,3}/4
    from overfit_aware_signals.pbo import _relative_rank

    scores = np.array([0.3, 0.1, 0.2])
    assert _relative_rank(scores, 0) == pytest.approx(3 / 4)
    assert _relative_rank(scores, 1) == pytest.approx(1 / 4)
    assert _relative_rank(scores, 2) == pytest.approx(2 / 4)


def test_pbo_excludes_median_rank_logit_zero():
    # IS winner always OOS median (rank 2 of 3) → λ = 0 → not counted (λ < 0 only)
    t = 40
    # col0 best IS always; OOS: col0 middle, col1 best, col2 worst in every block
    # Construct so mean ranks flip: use constant means with clear order per half
    rets = np.column_stack(
        [
            np.full(t, 0.02),  # always middle overall if halves identical
            np.full(t, 0.05),
            np.full(t, 0.00),
        ]
    )
    # With constant columns, IS winner is col1, OOS winner is col1 → PBO = 0
    assert probability_of_backtest_overfitting(rets, n_groups=4) == pytest.approx(0.0)


def test_logits_positive_when_stable():
    t = 40
    rets = np.column_stack([np.full(t, 0.05), np.full(t, 0.0)])
    logits = cscv_logits(rets, n_groups=4)
    assert len(logits) == 6  # C(4, 2)
    assert np.all(logits > 0.0)


def test_logits_nonpositive_when_flipped():
    t, s, n = 40, 4, 4
    block = t // s
    rets = np.full((t, n), -1.0)
    for j in range(n):
        b = j % s
        rets[b * block : (b + 1) * block, j] = 1.0
    logits = cscv_logits(rets, n_groups=s)
    assert np.all(logits < 0.0)


def test_rejects_odd_n_groups():
    rets = np.zeros((20, 3))
    with pytest.raises(ValueError, match="even"):
        probability_of_backtest_overfitting(rets, n_groups=3)


def test_rejects_too_few_strategies():
    rets = np.zeros((20, 1))
    with pytest.raises(ValueError, match="strateg"):
        probability_of_backtest_overfitting(rets, n_groups=4)


def test_rejects_short_sample():
    rets = np.zeros((3, 3))
    with pytest.raises(ValueError, match="n_groups"):
        probability_of_backtest_overfitting(rets, n_groups=4)


def test_cscv_ranks_by_sharpe_not_mean():
    # Mean ranks A > B; Sharpe ranks B > A. CSCV must pick B as IS winner.
    from overfit_aware_signals.pbo import _sharpe_perf

    t = 40
    a = np.array([0.20, -0.10] * (t // 2), dtype=float)  # high mean, high vol
    b = np.array([0.021, 0.019] * (t // 2), dtype=float)  # lower mean, low vol
    rets = np.column_stack([a, b])
    idx = np.arange(t)
    sharpe = _sharpe_perf(rets, idx)
    mean = rets.mean(axis=0)
    assert mean[0] > mean[1]
    assert sharpe[1] > sharpe[0]
    # Stable Sharpe ranking → PBO = 0 (B wins IS and OOS)
    assert probability_of_backtest_overfitting(rets, n_groups=4) == pytest.approx(0.0)
