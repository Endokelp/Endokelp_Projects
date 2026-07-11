from collections.abc import Iterator

import numpy as np


def _contiguous_segments(indices: np.ndarray) -> list[np.ndarray]:
    if indices.size == 0:
        return []
    idx = np.sort(np.unique(indices.astype(int)))
    breaks = np.where(np.diff(idx) > 1)[0] + 1
    return list(np.split(idx, breaks))


def purge_train_indices(
    n_samples: int,
    test_indices: np.ndarray,
    lookback: int,
    *,
    label_horizon: int = 1,
    embargo_pct: float = 0.0,
) -> np.ndarray:
    if n_samples < 1:
        raise ValueError(f"n_samples must be >= 1, got {n_samples}")
    if lookback < 0:
        raise ValueError(f"lookback must be >= 0, got {lookback}")
    if label_horizon < 0:
        raise ValueError(f"label_horizon must be >= 0, got {label_horizon}")
    if not 0.0 <= embargo_pct < 1.0:
        raise ValueError(f"embargo_pct must be in [0, 1), got {embargo_pct}")

    test = np.asarray(test_indices, dtype=int)
    if test.size == 0:
        return np.arange(n_samples)

    test_set = set(test.tolist())
    segments = _contiguous_segments(test)
    embargo = int(n_samples * embargo_pct)

    keep: list[int] = []
    for i in range(n_samples):
        if i in test_set:
            continue
        drop = False
        for seg in segments:
            seg_max = int(seg.max())
            # embargo after each contiguous test block (CPCV has gaps between groups)
            if seg_max + 1 <= i < seg_max + 1 + embargo:
                drop = True
                break
            # info interval for obs i: [i - lookback, i + label_horizon]
            t0 = i - lookback
            t1 = i + label_horizon
            test_t0 = int(seg.min()) - lookback
            test_t1 = int(seg.max()) + label_horizon
            if t0 <= test_t1 and test_t0 <= t1:
                drop = True
                break
        if not drop:
            keep.append(i)
    return np.asarray(keep, dtype=int)


class PurgedKFold:
    def __init__(
        self,
        n_splits: int,
        lookback: int,
        embargo_pct: float = 0.0,
        label_horizon: int = 1,
    ):
        if n_splits < 2:
            raise ValueError(f"n_splits must be >= 2, got {n_splits}")
        if lookback < 0:
            raise ValueError(f"lookback must be >= 0, got {lookback}")
        self.n_splits = n_splits
        self.lookback = lookback
        self.embargo_pct = embargo_pct
        self.label_horizon = label_horizon

    def split(self, n_samples: int) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        if n_samples < self.n_splits:
            raise ValueError(
                f"n_samples ({n_samples}) must be >= n_splits ({self.n_splits})"
            )
        fold_sizes = np.full(self.n_splits, n_samples // self.n_splits, dtype=int)
        fold_sizes[: n_samples % self.n_splits] += 1
        bounds = np.cumsum(fold_sizes)

        start = 0
        for end in bounds:
            test = np.arange(start, end)
            train = purge_train_indices(
                n_samples,
                test,
                self.lookback,
                label_horizon=self.label_horizon,
                embargo_pct=self.embargo_pct,
            )
            yield train, test
            start = int(end)
