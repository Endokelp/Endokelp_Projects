import math
from itertools import combinations

import numpy as np

_EPS = 1e-12


def _block_bounds(n_samples: int, n_groups: int) -> list[tuple[int, int]]:
    sizes = np.full(n_groups, n_samples // n_groups, dtype=int)
    sizes[: n_samples % n_groups] += 1
    bounds: list[tuple[int, int]] = []
    start = 0
    for size in sizes:
        end = start + int(size)
        bounds.append((start, end))
        start = end
    return bounds


def _mean_perf(rets: np.ndarray, idx: np.ndarray) -> np.ndarray:
    # (T, N) → mean return per strategy on selected rows
    return rets[idx].mean(axis=0)


def _relative_rank(scores: np.ndarray, winner: int) -> float:
    # Higher score = better. Average mid-rank among ties; ω̄ = rank / N ∈ (0, 1]
    v = scores[winner]
    n = len(scores)
    n_worse = int(np.sum(scores < v))
    n_tie = int(np.sum(scores == v))
    rank = n_worse + (n_tie + 1) / 2.0
    return rank / n


def cscv_logits(returns: np.ndarray, n_groups: int = 16) -> np.ndarray:
    rets = np.asarray(returns, dtype=float)
    if rets.ndim != 2:
        raise ValueError(f"returns must be 2-D (T, N), got shape {rets.shape}")
    t, n = rets.shape
    if n < 2:
        raise ValueError(f"need >= 2 strategies, got {n}")
    if n_groups < 2 or n_groups % 2 != 0:
        raise ValueError(f"n_groups must be even and >= 2, got {n_groups}")
    if t < n_groups:
        raise ValueError(f"n_samples ({t}) must be >= n_groups ({n_groups})")

    bounds = _block_bounds(t, n_groups)
    half = n_groups // 2
    logits: list[float] = []
    for test_groups in combinations(range(n_groups), half):
        test_set = set(test_groups)
        train_idx = np.concatenate(
            [np.arange(a, b) for i, (a, b) in enumerate(bounds) if i not in test_set]
        )
        test_idx = np.concatenate(
            [np.arange(a, b) for i, (a, b) in enumerate(bounds) if i in test_set]
        )
        is_perf = _mean_perf(rets, train_idx)
        oos_perf = _mean_perf(rets, test_idx)
        winner = int(np.argmax(is_perf))
        w_bar = _relative_rank(oos_perf, winner)
        w_bar = min(max(w_bar, _EPS), 1.0 - _EPS)
        logits.append(math.log(w_bar / (1.0 - w_bar)))
    return np.asarray(logits, dtype=float)


def cscv_rank_pairs(
    returns: np.ndarray,
    n_groups: int = 16,
) -> tuple[np.ndarray, np.ndarray]:
    # Per combo × strategy: relative IS rank vs relative OOS rank (higher = better)
    rets = np.asarray(returns, dtype=float)
    if rets.ndim != 2:
        raise ValueError(f"returns must be 2-D (T, N), got shape {rets.shape}")
    t, n = rets.shape
    if n < 2:
        raise ValueError(f"need >= 2 strategies, got {n}")
    if n_groups < 2 or n_groups % 2 != 0:
        raise ValueError(f"n_groups must be even and >= 2, got {n_groups}")
    if t < n_groups:
        raise ValueError(f"n_samples ({t}) must be >= n_groups ({n_groups})")

    bounds = _block_bounds(t, n_groups)
    half = n_groups // 2
    is_ranks: list[float] = []
    oos_ranks: list[float] = []
    for test_groups in combinations(range(n_groups), half):
        test_set = set(test_groups)
        train_idx = np.concatenate(
            [np.arange(a, b) for i, (a, b) in enumerate(bounds) if i not in test_set]
        )
        test_idx = np.concatenate(
            [np.arange(a, b) for i, (a, b) in enumerate(bounds) if i in test_set]
        )
        is_perf = _mean_perf(rets, train_idx)
        oos_perf = _mean_perf(rets, test_idx)
        for j in range(n):
            is_ranks.append(_relative_rank(is_perf, j))
            oos_ranks.append(_relative_rank(oos_perf, j))
    return np.asarray(is_ranks, dtype=float), np.asarray(oos_ranks, dtype=float)


def probability_of_backtest_overfitting(
    returns: np.ndarray,
    n_groups: int = 16,
) -> float:
    logits = cscv_logits(returns, n_groups=n_groups)
    return float(np.mean(logits <= 0.0))
