# momentum-backtest

A monthly cross-sectional momentum backtest written from scratch in Python.
No black-box backtest framework is used — every step of the engine is explicit
code you can read and audit.

## Layout

```
PythonProjects/momentum-backtest/
├── pyproject.toml
├── README.md
├── src/
│   └── momentum_backtest/
│       ├── __init__.py
│       ├── __main__.py      # python -m momentum_backtest
│       ├── config.py        # BacktestConfig dataclass
│       ├── data.py          # synthetic price generation + CSV loader
│       ├── signal.py        # momentum signal (vectorised, no lookahead)
│       ├── portfolio.py     # long-only and long-short weight formation
│       ├── backtest.py      # main rebalancing loop → BacktestResult
│       └── analytics.py     # CAGR, vol, Sharpe, drawdown, turnover
└── tests/
    ├── conftest.py
    ├── test_signal.py
    ├── test_portfolio.py
    ├── test_backtest.py
    └── test_analytics.py
```

## Quick start

```bash
# install (editable)
pip install -e ".[dev]"

# run example on synthetic data
python -m momentum_backtest

# run tests
pytest -v

# lint
ruff check src/ tests/
```

## Design decisions

### Signal (signal.py)

```
signal[t] = prices[t - skip] / prices[t - skip - lookback] - 1
```

- **lookback_months** (default 12): number of months in the return window.
- **skip_recent_month** (default True): sets `skip = 1`, i.e., the 12-1
  momentum variant that excludes the most recent month to avoid
  short-term reversal contamination.  Setting `False` uses the current
  month's price (lookahead if that price is not yet settled — see
  _Pitfalls_ below).

The signal is computed in a single vectorised pandas operation
(`prices.shift(skip) / prices.shift(skip + lookback) - 1`), so the
entire signal matrix is produced without a Python loop.

### Portfolio formation (portfolio.py)

| Mode | Description |
|---|---|
| `long_only` | Equal-weight top-N by signal; weights sum to 1 |
| `long_short` | Equal-weight top-N long, bottom-N short; weights sum to 0, gross exposure 2 |

Assets with NaN signal (insufficient history) are excluded from ranking.

### Rebalancing (backtest.py)

Rebalances every calendar month, at month-end close prices.

**Timeline:**

```
... | month t (rebalance): observe signal[t], form weights | month t+1: earn return | ...
```

The return earned in period t+1 is `prices[t+1] / prices[t] - 1` for each
asset.  Costs are charged at rebalance time (not at the end of the holding
period) to be conservative.

### Transaction costs (backtest.py)

```
one_way_turnover = Σ |w_new - w_old| / 2
cost = one_way_turnover × cost_bps / 10_000
```

`cost_bps` (default 10 bps) is deducted from that period's return.
The first rebalance has turnover ≈ 1.0 (going from cash to fully invested).

### Performance analytics (analytics.py)

| Metric | Formula |
|---|---|
| CAGR | `final_equity^(ppy/n) − 1` |
| Annual vol | `σ_monthly × √ppy` |
| Sharpe | `mean_excess_monthly × √ppy / σ_monthly` |
| Max drawdown | `min((equity − cummax) / cummax)` |
| Avg turnover | `mean of one-way turnovers` |

Risk-free rate: configurable via `BacktestConfig.rf_annual` (default 0).
`ppy` = `trading_periods_per_year` (default 12 for monthly data).

### Missing data (data.py / backtest.py)

- **Synthetic panel**: complete by construction — no missing values.
- **CSV panel** (`load_csv_prices`):
  1. Assets with > 20 % missing rows are dropped.
  2. Remaining gaps are forward-filled then back-filled.  This introduces
     spurious zero-return periods at the edges of an asset's listing.
     Callers should be aware that such assets will show a signal of 0
     until they have enough live history (which keeps them ranked in the
     middle and excluded from the tails).

## Pitfalls avoided

### 1. Lookahead bias in the signal

**Bug**: using `prices / prices.shift(lookback) - 1` with `skip=0` means the
signal at the rebalance date includes the current period's price, which is
the same price used as the _cost basis_ for the forward holding.  In a
monthly panel where you rebalance at month-end, the current price is not
yet known at the time the order is placed.

**Fix**: always pass `skip ≥ 1`.  The default (`skip_recent_month=True`) uses
`skip=1`.  The test `test_lookahead_inverts_signal_rankings` demonstrates
that `skip=0` inverts the ranking on the reversal panel.

### 2. Using next-period returns in the signal

**Bug**: accidentally computing `monthly_returns.shift(-1)` would give you the
return you are _about to earn_ — perfect foresight.

**Fix**: the holding-period return uses `monthly_returns.iloc[i+1]`, not a
shifted column, so it is always strictly after the rebalance decision.

### 3. Signal window alignment

Standard pandas `pct_change(lookback)` uses `prices[t]/prices[t-lookback]-1`,
which is correct for `skip=0` but does not support `skip=1` cleanly.
Using explicit `.shift(skip)` / `.shift(skip+lookback)` makes the window
endpoints explicit and auditable.

### 4. First rebalance without prior positions

Starting from an all-zero weight vector means the first rebalance always
shows turnover equal to the full initial allocation.  This is intentional
and conservative — it charges the cost of entering the first portfolio.

### 5. Survivorship bias

The synthetic panel generates all assets over the full period, so no
survivorship bias can enter.  When loading real CSV data you must ensure
the input panel is point-in-time (delisted assets included through their
last trade date).

## Running with real data

```python
from momentum_backtest import BacktestConfig, load_csv_prices, run_backtest
from momentum_backtest.analytics import compute_metrics, print_metrics

prices = load_csv_prices("your_prices.csv")   # date-indexed, asset columns
cfg = BacktestConfig(lookback_months=12, n_longs=20, cost_bps=5)
result = run_backtest(prices, cfg)
print_metrics(compute_metrics(result))
```

CSV expectations: first column = parseable date, remaining columns = close
prices, no header quirks.  See `data.load_csv_prices` docstring for the
missing-data handling rules.

## Configuration reference

| Parameter | Default | Description |
|---|---|---|
| `lookback_months` | 12 | Return window length |
| `skip_recent_month` | True | Exclude most recent month (12-1 style) |
| `portfolio_mode` | `"long_only"` | `"long_only"` or `"long_short"` |
| `n_longs` | 5 | Number of long positions |
| `n_shorts` | 5 | Number of short positions (long_short only) |
| `cost_bps` | 10 | One-way transaction cost in basis points |
| `rf_annual` | 0.0 | Annual risk-free rate for Sharpe |
| `n_assets` | 20 | Synthetic panel: number of assets |
| `n_years` | 15 | Synthetic panel: years of history |
| `seed` | 42 | Random seed for reproducibility |
