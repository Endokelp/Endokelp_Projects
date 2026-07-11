import numpy as np
import pandas as pd
import pytest

from overfit_aware_signals.config import BacktestConfig, CVConfig, SignalConfig
from overfit_aware_signals.data import make_synthetic_prices
from overfit_aware_signals.research import evaluate_signals, format_verdict_table


def test_evaluate_signals_returns_one_row_per_signal():
    prices = make_synthetic_prices(n_assets=12, n_years=8, seed=7)
    df = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
    )
    assert list(df["signal"]) == ["momentum", "reversal", "lowvol"]
    assert set(df["verdict"]).issubset({"PASS", "FAIL"})


def test_evaluate_signals_metrics_finite():
    prices = make_synthetic_prices(n_assets=12, n_years=8, seed=11)
    df = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
    )
    for col in ("sharpe", "cagr", "dsr", "pbo", "median_block_sharpe"):
        assert np.isfinite(df[col]).all()
    assert ((df["dsr"] >= 0.0) & (df["dsr"] <= 1.0)).all()
    assert ((df["pbo"] >= 0.0) & (df["pbo"] <= 1.0)).all()
    # PBO is a property of the strategy set — same across rows
    assert df["pbo"].nunique() == 1


def test_verdict_pass_fail_thresholds():
    prices = make_synthetic_prices(n_assets=10, n_years=6, seed=3)
    df = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
        dsr_threshold=0.0,
        pbo_threshold=1.0,
    )
    assert (df["verdict"] == "PASS").all()

    df_fail = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
        dsr_threshold=1.01,
        pbo_threshold=0.0,
    )
    assert (df_fail["verdict"] == "FAIL").all()


def test_format_verdict_table_contains_signals():
    prices = make_synthetic_prices(n_assets=10, n_years=6, seed=1)
    df = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
    )
    text = format_verdict_table(df)
    assert "momentum" in text
    assert "PASS" in text or "FAIL" in text


def test_evaluate_signals_rejects_empty_prices():
    with pytest.raises(ValueError, match="empty"):
        evaluate_signals(
            pd.DataFrame(),
            SignalConfig(),
            BacktestConfig(),
            CVConfig(),
        )


def test_evaluate_signals_uses_cross_trial_var_for_dsr():
    prices = make_synthetic_prices(n_assets=12, n_years=8, seed=7)
    df = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
    )
    df2 = evaluate_signals(
        prices,
        SignalConfig(),
        BacktestConfig(n_longs=3, cost_bps=0.0),
        CVConfig(n_groups=4, n_test_groups=1, embargo_pct=0.0),
        pbo_n_groups=4,
        n_trials=20,
    )
    assert (df2["dsr"] <= df["dsr"] + 1e-12).all()


def test_logged_n_trials_covers_research_log():
    from overfit_aware_signals.research import RESEARCH_TRIAL_LOG, logged_n_trials

    assert logged_n_trials() == len(RESEARCH_TRIAL_LOG)
    assert logged_n_trials() >= 3
    statuses = {r["status"] for r in RESEARCH_TRIAL_LOG}
    assert statuses == {"kept", "discarded"}


def test_dsr_sensitivity_declines_with_n_trials():
    from overfit_aware_signals.research import dsr_sensitivity

    sens = dsr_sensitivity(
        0.25, 200, skew=0.0, kurt=3.0, var_sr=0.01, n_trials_grid=[3, 50]
    )
    assert float(sens.loc[sens["n_trials"] == 50, "dsr"].iloc[0]) <= float(
        sens.loc[sens["n_trials"] == 3, "dsr"].iloc[0]
    ) + 1e-12
