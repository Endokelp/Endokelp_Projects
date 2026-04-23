import os
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.optimize import minimize
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.paths import MULTI_ASSET_DATA, ROOT
from src.plot_style import (
    PAPER,
    apply_plot_style,
    subtitle,
    finish_figure,
    FRONTIER,
    MVP,
    ACCENT_LINE,
    MUTED,
    INK,
)


def get_hrp_weights(cov, corr):

    def get_hrp_allocation(cov_mat, _cluster_items):
        inv_var = 1.0 / np.diag(cov_mat)
        weights = inv_var / inv_var.sum()
        return pd.Series(weights, index=cov_mat.index)

    return get_hrp_allocation(cov, corr.columns)


def get_mvo_weights(mu, cov, target_return=None):
    n = len(mu)

    def obj(w):
        return np.dot(w.T, np.dot(cov, w))

    constraints = [{"type": "eq", "fun": lambda x: np.sum(x) - 1}]
    if target_return:
        constraints.append({"type": "eq", "fun": lambda x: np.dot(x, mu) - target_return})

    bounds = tuple((0, 1) for _ in range(n))
    res = minimize(obj, n * [1.0 / n], method="SLSQP", bounds=bounds, constraints=constraints)
    return res.x


def run_backtest(prices, rebalance_freq="ME"):
    returns = np.log(prices / prices.shift(1)).dropna()
    tickers = prices.columns

    lookback = 252

    strategies = {"MVO (Min Var)": [], "HRP (inverse-var)": [], "Equal-Weighted": []}

    dates = returns.index[lookback:]
    portfolio_values = {k: [1.0] for k in strategies.keys()}

    print(f"Starting backtest from {dates[0]} to {dates[-1]}...")

    current_weights = {k: np.array([1.0 / len(tickers)] * len(tickers)) for k in strategies.keys()}

    for i in range(lookback, len(returns)):
        daily_ret = returns.iloc[i].values

        for name, weights in current_weights.items():
            ret = np.dot(weights, daily_ret)
            new_val = portfolio_values[name][-1] * np.exp(ret)
            portfolio_values[name].append(new_val)

        if i % 21 == 0:
            window = returns.iloc[i - lookback : i]
            mu = window.mean() * 252
            cov = window.cov() * 252
            corr = window.corr()

            current_weights["MVO (Min Var)"] = get_mvo_weights(mu, cov)
            current_weights["HRP (inverse-var)"] = get_hrp_weights(cov, corr).values
            current_weights["Equal-Weighted"] = np.array([1.0 / len(tickers)] * len(tickers))

    results_df = pd.DataFrame(portfolio_values, index=returns.index[lookback - 1 :])
    return results_df


def _corr_cmap():
    """Dusty teal ↔ brick — not the default coolwarm."""
    return sns.diverging_palette(200, 25, s=62, l=52, as_cmap=True)


def generate_visual_analytics(prices, returns, backtest_results):
    apply_plot_style()

    # 1. Correlation Heatmap
    corr = returns.corr()
    fig, ax = plt.subplots(figsize=(9.5, 7.8))
    sns.heatmap(
        corr,
        annot=True,
        cmap=_corr_cmap(),
        fmt=".2f",
        linewidths=0.6,
        linecolor=PAPER,
        ax=ax,
        vmin=-1,
        vmax=1,
        annot_kws={"size": 9, "color": INK},
    )
    ax.set_title("Pairwise correlations")
    subtitle(ax, "Daily log returns, full sample")
    finish_figure(fig)
    fig.savefig(ROOT / "multi_asset_heatmap.png")
    plt.close()

    # 2. HRP Cluster Dendrogram
    dist = np.sqrt(0.5 * (1 - corr))
    d = dist.values.copy()
    np.fill_diagonal(d, 0.0)
    link = linkage(squareform(d, checks=False), "single")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    dendrogram(link, labels=list(corr.columns), ax=ax, color_threshold=0, above_threshold_color=MUTED)
    ax.set_title("Single-linkage tree from correlation distance")
    subtitle(ax, "Distance = √(0.5(1 − ρ))")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=9)
    finish_figure(fig)
    fig.savefig(ROOT / "multi_asset_dendrogram.png")
    plt.close()

    # 3. Rolling Correlation
    rolling_corr = returns["NVDA"].rolling(window=252).corr(returns["SPY"])
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(rolling_corr.index, rolling_corr.values, color=FRONTIER, linewidth=1.35, label="NVDA vs SPY (1y rolling)")
    ax.axhline(
        rolling_corr.mean(),
        color=MVP,
        linestyle="--",
        linewidth=1.1,
        label=f"Mean ≈ {rolling_corr.mean():.2f}",
    )
    ax.set_ylabel("Correlation")
    ax.set_xlabel("Date")
    ax.set_title("NVDA vs SPY, rolling 1y correlation")
    subtitle(ax, "252 trading days")
    ax.legend(loc="lower left", fontsize=9)
    finish_figure(fig)
    fig.savefig(ROOT / "multi_asset_rolling_corr.png")
    plt.close()

    # 4. Drawdown Profile
    fig, ax = plt.subplots(figsize=(11, 6))
    series_colors = [FRONTIER, ACCENT_LINE, MVP]
    for idx, col in enumerate(backtest_results.columns):
        rolling_max = backtest_results[col].cummax()
        drawdowns = (backtest_results[col] - rolling_max) / rolling_max
        ax.fill_between(
            drawdowns.index,
            drawdowns,
            label=col,
            alpha=0.28,
            color=series_colors[idx % len(series_colors)],
        )
    ax.set_ylabel("Drawdown (fraction of peak)")
    ax.set_title("Drawdowns")
    subtitle(ax, "Min-var / HRP / equal weight; rules in script")
    ax.legend(loc="lower left", fontsize=9)
    finish_figure(fig)
    fig.savefig(ROOT / "multi_asset_drawdowns.png")
    plt.close()


def main():
    file_path = MULTI_ASSET_DATA
    prices = pd.read_excel(file_path, sheet_name="Price Data", index_col="Date")
    returns = np.log(prices / prices.shift(1)).dropna()

    backtest_results = run_backtest(prices)

    generate_visual_analytics(prices, returns, backtest_results)

    apply_plot_style()
    fig, ax = plt.subplots(figsize=(12.5, 6.5))
    series_colors = [FRONTIER, ACCENT_LINE, MVP]
    for idx, col in enumerate(backtest_results.columns):
        ax.plot(
            backtest_results.index,
            backtest_results[col],
            label=col,
            linewidth=1.55,
            color=series_colors[idx % len(series_colors)],
        )
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth of $1")
    ax.set_title("Cumulative $1 (backtest script)")
    subtitle(ax, "~monthly rebalance, 1y rolling window; no costs")
    ax.legend(loc="upper left", fontsize=9)
    finish_figure(fig)
    fig.savefig(ROOT / "multi_asset_backtest_equity.png")
    plt.close()

    metrics = {}
    for col in backtest_results.columns:
        total_return = (backtest_results[col].iloc[-1] / backtest_results[col].iloc[0]) - 1
        ann_return = (1 + total_return) ** (252 / len(backtest_results)) - 1

        rolling_max = backtest_results[col].cummax()
        drawdowns = (backtest_results[col] - rolling_max) / rolling_max
        max_dd = drawdowns.min()

        vol = backtest_results[col].pct_change().std() * np.sqrt(252)

        metrics[col] = {
            "Total Return": total_return,
            "Annualized Return": ann_return,
            "Annualized Volatility": vol,
            "Max Drawdown": max_dd,
            "Sharpe Ratio": ann_return / vol,
        }

    metrics_df = pd.DataFrame(metrics).transpose()
    metrics_path = ROOT / "multi_asset_backtest_metrics.csv"
    metrics_df.to_csv(metrics_path)
    print("\n--- Backtest Performance Metrics ---")
    print(metrics_df)
    print(f"\nSaved metrics to {metrics_path} and plots under {ROOT}")


if __name__ == "__main__":
    main()
