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
    def n_paths(self) -> int:
        return comb(self.n_groups, self.n_test_groups)

    def split(self, n_samples: int) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        if n_samples < self.n_groups:
            raise ValueError(
                f"n_samples ({n_samples}) must be >= n_groups ({self.n_groups})"
            )
        fold_sizes = np.full(self.n_groups, n_samples // self.n_groups, dtype=int)
        fold_sizes[: n_samples % self.n_groups] += 1
        bounds = np.cumsum(fold_sizes)
        groups: list[np.ndarray] = []
        start = 0
        for end in bounds:
            groups.append(np.arange(start, end))
            start = int(end)

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


def oos_sharpe_distribution(
    returns: np.ndarray,
    cv: CombinatorialPurgedCV,
    *,
    periods_per_year: int = 12,
) -> np.ndarray:
    rets = np.asarray(returns, dtype=float)
    return np.asarray(
        [_path_sharpe(rets[te], periods_per_year) for _, te in cv.split(len(rets))],
        dtype=float,
    )
