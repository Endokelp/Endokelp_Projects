# overfit-aware-signals — State
Vision: Quant research package proving 3 real cross-sectional equity signals (12-1 momentum, 1mo reversal, low-vol) against overfitting, using purged CV, CPCV, deflated Sharpe ratio, and probability of backtest overfitting (PBO) — all from primary sources (Bailey & Lopez de Prado 2014; Bailey/Borwein/Lopez de Prado/Zhu). Honest per-signal pass/fail verdict is the point, not a vanity Sharpe number.
Stack: Python 3.11+, numpy/pandas/yfinance/matplotlib. No scipy — `statistics.NormalDist` (stdlib 3.8+) covers norm cdf/inv_cdf for DSR; pandas `.skew()`/`.kurt()` cover moments; `itertools.combinations` covers CPCV/CSCV path generation.
Run: `pip install -e ".[dev]"` && `pytest -v` && `ruff check src/ tests/`
Demo: `python -m overfit_aware_signals synth`  |  Live: `python -m overfit_aware_signals run`

## Done
- P1: scaffold + inputs — config/data/signals/portfolio. `pytest` 27/27, ruff clean.
- P2: backtest engine + analytics — signal-agnostic `run_backtest`, `compute_metrics`. `pytest` 43/43, ruff clean.
- P3: purged CV + embargo — `purge_train_indices` + `PurgedKFold`; lookback-aware info interval. `pytest` 48/48, ruff clean.
- P4: combinatorial purged CV — `CombinatorialPurgedCV` C(S,k) paths + `oos_sharpe_distribution`. `pytest` 53/53, ruff clean.
- P5: PSR/DSR via `NormalDist`; hand-worked (SR=1,T=60,γ3=0,γ4=3) green. `pytest` 60/60, ruff clean.
- P6: PBO via CSCV; toy PBO=0 / PBO=1 green. `pytest` 67/67, ruff clean.
- P7: `research.py` + `plotting.py` + `cli.py`/`__main__.py`; `synth` prints verdict table. `pytest` 74/74, ruff clean.

## Current phase: 8 — real universe run + README
Goals:
- `python -m overfit_aware_signals run` on ~50-ticker universe; capture DSR/PBO/verdict numbers
- README: Results table, honest per-signal verdict, "why this isn't just another AFML clone", survivorship caveat
Done-when: README quotes real (non-NaN) numbers; `pytest` + `ruff` still green.

## Decisions
- No scipy — stdlib/pandas cover DSR moments and CPCV/CSCV combos.
- 3 signals only (pairs/stat-arb cut).
- CPCV: S=8, k=2 → C(8,2)=28. Code style: no docstrings, short vars, type hints on public API only.
- Real universe ~50 tickers, current constituents — not PIT survivorship-free; state in README.
- Differentiator: honest per-signal verdict + cite 2026 DSR/PBO-on-LLM-strategies work.
- P5: `kurt` is γ4 (non-excess; normal=3); callers use `rets.kurt() + 3`.
- P6: CSCV ranks by mean return; PBO = mean(λ≤0); reject if PBO > 0.05.
- P7: DSR uses non-annualized SR; n_trials = # signals; PBO is set-level (same across rows); PASS iff DSR≥0.95 and PBO≤0.05.
- P7: CLI avoids non-ASCII for Windows cp1252 consoles.

## Gotchas
- yfinance may lack "Adj Close" — fall back to "Close".
- Purge on LOOKBACK window overlap, not just labels.
- Embargo after *each* contiguous test block (CPCV gaps).
- Contiguous min/max purge over-deletes under CPCV — purge must segment.
- PSR/DSR: pandas `.kurt()` is excess → add 3.
- CSCV: `n_groups` even; returns (T, N) with N≥2.
- Windows consoles: no Unicode arrows in CLI prints.

## Key files
- `src/overfit_aware_signals/{data,signals,portfolio,backtest,analytics,cv,cpcv,stats,pbo}.py`
- `src/overfit_aware_signals/research.py` — evaluate_signals + verdict table
- `src/overfit_aware_signals/{plotting,cli,__main__}.py`
- Full design: `C:\Users\venni\.claude\plans\sorted-gathering-willow.md`
