# portfolio_mpt

Modern portfolio theory in Python: mean–variance optimization, efficient frontiers, Monte Carlo exploration, and a multi-asset hierarchical-risk-parity / backtest pass on a separate dataset.

**Data files:** The tech basket input is `portfolio_data.xlsx` (from `src/data_loader.py`). The extended panel is `multi_asset_data.xlsx` (from `multi_asset_data_loader.py`). If you have older files named `IA_Portfolio_Data.xlsx` or `Dissertation_Full_Data.xlsx`, rename them to those names (or re-run the loaders) so the analysis scripts can find them.

## What’s in here

- **`src/data_loader.py`** — download adjusted closes from Yahoo Finance → `portfolio_data.xlsx` (prices, returns, summary stats, covariance).
- **`mpt_frontier.py`** — efficient frontier, MVP, max-Sharpe, equal-weight, capital market line; writes `opt_results.txt` and `research_comparison_frontier.png`.
- **`monte_carlo_sim.py`** — random long-only weights on the same input data.
- **`multi_asset_data_loader.py`** — downloads a broader basket → `multi_asset_data.xlsx`.
- **`multi_asset_analysis.py`** — correlation heatmap, HRP-style dendrogram, rolling correlation, drawdowns, simple backtest of min-var / HRP / equal weight.

**`src/paths.py`** — root-relative paths (no hard-coded drives).  
**`src/plot_style.py`** — shared matplotlib look.

## Setup

```bash
pip install -r requirements.txt
python src/data_loader.py
python mpt_frontier.py
python monte_carlo_sim.py
python multi_asset_data_loader.py
python multi_asset_analysis.py
```

Not financial advice. Outputs are for learning and presentation only.
