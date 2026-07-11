# overfit-aware-signals

Most backtests report one Sharpe and stop. That number is statistically
meaningless under multiple testing. This package evaluates three real
cross-sectional equity signals with the overfitting toolkit from primary
sources — purged CV, combinatorial purged CV (CPCV), the Deflated Sharpe
Ratio (DSR), and Probability of Backtest Overfitting (PBO) — and prints an
honest per-signal pass/fail verdict.

**The verdict is the point, not a vanity Sharpe.**

## Results (live universe, Jul 2026)

50 liquid US equities, monthly rebalance, `2005-01` → `2026-07`, long-only
top-5, 10 bps one-way costs. DSR threshold ≥ 0.95; PBO threshold ≤ 0.05
(Bailey et al.). PBO is set-level (same across rows); `n_trials = 3`.

| signal   | Sharpe | CAGR  | median OOS Sharpe | DSR   | PBO   | verdict |
|----------|--------|-------|-------------------|-------|-------|---------|
| momentum | 0.937  | 0.187 | 1.039             | 0.999 | 0.031 | **PASS** |
| reversal | 0.808  | 0.186 | 0.882             | 0.998 | 0.031 | **PASS** |
| lowvol   | 0.816  | 0.103 | 0.836             | 0.995 | 0.031 | **PASS** |

Reproduce:

```bash
python -m overfit_aware_signals run --plot-dir results
```

Plots land in `results/` (OOS Sharpe histograms + IS-vs-OOS rank scatter).

### Caveats (read these)

- **Survivorship**: the universe is *current* constituents, not a point-in-time
  survivorship-bias-free panel. Survivors of 2005–2026 look better than a
  true historical cross-section would. Treat absolute Sharpes as optimistic;
  the DSR/PBO machinery is still valid for ranking and multiple-testing
  correction *within* this panel.
- **Not trading advice.** Research code for evaluating statistical claims.
- A pairs/stat-arb signal was considered and cut for v1 (different engineering
  surface: pair selection, hedge ratios, spread sizing).

## Why this isn't just another AFML clone

Implementing CPCV/DSR/PBO as a portfolio piece is no longer rare — the
AFML overfitting toolkit is baseline knowledge by 2026, not a differentiator.
What this package emphasizes instead:

1. **Honest per-signal verdict as the centerpiece.** Each signal gets PASS
   or FAIL under fixed thresholds (`DSR ≥ 0.95` and set-level `PBO ≤ 0.05`),
   not a buried footnote under a big Sharpe chart.
2. **Primary-source formulas, no scipy.** PSR/DSR use `statistics.NormalDist`
   (Eq. 2 of Bailey & López de Prado 2014); CSCV uses `itertools.combinations`.
   Hand-worked fixtures lock the math (SR=1, T=60, γ3=0, γ4=3; toy PBO=0 / PBO=1).
3. **Positioned against 2026 use, not 2018 tutorials.** Recent work gates
   LLM-generated / strategy-to-code trading systems with the same DSR and PBO
   checks (e.g. SysTradeBench, arXiv:2604.04812; see also "The Alpha Illusion,"
   arXiv:2605.16895). The toolkit is a filter for claims — including
   machine-generated ones — not a museum piece.

## Quick start

```bash
pip install -e ".[dev]"

# offline demo (no network)
python -m overfit_aware_signals synth

# live universe
python -m overfit_aware_signals run

pytest -v
ruff check src/ tests/
```

## Signals

| name     | definition |
|----------|------------|
| momentum | 12-1 total return (skip most recent month) |
| reversal | negative 1-month return |
| lowvol   | negative trailing 12-month realized vol |

Shared interface: `prices → cross-sectional score → rank → weights` via
`SIGNAL_REGISTRY`.

## Methodology (sourced)

- **Purged K-Fold + embargo** — López de Prado, *AFML* ch.7. Purge on the
  signal's *lookback window* overlap, not just label overlap.
- **CPCV** — `S=8` groups, `k=2` test → `C(8,2)=28` OOS Sharpe paths.
- **DSR** — Bailey & López de Prado (2014), *JPM* 40(5). `DSR ≡ PSR(SR₀)`
  with `SR₀` from the expected-max-Sharpe under `N` trials.
  `γ4` is non-excess kurtosis (pandas `.kurt()` + 3).
- **PBO** — Bailey, Borwein, López de Prado & Zhu via CSCV. Split returns into
  `S` blocks, enumerate `C(S, S/2)` combos, rank strategies IS, take the OOS
  relative rank of the IS-winner; `PBO = mean(λ ≤ 0)`. Paper cutoff: reject
  if `PBO > 0.05`.

## Layout

```
src/overfit_aware_signals/
  config.py      SignalConfig, BacktestConfig, CVConfig, UniverseConfig
  data.py        yfinance fetch + synthetic panel
  signals.py     momentum / reversal / lowvol + SIGNAL_REGISTRY
  portfolio.py   long-only / long-short weights
  backtest.py    monthly rebalance loop
  analytics.py   Sharpe, CAGR, vol, drawdown
  cv.py          PurgedKFold (lookback-aware purge + embargo)
  cpcv.py        CombinatorialPurgedCV + OOS Sharpe distribution
  stats.py       PSR, expected_max_sharpe, DSR
  pbo.py         CSCV logits + PBO
  research.py    evaluate_signals → verdict table
  plotting.py    OOS Sharpe hist, IS/OOS rank scatter
  cli.py         synth / run
tests/           hand-worked fixtures for DSR and PBO extremes
```

## References

- Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio.
  *Journal of Portfolio Management*, 40(5), 94–107.
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2014/2017).
  The Probability of Backtest Overfitting.
- López de Prado, M. *Advances in Financial Machine Learning*, ch.7.
- SysTradeBench (2026). arXiv:2604.04812 — DSR/PBO as robustness gates for
  LLM strategy-to-code systems.
- The Alpha Illusion (2026). arXiv:2605.16895 — reported LLM-agent alpha is
  not deployment evidence without structural validity tests.
