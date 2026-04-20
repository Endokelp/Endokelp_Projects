# portfolio_mpt

Scratch-paper quant: mean–variance on a few tech names, plus a longer multi-asset backtest / HRP experiment.

## What’s in here

- **`src/data_loader.py`** — Yahoo → `IA_Portfolio_Data.xlsx`
- **`calculate_ia_data.py`** — frontier, MVP, tangency, equal weight
- **`monte_carlo_sim.py`** — random weights
- **`dissertation_analysis.py`** — heatmap, dendrogram, rolling corr, drawdowns, equity curves (`Dissertation_Full_Data.xlsx`)
- **`analyze_bench_press.py`** — separate class exercise

**`src/plot_style.py`** — matplotlib rcParams + fixed colors.

## Setup

```bash
pip install -r requirements.txt
python src/data_loader.py
python calculate_ia_data.py
python monte_carlo_sim.py
python dissertation_analysis.py
python analyze_bench_press.py
```

Not trading advice. Course submission PDFs/DOCX aren’t in this tree on purpose.
