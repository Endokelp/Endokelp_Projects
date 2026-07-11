# overfit-aware-signals - State
Vision: Quant research package proving 3 real cross-sectional equity signals (12-1 momentum, 1mo reversal, low-vol) against overfitting via CPCV/DSR/PBO from primary sources. Honest per-signal pass/fail is the point. Showcase gate: 100% GO from re-audit.
Stack: Python 3.11+, numpy/pandas/yfinance/matplotlib. No scipy.
Run: `pip install -e ".[dev]"` && `pytest -v` && `ruff check src/ tests/`
Demo: `python -m overfit_aware_signals synth` (preferred)  |  Live non-claim: `python -m overfit_aware_signals run`

## Agent routing (user mandate - every session)
- Reviews / audits / QA: Sonnet subagents only, not Opus
- Implementation / coding: prefer Grok + Composer wherever possible
- Catchup must restate this; do not regress to Opus for audits

## Done
- P1-P8: scaffold through live run (pre-audit Results later invalidated)
- P9: formula remediation - PBO rank/(N+1) + lambda<0; CPCV phi=C(N-1,k-1) + block Sharpes; DSR cross-trial V[{SR}]; drop incomplete month; one-way costs; reversal = latest month.
- P10: showcase blockers closed; Sonnet re-audit 100% GO (2026-07-11).
- P11: showcase assets redone to post-audit numbers (PDF + LinkedIn PNG + root README); committed and pushed.

## Current phase: complete
Goals: n/a
Done-when: n/a

## Decisions
- No scipy. 3 signals (pairs cut). Pass n_trials= for discarded configs; log has 9.
- CPCV: S=8, k=2 -> 28 combos, phi=7 paths; table median = combinatorial block Sharpes.
- PASS iff DSR>=0.95 and set PBO<=0.05.
- CSCV ranks by Sharpe (mean fallback only when subsample vol=0).
- Live Results = non-claim (survivorship); synth is the honest demo path.
- Post-audit live demo: momentum PASS, reversal FAIL, lowvol PASS (n_trials=3, PBO=0.041).

## Gotchas
- Current-constituent universe = survivorship; DSR/PBO do not fix look-ahead constituency
- Undercounted n_trials inflates DSR (esp. lowvol ~n=50)
- Fixed-rule CPCV paths collapse - do not sell path dispersion
- yfinance may lack Adj Close -> Close fallback
- Stale showcase PNGs/PDFs from pre-audit all-PASS tables must not be reused

## Key files
- `src/overfit_aware_signals/{data,signals,portfolio,backtest,analytics,cv,cpcv,stats,pbo,research,plotting,cli}.py`
- `README.md`, `results/`, `showcase/` (onepager PDF, LinkedIn PNG + post copy)
- this `PHASE-STATE.md`
