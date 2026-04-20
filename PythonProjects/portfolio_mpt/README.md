# portfolio_mpt

Scratch-paper quant work: mean–variance stuff on a handful of tech names, plus a messier multi-asset backtest / HRP experiment that grew out of the same thread.

## What’s actually in here

- **`src/data_loader.py`** — pulls adjusted closes from Yahoo, writes `IA_Portfolio_Data.xlsx` (means, covariance, etc.). Run this first if you’re cloning cold.
- **`calculate_ia_data.py`** — MVP, tangency, equal-weight, efficient frontier + CML; saves `research_comparison_frontier.png` and `opt_results.txt`.
- **`monte_carlo_sim.py`** — random long-only weights against the same μ and Σ; `monte_carlo_portfolios.png`.
- **`dissertation_analysis.py`** — longer backtest + correlation heatmap, dendrogram, rolling corr, drawdowns, equity curves. Needs `Dissertation_Full_Data.xlsx`. Outputs `dissertation_*.png` and `dissertation_backtest_metrics.csv`.
- **`analyze_bench_press.py`** — unrelated stats class exercise (strength vs endurance); two scatter PNGs.

Plot styling lives in **`src/plot_style.py`** so the figures don’t all look like default matplotlib homework.

## Setup

```bash
pip install -r requirements.txt
python src/data_loader.py          # optional: refresh Excel from Yahoo
python calculate_ia_data.py
python monte_carlo_sim.py
python dissertation_analysis.py    # if you have the dissertation workbook
python analyze_bench_press.py
```

## What I’m not claiming

This isn’t trading advice, not a product, and not a promise that any of these weights would have been tradable with zero slippage. It’s code I wrote to understand the math and stress how sensitive optimization is to inputs.

Personal submission PDFs / Word docs aren’t in this folder on purpose.
