import os
import sys

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.paths import PORTFOLIO_DATA
from src.plot_style import apply_plot_style, subtitle, finish_figure, MONTE_CMAP, MUTED

# Load data
stats_df = pd.read_excel(PORTFOLIO_DATA, sheet_name="Summary Stats")
cov_df = pd.read_excel(PORTFOLIO_DATA, sheet_name="Covariance Matrix")

tickers = stats_df["Ticker"].values
mu = stats_df["Annualized Mean Return"].values
cov = cov_df.drop(columns=["Ticker"]).values

# Monte Carlo Simulation
num_portfolios = 10000
results = np.zeros((3, num_portfolios))

for i in range(num_portfolios):
    weights = np.random.random(len(tickers))
    weights /= np.sum(weights)

    portfolio_return = np.dot(weights, mu)
    portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))

    results[0, i] = portfolio_return
    results[1, i] = portfolio_std
    results[2, i] = (portfolio_return - 0.02) / portfolio_std

apply_plot_style()
fig, ax = plt.subplots(figsize=(10.5, 6.8))
sc = ax.scatter(
    results[1, :],
    results[0, :],
    c=results[2, :],
    cmap=MONTE_CMAP,
    marker="o",
    s=14,
    alpha=0.35,
    edgecolors="none",
    rasterized=True,
)
cbar = fig.colorbar(sc, ax=ax, shrink=0.82, pad=0.02)
cbar.set_label("Sharpe (rf = 2%)", color=MUTED)
cbar.ax.tick_params(colors=MUTED)
ax.set_xlabel("Volatility (annualized σ)")
ax.set_ylabel("Expected return (annualized μ)")
ax.set_title("Monte Carlo: random long-only weights")
subtitle(ax, f"{len(tickers)} tickers, {num_portfolios:,} draws")
finish_figure(fig)
out = "monte_carlo_portfolios.png"
fig.savefig(out)
plt.close()
print(f"Monte Carlo plot saved as {out}")
