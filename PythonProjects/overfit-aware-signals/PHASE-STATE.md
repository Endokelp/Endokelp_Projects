# overfit-aware-signals — State
Vision: Quant research package proving 3 real cross-sectional equity signals (12-1 momentum, 1mo reversal, low-vol) against overfitting, using purged CV, CPCV, deflated Sharpe ratio, and probability of backtest overfitting (PBO) — all from primary sources (Bailey & Lopez de Prado 2014; Bailey/Borwein/Lopez de Prado/Zhu). Honest per-signal pass/fail verdict is the point, not a vanity Sharpe number.
Stack: Python 3.11+, numpy/pandas/yfinance/matplotlib. No scipy — `statistics.NormalDist` (stdlib 3.8+) covers norm cdf/inv_cdf for DSR; pandas `.skew()`/`.kurt()` cover moments; `itertools.combinations` covers CPCV/CSCV path generation.
Run: `pip install -e ".[dev]"` && `pytest -v` && `ruff check src/ tests/`

## Done
- P1: scaffold + inputs — config/data/signals/portfolio. `pytest` 27/27, ruff clean.
- P2: backtest engine + analytics — signal-agnostic `run_backtest`, `compute_metrics`. `pytest` 43/43, ruff clean.
- P3: purged CV + embargo — `purge_train_indices` + `PurgedKFold`; lookback-aware info interval. `pytest` 48/48, ruff clean.
- P4: combinatorial purged CV — `CombinatorialPurgedCV` C(S,k) paths + `oos_sharpe_distribution`; purge fixed for non-contiguous test blocks. `pytest` 53/53, ruff clean.
- P5: PSR/DSR — `probabilistic_sharpe_ratio`, `expected_max_sharpe`, `deflated_sharpe_ratio` via `NormalDist`; hand-worked (SR=1,T=60,γ3=0,γ4=3) green. `pytest` 60/60, ruff clean.
- P6: PBO via CSCV — `cscv_logits` + `probability_of_backtest_overfitting`; toy PBO=0 (stable rank) and PBO=1 (IS/OOS flip) green. `pytest` 67/67, ruff clean.

## Current phase: 7 — research orchestration + CLI
Goals:
- `research.py`: signals × CPCV × DSR × PBO → results DataFrame with per-signal pass/fail
- `plotting.py`: OOS Sharpe histograms, IS-rank vs OOS-rank scatter
- `cli.py` + `__main__.py`: `run` / `synth` offline demo
Done-when: `python -m overfit_aware_signals synth` prints a verdict table; `pytest -v` + `ruff check` clean.

## Decisions
- No scipy — stdlib/pandas cover DSR moments and CPCV/CSCV combos.
- 3 signals only (pairs/stat-arb cut — different surface, dilutes overfitting-toolkit focus).
- CPCV: S=8, k=2 → C(8,2)=28 via `itertools.combinations`.
- Code style: no docstrings, short vars, type hints on public API only (`volatility-targeting/vol.py` template).
- Real universe ~50 tickers, current constituents — not PIT survivorship-free; state in README.
- Differentiator for later: honest per-signal verdict + cite 2026 DSR/PBO-on-LLM-strategies work, not AFML tutorial retread.
- P2: `run_backtest` takes precomputed signals; skips empty signal rows.
- P3: purge helper is the reusable core; `PurgedKFold.split(n_samples)` takes a length.
- P4: `oos_sharpe_distribution` evaluates precomputed path returns on test indices (rule-based signals — no IS fit yet); train indices reserved for later hyperparam selection.
- P5: `kurt` is γ4 (non-excess; normal=3), not pandas excess. Callers convert `rets.kurt() + 3`.
- P6: CSCV ranks by mean return on concatenated blocks; ω̄ = mid-rank/N; PBO = mean(λ≤0). Paper cutoff reject if PBO > 0.05.

## Gotchas
- yfinance may lack "Adj Close" — fall back to "Close" (portfolio_mpt loader pattern).
- Purge on LOOKBACK window overlap, not just labels — test explicitly.
- Embargo = `int(n * embargo_pct)` samples after *each* contiguous test block (CPCV gaps).
- Contiguous min/max purge over-deletes middle train groups under CPCV — purge must segment non-contiguous test indices.
- PSR/DSR: pass γ4 raw kurtosis; pandas `.kurt()` is excess → add 3 before calling.
- CSCV: `n_groups` must be even; returns shape (T, N) with N≥2 strategies.

## Key files
- `src/overfit_aware_signals/{data,signals,portfolio,backtest,analytics}.py`
- `src/overfit_aware_signals/cv.py` — purge_train_indices + PurgedKFold
- `src/overfit_aware_signals/cpcv.py` — CombinatorialPurgedCV + oos_sharpe_distribution
- `src/overfit_aware_signals/stats.py` — PSR, expected_max_sharpe (SR0), DSR
- `src/overfit_aware_signals/pbo.py` — CSCV logits + PBO
- Full design: `C:\Users\venni\.claude\plans\sorted-gathering-willow.md`
