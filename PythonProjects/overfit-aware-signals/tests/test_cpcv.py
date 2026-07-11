from itertools import combinations
from math import comb

import numpy as np
import pytest

from overfit_aware_signals.cpcv import (
    CombinatorialPurgedCV,
    combinatorial_test_sharpes,
    path_sharpe_distribution,
)
from overfit_aware_signals.cv import purge_train_indices


def test_cpcv_combination_and_path_counts():
    cv = CombinatorialPurgedCV(n_groups=8, n_test_groups=2, lookback=0)
    assert cv.n_combinations == 28
    assert cv.n_paths == 7  # C(7,1) = φ(8,2)
    assert comb(8, 2) == 28
    assert len(list(cv.split(80))) == 28


def test_cpcv_each_path_matches_purge_helper():
    n, n_groups, k, lookback = 40, 8, 2, 3
    cv = CombinatorialPurgedCV(
        n_groups=n_groups,
        n_test_groups=k,
        lookback=lookback,
        embargo_pct=0.05,
        label_horizon=1,
    )
    fold_sizes = np.full(n_groups, n // n_groups, dtype=int)
    fold_sizes[: n % n_groups] += 1
    bounds = np.cumsum(fold_sizes)
    groups = []
    start = 0
    for end in bounds:
        groups.append(np.arange(start, end))
        start = int(end)

    for (tr, te), combo in zip(cv.split(n), combinations(range(n_groups), k), strict=True):
        expected_test = np.concatenate([groups[g] for g in combo])
        np.testing.assert_array_equal(te, expected_test)
        expected_train = purge_train_indices(
            n, te, lookback, label_horizon=1, embargo_pct=0.05
        )
        np.testing.assert_array_equal(tr, expected_train)


def test_oos_path_sharpes_length_and_fixed_signal_collapse():
    # Fixed returns → every reconstructed path is the full series → identical Sharpes
    rng = np.random.default_rng(0)
    rets = rng.normal(0.01, 0.05, size=96)
    cv = CombinatorialPurgedCV(n_groups=8, n_test_groups=2, lookback=2)
    sharpes = path_sharpe_distribution(rets, cv, periods_per_year=12)
    assert sharpes.shape == (7,)
    assert np.isfinite(sharpes).all()
    assert np.allclose(sharpes, sharpes[0])


def test_combinatorial_test_sharpes_are_fold_count():
    rng = np.random.default_rng(0)
    rets = rng.normal(0.01, 0.05, size=96)
    cv = CombinatorialPurgedCV(n_groups=8, n_test_groups=2, lookback=2)
    block = combinatorial_test_sharpes(rets, cv, periods_per_year=12)
    assert block.shape == (28,)
    assert np.isfinite(block).all()
    # overlapping short folds should disperse (not collapse like paths)
    assert float(np.std(block)) > 0.0


def test_path_group_splits_cover_each_group_once_per_path():
    cv = CombinatorialPurgedCV(n_groups=6, n_test_groups=2, lookback=0)
    paths = cv.path_group_splits()
    assert len(paths) == cv.n_paths == 5
    for path in paths:
        assert all(s is not None for s in path)


def test_invalid_n_test_groups_raises():
    with pytest.raises(ValueError, match="n_test_groups"):
        CombinatorialPurgedCV(n_groups=8, n_test_groups=0, lookback=0)
    with pytest.raises(ValueError, match="n_test_groups"):
        CombinatorialPurgedCV(n_groups=8, n_test_groups=8, lookback=0)
