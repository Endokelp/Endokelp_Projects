import pandas as pd
import pytest

from overfit_aware_signals.config import SignalConfig
from overfit_aware_signals.signals import (
    SIGNAL_REGISTRY,
    compute_lowvol,
    compute_momentum,
    compute_reversal,
)


def test_momentum_values_by_hand(toy_prices_3x6):
    cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    sig = compute_momentum(toy_prices_3x6, cfg).iloc[3]
    assert sig["A"] == pytest.approx(0.20, rel=1e-9)
    assert sig["B"] == pytest.approx(-0.20, rel=1e-9)
    assert sig["C"] == pytest.approx(0.00, abs=1e-12)


def test_momentum_nan_for_insufficient_history(toy_prices_3x6):
    cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    sig = compute_momentum(toy_prices_3x6, cfg)
    assert sig.iloc[:3].isna().all(axis=None)
    assert sig.iloc[3:].notna().all(axis=None)


def test_momentum_ranking_correct(toy_prices_3x6):
    cfg = SignalConfig(lookback_months=2, skip_recent_month=True)
    sig = compute_momentum(toy_prices_3x6, cfg).iloc[3]
    assert sig["A"] > sig["C"] > sig["B"]


def test_momentum_invalid_lookback_raises(toy_prices_3x6):
    cfg = SignalConfig(lookback_months=0)
    with pytest.raises(ValueError, match="lookback"):
        compute_momentum(toy_prices_3x6, cfg)


def test_reversal_values_by_hand(toy_prices_3x6):
    cfg = SignalConfig()
    sig = compute_reversal(toy_prices_3x6, cfg).iloc[1]
    assert sig["A"] == pytest.approx(-(110.0 / 100.0 - 1), rel=1e-9)
    assert sig["B"] == pytest.approx(-(90.0 / 100.0 - 1), rel=1e-9)
    assert sig["C"] == pytest.approx(0.00, abs=1e-12)


def test_reversal_losers_score_highest(toy_prices_3x6):
    cfg = SignalConfig()
    sig = compute_reversal(toy_prices_3x6, cfg).iloc[1]
    # B lost value from index0->1 (recent loser) -> highest reversal score
    assert sig["B"] > sig["C"] > sig["A"]


def test_reversal_nan_before_two_periods(toy_prices_3x6):
    cfg = SignalConfig()
    sig = compute_reversal(toy_prices_3x6, cfg)
    assert sig.iloc[:1].isna().all(axis=None)
    assert sig.iloc[1:].notna().all(axis=None)


def test_lowvol_matches_pandas_composition(toy_prices_3x6):
    cfg = SignalConfig(lowvol_window_months=2)
    sig = compute_lowvol(toy_prices_3x6, cfg)
    expected = -toy_prices_3x6.pct_change().rolling(2).std()
    pd.testing.assert_frame_equal(sig, expected)


def test_lowvol_lower_vol_scores_higher(toy_prices_3x6):
    cfg = SignalConfig(lowvol_window_months=2)
    sig = compute_lowvol(toy_prices_3x6, cfg).iloc[2]
    # C is flat (zero vol) -> must outrank both trending assets
    assert sig["C"] > sig["A"]
    assert sig["C"] > sig["B"]


def test_lowvol_nan_before_window_filled(toy_prices_3x6):
    cfg = SignalConfig(lowvol_window_months=2)
    sig = compute_lowvol(toy_prices_3x6, cfg)
    assert sig.iloc[:2].isna().all(axis=None)
    assert sig.iloc[2:].notna().all(axis=None)


def test_registry_contains_all_three():
    assert set(SIGNAL_REGISTRY) == {"momentum", "reversal", "lowvol"}
    assert SIGNAL_REGISTRY["momentum"] is compute_momentum
    assert SIGNAL_REGISTRY["reversal"] is compute_reversal
    assert SIGNAL_REGISTRY["lowvol"] is compute_lowvol
