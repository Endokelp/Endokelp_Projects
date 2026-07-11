# overfit-aware-signals — State
Vision: Quant research package proving 3 real cross-sectional equity signals (12-1 momentum, 1mo reversal, low-vol) against overfitting via CPCV/DSR/PBO from primary sources. Honest per-signal pass/fail is the point. **Showcase gate: 100% GO from re-audit.**
Stack: Python 3.11+, numpy/pandas/yfinance/matplotlib. No scipy.
Run: `pip install -e ".[dev]"` && `pytest -v` && `ruff check src/ tests/`
Demo: `python -m overfit_aware_signals synth` (preferred)  |  Live non-claim: `python -m overfit_aware_signals run`

## Agent routing (user mandate — every session)
- Reviews / audits / QA: **Sonnet subagents only — not Opus**
- Implementation / coding: prefer **Grok + Composer** wherever possible
- Catchup must restate this; do not regress to Opus for audits

## Done
- P1–P8: scaffold → live run (pre-audit Results later invalidated)
- P9: formula remediation — PBO `rank/(N+1)` + `λ<0`; CPCV `φ=C(N-1,k-1)` + block Sharpes; DSR cross-trial `V[{SR̂}]`; drop incomplete month; one-way Σ|Δw| costs; reversal = latest month.
- P10: showcase blockers closed — CSCV Sharpe-rank; `median_block_sharpe` / `block_sharpe_*` / `path_sharpe_distribution`; `RESEARCH_TRIAL_LOG` (9) + `--sensitivity` / `trials` CLI; survivorship NON-CLAIM + synth preferred; arXiv cites verified. `pytest` 84/84, ruff clean.
- P10b: Sonnet re-audit **100% GO for showcase** (2026-07-11). Deprecated `oos_sharpe_distribution` alias removed.

## Current phase: P11 — optional showcase polish / commit
Goals:
- Commit P9+P10 work if user wants (still uncommitted at digest write)
- Optional: regenerate onepager PDF; LinkedIn surface; portfolio page
Done-when:
- [ ] User commits or requests PR
- [ ] Optional polish only if requested

## Decisions
- No scipy. 3 signals (pairs cut). Pass `n_trials=` for discarded configs; log has 9.
- CPCV: S=8, k=2 → 28 combos, φ=7 paths; table median = combinatorial **block** Sharpes.
- PASS iff DSR≥0.95 and set PBO≤0.05.
- CSCV ranks by **Sharpe** (mean fallback only when subsample vol=0).
- Live Results = **non-claim** (survivorship); `synth` is the honest demo path.
- Showcase bar cleared: Sonnet **100% GO**.

## Gotchas
- Current-constituent universe = survivorship; DSR/PBO do not fix look-ahead constituency
- Undercounted `n_trials` inflates DSR (esp. lowvol ~n=50)
- Fixed-rule CPCV paths collapse — don’t sell path dispersion
- yfinance may lack Adj Close → Close fallback
- Large uncommitted tree (P9–P10 + showcase/) until user asks to commit

## Key files
- `src/overfit_aware_signals/{data,signals,portfolio,backtest,analytics,cv,cpcv,stats,pbo,research,plotting,cli}.py`
- `README.md`, `results/`, `showcase/`, this `PHASE-STATE.md`
