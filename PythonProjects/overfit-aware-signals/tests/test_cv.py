import numpy as np
import pytest

from overfit_aware_signals.cv import PurgedKFold, purge_train_indices


def test_basic_folds_cover_all_and_disjoint():
    n, n_splits = 20, 4
    cv = PurgedKFold(n_splits=n_splits, lookback=0, embargo_pct=0.0, label_horizon=0)
    folds = list(cv.split(n))
    assert len(folds) == n_splits

    all_test = np.concatenate([te for _, te in folds])
    assert sorted(all_test.tolist()) == list(range(n))
    for tr, te in folds:
        assert len(np.intersect1d(tr, te)) == 0


def test_lookback_purge_removes_leak_label_only_misses():
    # n=12, one test index at 10, lookback=3, label_horizon=1
    # label-only (lookback=0): train@8 has [8,9] vs test@10 [10,11] — no overlap
    # lookback=3: train@8 has [5,9] vs test@10 [7,11] — overlaps, must purge
    n = 12
    test = np.array([10])

    label_only = purge_train_indices(
        n, test, lookback=0, label_horizon=1, embargo_pct=0.0
    )
    with_lookback = purge_train_indices(
        n, test, lookback=3, label_horizon=1, embargo_pct=0.0
    )

    assert 8 in label_only
    assert 8 not in with_lookback
    assert 7 not in with_lookback
    assert 5 in with_lookback


def test_embargo_drops_post_test_train():
    n = 100
    test = np.arange(40, 50)
    no_embargo = purge_train_indices(
        n, test, lookback=0, label_horizon=0, embargo_pct=0.0
    )
    with_embargo = purge_train_indices(
        n, test, lookback=0, label_horizon=0, embargo_pct=0.05
    )
    # 5% of 100 = 5 samples immediately after test end (50..54)
    assert 50 in no_embargo
    assert 54 in no_embargo
    assert 50 not in with_embargo
    assert 54 not in with_embargo
    assert 55 in with_embargo


def test_purged_kfold_applies_lookback_on_each_fold():
    n, lookback = 24, 4
    cv = PurgedKFold(n_splits=4, lookback=lookback, embargo_pct=0.0, label_horizon=1)
    for tr, te in cv.split(n):
        te_start = int(te.min())
        # indices inside the lookback window of the first test sample must be gone
        leaked = [i for i in range(max(0, te_start - lookback), te_start) if i in tr]
        assert leaked == [], f"leaked train indices {leaked} for test starting {te_start}"


def test_noncontiguous_test_keeps_middle_train():
    # CPCV can pick non-adjacent groups; min/max span must not nuke the gap
    n = 12
    test = np.array([1, 2, 9, 10])
    kept = purge_train_indices(n, test, lookback=0, label_horizon=0, embargo_pct=0.0)
    assert 5 in kept
    assert 1 not in kept
    assert 9 not in kept


def test_invalid_n_splits_raises():
    with pytest.raises(ValueError, match="n_splits"):
        PurgedKFold(n_splits=1, lookback=0)
