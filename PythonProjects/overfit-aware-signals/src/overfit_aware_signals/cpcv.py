from collections.abc import Iterator
from itertools import combinations
from math import comb

import numpy as np

from .cv import purge_train_indices


def _path_sharpe(rets: np.ndarray, periods_per_year: int) -> float:
    if len(rets) < 2:
        return float("nan")
    std = float(np.std(rets, ddof=1))
    if std == 0.0:
        return 0.0
    return float(np.mean(rets) / std * np.sqrt(periods_per_year))


def _group_slices(n_samples: int, n_groups: int) -> list[np.ndarray]:
    fold_sizes = np.full(n_groups, n_samples // n_groups, dtype=int)
    fold_sizes[: n_samples % n_groups] += 1
    bounds = np.cumsum(fold_sizes)
    groups: list[np.ndarray] = []
    start = 0
    for end in bounds:
        groups.append(np.arange(start, end))
        start = int(end)
    return groups


class CombinatorialPurgedCV:
    def __init__(
        self,
        n_groups: int,
        n_test_groups: int,
        lookback: int,
        embargo_pct: float = 0.0,
        label_horizon: int = 1,
    ):
        if n_groups < 2:
            raise ValueError(f"n_groups must be >= 2, got {n_groups}")
        if not 1 <= n_test_groups < n_groups:
            raise ValueError(
                f"n_test_groups must be in [1, n_groups), got {n_test_groups}"
            )
        if lookback < 0:
            raise ValueError(f"lookback must be >= 0, got {lookback}")
        self.n_groups = n_groups
        self.n_test_groups = n_test_groups
        self.lookback = lookback
        self.embargo_pct = embargo_pct
        self.label_horizon = label_horizon

    @property
    def n_combinations(self) -> int:
        return comb(self.n_groups, self.n_test_groups)

    @property
    def n_paths(self) -> int:
        # AFML: φ(N,k) = (k/N)·C(N,k) = C(N-1, k-1)
        return comb(self.n_groups - 1, self.n_test_groups - 1)

    def split(self, n_samples: int) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        if n_samples < self.n_groups:
            raise ValueError(
                f"n_samples ({n_samples}) must be >= n_groups ({self.n_groups})"
            )
        groups = _group_slices(n_samples, self.n_groups)
        for combo in combinations(range(self.n_groups), self.n_test_groups):
            test = np.concatenate([groups[g] for g in combo])
            train = purge_train_indices(
                n_samples,
                test,
                self.lookback,
                label_horizon=self.label_horizon,
                embargo_pct=self.embargo_pct,
            )
            yield train, test

    def path_group_splits(self) -> list[list[int | None]]:
        """For each path, map group → combination index that supplies its OOS block.

        ponytail: for fixed (non-fitted) signals every path reassembles the same
        returns; path Sharpes then collapse. Purge matters only when train fits.
        """
        splits = list(combinations(range(self.n_groups), self.n_test_groups))
        paths: list[list[int | None]] = [
            [None] * self.n_groups for _ in range(self.n_paths)
        ]
        for g in range(self.n_groups):
            containing = [i for i, s in enumerate(splits) if g in s]
            if len(containing) != self.n_paths:
                raise RuntimeError(
                    f"group {g}: expected {self.n_paths} containing splits, "
                    f"got {len(containing)}"
                )
            for path_id, split_i in enumerate(containing):
                paths[path_id][g] = split_i
        return paths


def combinatorial_test_sharpes(
    returns: np.ndarray,
    cv: CombinatorialPurgedCV,
    *,
    periods_per_year: int = 12,
) -> np.ndarray:
    """Sharpe on each combinatorial test-block set (stability diagnostic).

    Not CPCV paths — C(N,k) overlapping held-out folds. For fixed-rule signals
    purge/train indices do not change these values.
    """
    rets = np.asarray(returns, dtype=float)
    return np.asarray(
        [_path_sharpe(rets[te], periods_per_year) for _, te in cv.split(len(rets))],
        dtype=float,
    )


def path_sharpe_distribution(
    returns: np.ndarray,
    cv: CombinatorialPurgedCV,
    *,
    periods_per_year: int = 12,
) -> np.ndarray:
    """Sharpe on each reconstructed CPCV backtest path (φ = C(N-1, k-1))."""
    rets = np.asarray(returns, dtype=float)
    n = len(rets)
    groups = _group_slices(n, cv.n_groups)
    path_maps = cv.path_group_splits()
    sharpes: list[float] = []
    for path in path_maps:
        pieces: list[np.ndarray] = []
        for g, split_i in enumerate(path):
            if split_i is None:
                continue
            pieces.append(rets[groups[g]])
        if not pieces:
            sharpes.append(float("nan"))
            continue
        sharpes.append(_path_sharpe(np.concatenate(pieces), periods_per_year))
    return np.asarray(sharpes, dtype=float)
