from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .pbo import cscv_rank_pairs


def plot_block_sharpe_hist(
    block_sharpes: np.ndarray,
    *,
    title: str = "Combinatorial block Sharpe",
    path: str | Path | None = None,
) -> plt.Figure:
    fig, ax = plt.subplots()
    vals = np.asarray(block_sharpes, dtype=float)
    vals = vals[np.isfinite(vals)]
    ax.hist(vals, bins=min(20, max(5, len(vals) // 2)), edgecolor="black", linewidth=0.4)
    ax.set_title(title)
    ax.set_xlabel("block Sharpe")
    ax.set_ylabel("count")
    fig.tight_layout()
    if path is not None:
        fig.savefig(path)
    return fig


def plot_is_oos_rank_scatter(
    returns: np.ndarray,
    n_groups: int = 16,
    *,
    title: str = "IS Sharpe-rank vs OOS Sharpe-rank",
    path: str | Path | None = None,
) -> plt.Figure:
    is_r, oos_r = cscv_rank_pairs(returns, n_groups=n_groups)
    fig, ax = plt.subplots()
    ax.scatter(is_r, oos_r, s=12, alpha=0.6)
    ax.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=1.0)
    ax.set_title(title)
    ax.set_xlabel("IS relative Sharpe-rank")
    ax.set_ylabel("OOS relative Sharpe-rank")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    if path is not None:
        fig.savefig(path)
    return fig
