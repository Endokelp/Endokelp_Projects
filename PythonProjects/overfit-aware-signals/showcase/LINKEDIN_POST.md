# LinkedIn post (copy/paste)

Attach: `showcase/linkedin-verdict.png`

---

Most backtests stop at one Sharpe ratio.

That number is easy to inflate once you try a few ideas. I built a small Python research package that treats the Sharpe as a claim to test, not a trophy.

Overfit-Aware Signals runs three real cross-sectional equity factors (12-1 momentum, one-month reversal, low-vol) through purged CV, combinatorial purged CV, the Deflated Sharpe Ratio (Bailey and Lopez de Prado, 2014), and Probability of Backtest Overfitting via CSCV. Each signal gets a hard PASS or FAIL under fixed gates (DSR >= 0.95, set-level PBO <= 0.05).

On a live 50-name panel demo, reversal fails. Momentum and low-vol pass. That is the point. The package is willing to reject a signal.

Important caveat: the live panel uses current constituents, so absolute Sharpes are optimistic and not an alpha claim. Prefer the offline synth path for demos. DSR and PBO still work as within-panel multiple-testing filters.

Code and one-pager:
https://github.com/Endokelp/Endokelp_Projects/tree/main/PythonProjects/overfit-aware-signals

Not trading advice.

#quant #systematictrading #python #research
