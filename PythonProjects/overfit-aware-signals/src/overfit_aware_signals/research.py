import numpy as np
import pandas as pd

from .analytics import compute_metrics
from .backtest import run_backtest
from .config import BacktestConfig, CVConfig, SignalConfig
from .cpcv import CombinatorialPurgedCV, oos_sharpe_distribution
from .pbo import probability_of_backtest_overfitting
from .signals import SIGNAL_REGISTRY
from .stats import deflated_sharpe_ratio


def signal_lookback(name: str, cfg: SignalConfig) -> int:
    if name == "reversal":
        return 2
    if name == "lowvol":
        return cfg.lowvol_window_months
    skip = 1 if cfg.skip_recent_month else 0
    return cfg.lookback_months + skip


def _period_sharpe(rets: pd.Series) -> float:
    std = float(rets.std())
    if std == 0.0:
        return 0.0
    return float(rets.mean() / std)


def _var_sr(sr: float, t: int, skew: float, kurt: float) -> float:
    # Bailey & López de Prado: Var(SR̂) ≈ (1 − γ3 SR + ((γ4−1)/4) SR²) / (T−1)
    return (1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr) / (t - 1)


def evaluate_signals(
    prices: pd.DataFrame,
    signal_cfg: SignalConfig | None = None,
    backtest_cfg: BacktestConfig | None = None,
    cv_cfg: CVConfig | None = None,
    *,
    pbo_n_groups: int = 16,
    dsr_threshold: float = 0.95,
    pbo_threshold: float = 0.05,
) -> pd.DataFrame:
    if prices.empty:
        raise ValueError("prices is empty")
    signal_cfg = signal_cfg or SignalConfig()
    backtest_cfg = backtest_cfg or BacktestConfig()
    cv_cfg = cv_cfg or CVConfig()

    n_trials = len(SIGNAL_REGISTRY)
    ppy = backtest_cfg.trading_periods_per_year
    rows: list[dict] = []
    ret_cols: dict[str, pd.Series] = {}

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
        oos = oos_sharpe_distribution(rets.to_numpy(), cv, periods_per_year=ppy)
        median_oos = float(np.nanmedian(oos))

        # DSR uses non-annualized SR + γ4 (pandas kurt is excess → +3)
        sr = _period_sharpe(rets)
        skew = float(rets.skew())
        kurt = float(rets.kurt()) + 3.0
        t = len(rets)
        dsr = deflated_sharpe_ratio(
            sr,
            t,
            n_trials,
            skew=skew,
            kurt=kurt,
            var_sr=_var_sr(sr, t, skew, kurt),
        )

        rows.append(
            {
                "signal": name,
                "sharpe": m.sharpe,
                "cagr": m.cagr,
                "ann_vol": m.annual_vol,
                "max_drawdown": m.max_drawdown,
                "n_months": m.n_months,
                "median_oos_sharpe": median_oos,
                "dsr": dsr,
                "skew": skew,
                "kurt": kurt,
            }
        )

    # Align strategy returns on common dates for CSCV PBO
    ret_mat = pd.DataFrame(ret_cols).dropna(how="any")
    pbo = probability_of_backtest_overfitting(ret_mat.to_numpy(), n_groups=pbo_n_groups)

    out_rows = []
    for row in rows:
        verdict = (
            "PASS"
            if row["dsr"] >= dsr_threshold and pbo <= pbo_threshold
            else "FAIL"
        )
        out_rows.append({**row, "pbo": pbo, "verdict": verdict})

    return pd.DataFrame(out_rows)


def format_verdict_table(df: pd.DataFrame) -> str:
    cols = [
        "signal",
        "sharpe",
        "cagr",
        "median_oos_sharpe",
        "dsr",
        "pbo",
        "verdict",
    ]
    show = df[cols].copy()
    for c in ("sharpe", "cagr", "median_oos_sharpe", "dsr", "pbo"):
        show[c] = show[c].map(lambda x: f"{x:.3f}")
    return show.to_string(index=False)
