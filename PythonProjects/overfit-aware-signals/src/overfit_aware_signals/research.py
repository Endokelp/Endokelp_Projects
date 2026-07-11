"""Research orchestration: evaluate signals, trial log, DSR sensitivity."""

import numpy as np
import pandas as pd

from .analytics import compute_metrics
from .backtest import run_backtest
from .config import BacktestConfig, CVConfig, SignalConfig
from .cpcv import CombinatorialPurgedCV, combinatorial_test_sharpes
from .pbo import probability_of_backtest_overfitting
from .signals import SIGNAL_REGISTRY
from .stats import deflated_sharpe_ratio

# Honest trial ledger for DSR. Undercounting inflates DSR (esp. lowvol).
# status: kept = in SIGNAL_REGISTRY; discarded = researched then cut.
RESEARCH_TRIAL_LOG: list[dict[str, str]] = [
    {"id": "momentum-12-1", "status": "kept", "note": "skip most recent month"},
    {"id": "momentum-6-1", "status": "discarded", "note": "shorter lookback grid"},
    {"id": "momentum-12-0", "status": "discarded", "note": "no skip-month variant"},
    {"id": "reversal-1m", "status": "kept", "note": "negative latest month"},
    {"id": "reversal-3m", "status": "discarded", "note": "3m reversal grid"},
    {"id": "lowvol-12m", "status": "kept", "note": "trailing realized vol"},
    {"id": "lowvol-6m", "status": "discarded", "note": "shorter vol window"},
    {"id": "lowvol-24m", "status": "discarded", "note": "longer vol window"},
    {"id": "pairs-statarb", "status": "discarded", "note": "cut; different eng surface"},
]


def logged_n_trials() -> int:
    return len(RESEARCH_TRIAL_LOG)


def signal_lookback(name: str, cfg: SignalConfig) -> int:
    if name == "reversal":
        return 1
    if name == "lowvol":
        return cfg.lowvol_window_months
    skip = 1 if cfg.skip_recent_month else 0
    return cfg.lookback_months + skip


def _period_sharpe(rets: pd.Series) -> float:
    std = float(rets.std())
    if std == 0.0:
        return 0.0
    return float(rets.mean() / std)


def dsr_sensitivity(
    period_sr: float,
    t: int,
    *,
    skew: float,
    kurt: float,
    var_sr: float,
    n_trials_grid: list[int] | None = None,
) -> pd.DataFrame:
    """DSR vs n_trials — shows how fragile a PASS is under undercounted trials."""
    grid = n_trials_grid or [3, 5, 10, 25, 50, 100]
    rows = []
    for n in grid:
        if n < 2:
            continue
        dsr = deflated_sharpe_ratio(
            period_sr, t, n, skew=skew, kurt=kurt, var_sr=var_sr
        )
        rows.append({"n_trials": n, "dsr": dsr, "pass_095": dsr >= 0.95})
    return pd.DataFrame(rows)


def evaluate_signals(
    prices: pd.DataFrame,
    signal_cfg: SignalConfig | None = None,
    backtest_cfg: BacktestConfig | None = None,
    cv_cfg: CVConfig | None = None,
    *,
    pbo_n_groups: int = 16,
    dsr_threshold: float = 0.95,
    pbo_threshold: float = 0.05,
    n_trials: int | None = None,
) -> pd.DataFrame:
    if prices.empty:
        raise ValueError("prices is empty")
    signal_cfg = signal_cfg or SignalConfig()
    backtest_cfg = backtest_cfg or BacktestConfig()
    cv_cfg = cv_cfg or CVConfig()

    # ponytail: default N = registry size. Pass n_trials=logged_n_trials() for
    # the research-log count; undercounting inflates DSR.
    n_trials = n_trials if n_trials is not None else len(SIGNAL_REGISTRY)
    if n_trials < 2:
        raise ValueError(f"n_trials must be >= 2, got {n_trials}")
    ppy = backtest_cfg.trading_periods_per_year
    rows: list[dict] = []
    ret_cols: dict[str, pd.Series] = {}
    period_srs: list[float] = []

    for name, fn in SIGNAL_REGISTRY.items():
        signals = fn(prices, signal_cfg)
        result = run_backtest(prices, signals, backtest_cfg)
        m = compute_metrics(result)
        rets = result.returns
        ret_cols[name] = rets

        cv = CombinatorialPurgedCV(
            n_groups=cv_cfg.n_groups,
            n_test_groups=cv_cfg.n_test_groups,
            lookback=signal_lookback(name, signal_cfg),
            embargo_pct=cv_cfg.embargo_pct,
        )
        # stability: Sharpe on each combinatorial held-out block set (not path φ)
        block = combinatorial_test_sharpes(rets.to_numpy(), cv, periods_per_year=ppy)
        median_block = float(np.nanmedian(block))

        sr = _period_sharpe(rets)
        period_srs.append(sr)
        skew = float(rets.skew())
        kurt = float(rets.kurt()) + 3.0
        t = len(rets)

        rows.append(
            {
                "signal": name,
                "sharpe": m.sharpe,
                "cagr": m.cagr,
                "ann_vol": m.annual_vol,
                "max_drawdown": m.max_drawdown,
                "n_months": m.n_months,
                "median_block_sharpe": median_block,
                "period_sr": sr,
                "skew": skew,
                "kurt": kurt,
                "t": t,
            }
        )

    # Bailey & López de Prado: V[{SR̂_n}] = cross-sectional variance across trials
    var_sr = float(np.var(period_srs, ddof=1)) if len(period_srs) > 1 else 0.0

    for row in rows:
        row["dsr"] = deflated_sharpe_ratio(
            row["period_sr"],
            row["t"],
            n_trials,
            skew=row["skew"],
            kurt=row["kurt"],
            var_sr=var_sr,
        )
        row["var_sr"] = var_sr

    # Align strategy returns on common dates for CSCV PBO (set-level)
    ret_mat = pd.DataFrame(ret_cols).dropna(how="any")
    pbo = probability_of_backtest_overfitting(ret_mat.to_numpy(), n_groups=pbo_n_groups)

    out_rows = []
    for row in rows:
        verdict = (
            "PASS"
            if row["dsr"] >= dsr_threshold and pbo <= pbo_threshold
            else "FAIL"
        )
        out_rows.append(
            {
                k: v
                for k, v in {**row, "pbo": pbo, "verdict": verdict, "n_trials": n_trials}.items()
                if k not in ("period_sr", "t", "skew", "kurt", "var_sr")
            }
        )

    return pd.DataFrame(out_rows)


def format_verdict_table(df: pd.DataFrame) -> str:
    cols = [
        "signal",
        "sharpe",
        "cagr",
        "median_block_sharpe",
        "dsr",
        "pbo",
        "verdict",
    ]
    show = df[cols].copy()
    for c in ("sharpe", "cagr", "median_block_sharpe", "dsr", "pbo"):
        show[c] = show[c].map(lambda x: f"{x:.3f}")
    return show.to_string(index=False)


def format_dsr_sensitivity(
    prices: pd.DataFrame,
    signal_cfg: SignalConfig | None = None,
    backtest_cfg: BacktestConfig | None = None,
    *,
    n_trials_grid: list[int] | None = None,
) -> str:
    """Print DSR vs n_trials for each signal (uses live period stats)."""
    signal_cfg = signal_cfg or SignalConfig()
    backtest_cfg = backtest_cfg or BacktestConfig()
    period_srs: list[float] = []
    meta: list[dict] = []
    for name, fn in SIGNAL_REGISTRY.items():
        rets = run_backtest(prices, fn(prices, signal_cfg), backtest_cfg).returns
        sr = _period_sharpe(rets)
        period_srs.append(sr)
        meta.append(
            {
                "signal": name,
                "period_sr": sr,
                "t": len(rets),
                "skew": float(rets.skew()),
                "kurt": float(rets.kurt()) + 3.0,
            }
        )
    var_sr = float(np.var(period_srs, ddof=1)) if len(period_srs) > 1 else 0.0
    lines = [
        f"DSR sensitivity (var_sr={var_sr:.6f}; research log n={logged_n_trials()}):",
    ]
    for m in meta:
        sens = dsr_sensitivity(
            m["period_sr"],
            m["t"],
            skew=m["skew"],
            kurt=m["kurt"],
            var_sr=var_sr,
            n_trials_grid=n_trials_grid,
        )
        cells = "  ".join(
            f"n={int(r.n_trials)}:{r.dsr:.3f}{'*' if r.pass_095 else ''}"
            for r in sens.itertuples()
        )
        lines.append(f"  {m['signal']}: {cells}")
    lines.append("  (* = DSR >= 0.95)")
    return "\n".join(lines)
