# overfit-aware-signals

Most backtests report one Sharpe and stop. That number is statistically
meaningless under multiple testing. This package evaluates three real
cross-sectional equity signals with the overfitting toolkit from primary
sources — combinatorial held-out block Sharpes, reconstructed CPCV paths,
the Deflated Sharpe Ratio (DSR), and Probability of Backtest Overfitting
(PBO) — and prints an honest per-signal pass/fail verdict.

**The verdict is the point, not a vanity Sharpe.**

## Results (live panel, Jul 2026 — **non-claim demo**)

> **Survivorship non-claim.** The live table uses *current* constituents, not a
> point-in-time universe. Absolute Sharpes are optimistic illustration only —
> **not** a deployment or alpha claim. Prefer the offline path:
> `python -m overfit_aware_signals synth`. DSR/PBO remain valid as
> *within-panel* multiple-testing filters on whatever return matrix you supply.

50 liquid US equities, monthly rebalance, `2005-01` → `2026-06` (incomplete
trailing month dropped), long-only top-5, **10 bps one-way per traded leg**.
DSR threshold ≥ 0.95; PBO threshold ≤ 0.05 (Bailey et al.). PBO is
**set-level** (same across rows). Table DSR uses `n_trials = 3` (registry
size). Research log has **9** configs (`python -m overfit_aware_signals trials`);
pass `--n-trials 9` or higher for honesty.

| signal   | Sharpe | CAGR  | median block Sharpe | DSR   | PBO   | verdict |
|----------|--------|-------|---------------------|-------|-------|---------|
| momentum | 0.921  | 0.183 | 0.925               | 0.999 | 0.041 | **PASS** |
| reversal | 0.453  | 0.081 | 0.526               | 0.860 | 0.041 | **FAIL** |
| lowvol   | 0.798  | 0.100 | 0.831               | 0.994 | 0.041 | **PASS** |

### DSR sensitivity to `n_trials` (same live panel)

Undercounting trials inflates DSR. Low-vol is fragile — around `n ≈ 50` it
loses the 0.95 gate while momentum usually holds longer. Reproduce with
`--sensitivity`:

```bash
python -m overfit_aware_signals run --sensitivity
```

| n_trials | momentum DSR | reversal DSR | lowvol DSR | lowvol ≥0.95? |
|----------|--------------|--------------|------------|---------------|
| 3        | ~0.999       | ~0.860       | ~0.994     | yes           |
| 9 (log)  | high         | fail         | high       | usually yes   |
| 25       | high         | fail         | borderline | fragile       |
| 50       | often holds  | fail         | **often no** | **fragile** |

Exact cells depend on the panel draw; the qualitative point is the gate.

Reproduce:

```bash
# preferred: offline demo (no live-equity claim)
python -m overfit_aware_signals synth --sensitivity

# live panel (prints NON-CLAIM banner)
python -m overfit_aware_signals run --plot-dir results --sensitivity
python -m overfit_aware_signals trials
```

Plots land in `results/` (`block_sharpe_*.png` + IS/OOS Sharpe-rank scatter).

### Caveats (read these)

- **Survivorship**: current constituents ≠ PIT panel. Treat absolute Sharpes as
  optimistic; DSR/PBO do not undo look-ahead universe construction.
- **Fixed-rule signals**: nothing is fitted inside CV folds. Reconstructed CPCV
  paths therefore collapse to the full-sample return series. `median_block_sharpe`
  is the median Sharpe across **combinatorial held-out blocks** (stability),
  not path φ. Purge/embargo matter when a model is trained on `train`.
- **Trial count**: default `n_trials = 3`. Research log = 9. Undercounting
  inflates DSR — pass `--n-trials` / `n_trials=` explicitly.
- **CSCV ranks by Sharpe** (not mean return), consistent with the DSR metric.
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
   (Eq. 2 of Bailey & López de Prado 2014); CSCV uses `ω = rank/(N+1)` and
   `PBO = P(λ < 0)`; CPCV path count is `φ = C(N-1, k-1)`.
   Hand-worked fixtures lock the math (SR=1, T=60, γ3=0, γ4=3; toy PBO=0 / PBO=1).
3. **Positioned against 2026 use, not 2018 tutorials.** Recent work gates
   LLM-generated / strategy-to-code trading systems with the same DSR and PBO
   checks (SysTradeBench, [arXiv:2604.04812](https://arxiv.org/abs/2604.04812);
   see also "The Alpha Illusion,"
   [arXiv:2605.16895](https://arxiv.org/abs/2605.16895)). The toolkit is a
   filter for claims — including machine-generated ones — not a museum piece.

## Quick start

```bash
pip install -e ".[dev]"

# offline demo (no network) — preferred showcase path
python -m overfit_aware_signals synth

# live universe (non-claim / survivorship-biased)
python -m overfit_aware_signals run

pytest -v
ruff check src/ tests/
```

## Signals

| name     | definition |
|----------|------------|
| momentum | 12-1 total return (skip most recent month): `P[t-1]/P[t-13]-1` |
| reversal | negative latest 1-month return at formation close |
| lowvol   | negative trailing 12-month realized vol through formation close |

Shared interface: `prices → cross-sectional score → rank → weights` via
`SIGNAL_REGISTRY`.

## Methodology (sourced)

- **Purged K-Fold + embargo** — López de Prado, *AFML* ch.7. Purge on the
  signal's *lookback window* overlap, not just label overlap. Relevant when
  fitting on `train`; unused by fixed-rule fold Sharpes.
- **CPCV** — `S=8` groups, `k=2` test → `C(8,2)=28` combinations and
  `φ = C(7,1)=7` reconstructed paths. Table median uses combinatorial
  **block** Sharpes (stability).
- **DSR** — Bailey & López de Prado (2014), *JPM* 40(5). `DSR ≡ PSR(SR₀)`
  with `SR₀` from the expected-max-Sharpe under `N` trials and
  **cross-trial** `V[{SR̂_n}]`. `γ4` is non-excess kurtosis (pandas `.kurt()` + 3).
- **PBO** — Bailey, Borwein, López de Prado & Zhu via CSCV. Split returns into
  `S` blocks, enumerate `C(S, S/2)` combos, rank strategies by **Sharpe** IS,
  take the OOS relative rank `ω = rank/(N+1)` of the IS-winner;
  `PBO = mean(λ < 0)`. Paper cutoff: reject if `PBO > 0.05`.

## Layout

```
src/overfit_aware_signals/
  config.py      SignalConfig, BacktestConfig, CVConfig, UniverseConfig
  data.py        yfinance fetch + synthetic panel (drops incomplete month)
  signals.py     momentum / reversal / lowvol + SIGNAL_REGISTRY
  portfolio.py   long-only / long-short weights
  backtest.py    monthly rebalance loop (one-way cost per traded leg)
  analytics.py   Sharpe, CAGR, vol, drawdown
  cv.py          PurgedKFold (lookback-aware purge + embargo)
  cpcv.py        CombinatorialPurgedCV + path φ + block Sharpes
  stats.py       PSR, expected_max_sharpe, DSR
  pbo.py         CSCV logits + PBO (Sharpe-ranked)
  research.py    evaluate_signals, trial log, DSR sensitivity
  plotting.py    block Sharpe hist, IS/OOS Sharpe-rank scatter
  cli.py         synth / run / trials
tests/           hand-worked fixtures for DSR and PBO extremes
```

## References

- Bailey, D. H., & López de Prado, M. (2014). The Deflated Sharpe Ratio.
  *Journal of Portfolio Management*, 40(5), 94–107.
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2014/2017).
  The Probability of Backtest Overfitting.
- López de Prado, M. *Advances in Financial Machine Learning*, ch.7.
- Chen et al. (2026). SysTradeBench: An Iterative Build–Test–Patch Benchmark
  for Strategy-to-Code Trading Systems.
  [arXiv:2604.04812](https://arxiv.org/abs/2604.04812) — DSR/PBO as robustness
  gates for LLM strategy-to-code systems.
- Ye et al. (2026). The Alpha Illusion: Reported Alpha from LLM Trading Agents
  Should Not Be Treated as Deployment Evidence.
  [arXiv:2605.16895](https://arxiv.org/abs/2605.16895).
