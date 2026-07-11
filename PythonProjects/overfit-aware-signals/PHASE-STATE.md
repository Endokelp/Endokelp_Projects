# overfit-aware-signals — State
Vision: Quant research package proving 3 real cross-sectional equity signals (12-1 momentum, 1mo reversal, low-vol) against overfitting, using purged CV, CPCV, deflated Sharpe ratio, and probability of backtest overfitting (PBO) — all from primary sources (Bailey & Lopez de Prado 2014; Bailey/Borwein/Lopez de Prado/Zhu). Honest per-signal pass/fail verdict is the point, not a vanity Sharpe number.
Stack: Python 3.11+, numpy/pandas/yfinance/matplotlib. No scipy — `statistics.NormalDist` (stdlib 3.8+) covers norm cdf/inv_cdf for DSR; pandas `.skew()`/`.kurt()` cover moments; `itertools.combinations` covers CPCV path generation.
Run: `pip install -e ".[dev]"` && `pytest -v` && `ruff check src/ tests/`

## Done
- P1: scaffold + inputs — config/data/signals/portfolio built and ported from momentum-backtest/portfolio_mpt. `pip install -e ".[dev]"` clean, `pytest -v` 27/27 green, `ruff check` clean.
- P2: backtest engine + analytics — signal-agnostic `run_backtest(prices, signals, cfg)`, `compute_metrics` with skew/kurtosis, parity vs momentum-backtest hand fixtures. `pytest -v` 43/43 green, `ruff check` clean.
- P3: purged CV + embargo — `purge_train_indices` + `PurgedKFold`; info interval `[i-lookback, i+label_horizon]` so lookback leaks die even when labels don't overlap. `pytest -v` 48/48 green, `ruff check` clean.

## Current phase: 4 — combinatorial purged CV
Goals:
- `cpcv.py`: CombinatorialPurgedCV — S=`n_groups` blocks, k=`n_test_groups` test groups → C(S,k) paths; reuse `purge_train_indices` per path
- Return OOS Sharpe distribution across paths (feeds DSR/PBO later)
Done-when: `pytest -v` green including C(8,2)=28 path count test; `ruff check` clean.

## Decisions
- No scipy dependency — stdlib/pandas cover everything it would've (ponytail: fewer deps).
- 3 signals only, not 4 — a pairs/stat-arb signal was cut, different engineering surface, dilutes focus from the actual point (the overfitting toolkit).
- CPCV kept small: S=8 blocks, k=2 test groups -> C(8,2)=28 paths, via `itertools.combinations`.
- Code style: no docstrings, short var names, type hints on public API only — matches `volatility-targeting/vol.py`, not `momentum-backtest/signal.py` (the latter predates the style).
- Real universe (~50 tickers, current constituents) not point-in-time survivorship-free — stated honestly in README, not hidden.
- Differentiation note for later phases: the "implement AFML's toolkit as a portfolio piece" template is now common (per should-i-build research) — lean on the honest per-signal verdict + cite 2026-current extensions (e.g. DSR/PBO gating LLM-generated strategies), not a 2018-tutorial retread.
- P2: `run_backtest` takes precomputed signals (not a signal name) — backtest stays signal-agnostic; skips rows where `signals.iloc[i].dropna()` is empty.
- P3: purge helper is the reusable core (CPCV will call it per combo); `PurgedKFold.split(n_samples)` takes a length, not an array.

## Gotchas
- yfinance sometimes lacks "Adj Close" — fall back to "Close" (see portfolio_mpt's own loader for the exact pattern already hit in this repo).
- Purge must remove overlap from the signal's LOOKBACK window, not just the label window — a common shortcut that still leaks. Test this directly.
- Embargo is a *count* `int(n * embargo_pct)` of samples immediately after the test block — serial correlation beyond label_horizon.

## Key files
- `src/overfit_aware_signals/data.py` — yfinance + cache + synthetic panel
- `src/overfit_aware_signals/signals.py` — the 3-signal registry
- `src/overfit_aware_signals/portfolio.py` — weight formation
- `src/overfit_aware_signals/backtest.py` — signal-agnostic rebalancing loop
- `src/overfit_aware_signals/analytics.py` — sharpe/cagr/vol/maxDD/skew/kurtosis
- `src/overfit_aware_signals/cv.py` — purge_train_indices + PurgedKFold
- `../momentum-backtest/src/momentum_backtest/{backtest,signal,portfolio}.py` — porting source
- `../portfolio_mpt/multi_asset_data_loader.py` — yfinance fallback pattern
- Full design (cpcv/stats/pbo formulas, phases 2-5, should-i-build appendix): `C:\Users\venni\.claude\plans\sorted-gathering-willow.md`
