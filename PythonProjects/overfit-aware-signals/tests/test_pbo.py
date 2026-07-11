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
    assert np.all(logits <= 0.0)


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
