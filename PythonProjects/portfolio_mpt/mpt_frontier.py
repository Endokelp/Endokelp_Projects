import os
import sys

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from matplotlib import pyplot as plt

# allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.paths import PORTFOLIO_DATA
from src.plot_style import (
    apply_plot_style,
    subtitle,
    finish_figure,
    FRONTIER,
    MVP,
    TANGENCY,
    EW,
    CML,
    SCATTER_TICKER,
    MUTED,
    INK,
)

# Load data from Excel
stats_df = pd.read_excel(PORTFOLIO_DATA, sheet_name="Summary Stats")
cov_df = pd.read_excel(PORTFOLIO_DATA, sheet_name="Covariance Matrix")

# Clean data
tickers = stats_df["Ticker"].values
mu = stats_df["Annualized Mean Return"].values
cov = cov_df.drop(columns=["Ticker"]).values
rf = 0.02  # Risk-free rate (2%)


def portfolio_performance(weights, mu, cov):
    returns = np.dot(weights, mu)
    variance = np.dot(weights.T, np.dot(cov, weights))
    std = np.sqrt(variance)
    return returns, std


# 1. Minimum Variance Portfolio (MVP)
constraints_mvp = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
bounds = tuple((0, 1) for _ in range(len(mu)))
mvp_result = minimize(
    lambda x: portfolio_performance(x, mu, cov)[1] ** 2,
    len(mu) * [1.0 / len(mu)],
    method="SLSQP",
    bounds=bounds,
    constraints=constraints_mvp,
)
mvp_weights = mvp_result.x
mvp_return, mvp_std = portfolio_performance(mvp_weights, mu, cov)


# 2. Maximum Sharpe Ratio Portfolio (Tangency Portfolio)
def neg_sharpe(weights, mu, cov, rf):
    p_ret, p_std = portfolio_performance(weights, mu, cov)
    return -(p_ret - rf) / p_std


max_sharpe_result = minimize(
    neg_sharpe,
    len(mu) * [1.0 / len(mu)],
    args=(mu, cov, rf),
    method="SLSQP",
    bounds=bounds,
    constraints=constraints_mvp,
)
m_sharpe_weights = max_sharpe_result.x
m_sharpe_return, m_sharpe_std = portfolio_performance(m_sharpe_weights, mu, cov)

# 3. Equal Weighted Portfolio (Baseline)
ew_weights = np.array(len(mu) * [1.0 / len(mu)])
ew_return, ew_std = portfolio_performance(ew_weights, mu, cov)


# 4. Generate Efficient Frontier points
def min_variance_for_return(target_return, mu, cov):
    n = len(mu)
    constraints = (
        {"type": "eq", "fun": lambda x: np.dot(x, mu) - target_return},
        {"type": "eq", "fun": lambda x: np.sum(x) - 1},
    )
    res = minimize(
        lambda x: portfolio_performance(x, mu, cov)[1] ** 2,
        n * [1.0 / n],
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    return res


target_returns = np.linspace(mvp_return, mu.max(), 50)
efficient_vols = []
for tr in target_returns:
    res = min_variance_for_return(tr, mu, cov)
    if res.success:
        efficient_vols.append(res.fun**0.5)
    else:
        efficient_vols.append(None)

# 5. Dump weights / stats to text
with open("opt_results.txt", "w") as f:
    f.write("--- Strategy Comparison Analysis ---\n\n")
    f.write("1. Minimum Variance Portfolio (MVP):\n")
    f.write(f"   Return: {mvp_return:.4f}, Risk: {mvp_std:.4f}\n")
    f.write(f"   Weights: {dict(zip(tickers, np.round(mvp_weights, 4)))}\n\n")

    f.write("2. Maximum Sharpe Ratio (Tangency):\n")
    f.write(f"   Return: {m_sharpe_return:.4f}, Risk: {m_sharpe_std:.4f}\n")
    f.write(f"   Sharpe: {-(max_sharpe_result.fun):.4f}\n")
    f.write(f"   Weights: {dict(zip(tickers, np.round(m_sharpe_weights, 4)))}\n\n")

    f.write("3. Equal Weighted (EW):\n")
    f.write(f"   Return: {ew_return:.4f}, Risk: {ew_std:.4f}\n")
    f.write(f"   Weights: {dict(zip(tickers, np.round(ew_weights, 4)))}\n")

# 6. Comparative Plot
apply_plot_style()
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.plot(
    efficient_vols,
    target_returns,
    color=FRONTIER,
    linewidth=2.2,
    label="Efficient frontier",
    zorder=3,
)
ax.scatter(
    mvp_std,
    mvp_return,
    color=MVP,
    marker="*",
    s=280,
    label="Min variance",
    edgecolors=INK,
    linewidths=0.6,
    zorder=5,
)
ax.scatter(
    m_sharpe_std,
    m_sharpe_return,
    color=TANGENCY,
    marker="v",
    s=130,
    label="Max Sharpe (tangency)",
    edgecolors="#3d3518",
    linewidths=0.5,
    zorder=5,
)
ax.scatter(
    ew_std,
    ew_return,
    color=EW,
    marker="o",
    s=95,
    label="Equal weight",
    edgecolors="#dfe6f0",
    linewidths=0.8,
    zorder=5,
)

cml_x = [0, m_sharpe_std * 1.5]
cml_y = [rf, rf + (m_sharpe_return - rf) / m_sharpe_std * (m_sharpe_std * 1.5)]
ax.plot(cml_x, cml_y, color=CML, linestyle="--", linewidth=1.4, alpha=0.85, label="Capital market line")

for i, ticker in enumerate(tickers):
    ax.scatter(
        np.sqrt(cov[i, i]),
        mu[i],
        color=SCATTER_TICKER,
        s=42,
        alpha=0.75,
        zorder=2,
        edgecolors="white",
        linewidths=0.35,
    )
    ax.annotate(
        ticker,
        (np.sqrt(cov[i, i]), mu[i]),
        xytext=(6, 4),
        textcoords="offset points",
        fontsize=9,
        color=MUTED,
    )

ax.set_xlabel("Annualized volatility")
ax.set_ylabel("Annualized expected return")
ax.set_title("Efficient frontier vs benchmarks")
subtitle(ax, "AAPL MSFT GOOGL NVDA PLTR — daily log returns, annualized")
ax.legend(loc="lower right", fontsize=9)
finish_figure(fig)
out = "research_comparison_frontier.png"
fig.savefig(out)
plt.close()
print(f"Comparative analysis plot saved as {out}")
