import pandas as pd
import pytest

from momentum_backtest.signal import compute_momentum_signal


def test_signal_values_by_hand(toy_prices_3x6):
    """Signal at index 3 matches hand-computed values."""
    signals = compute_momentum_signal(toy_prices_3x6, lookback=2, skip=1)
    sig = signals.iloc[3]

    assert sig["A"] == pytest.approx(0.20, rel=1e-9)
    assert sig["B"] == pytest.approx(-0.20, rel=1e-9)
    assert sig["C"] == pytest.approx(0.00, abs=1e-12)


def test_signal_nan_for_insufficient_history(toy_prices_3x6):
    """First skip+lookback rows must be NaN; remainder must be finite."""
    signals = compute_momentum_signal(toy_prices_3x6, lookback=2, skip=1)

    assert signals.iloc[:3].isna().all(axis=None)
    assert signals.iloc[3:].notna().all(axis=None)


def test_signal_no_skip_uses_current_period(toy_prices_3x6):
    """With skip=0, first valid row is lookback=2, using price at that index."""
    signals = compute_momentum_signal(toy_prices_3x6, lookback=2, skip=0)
    # At index 2: prices[2] / prices[0] - 1
    sig = signals.iloc[2]
    assert sig["A"] == pytest.approx(0.20, rel=1e-9)


def test_signal_ranking_correct(toy_prices_3x6):
    """A > C > B at first valid date."""
    signals = compute_momentum_signal(toy_prices_3x6, lookback=2, skip=1)
    sig = signals.iloc[3]
    assert sig["A"] > sig["C"] > sig["B"]


def test_signal_invalid_skip_raises():
    prices = pd.DataFrame({"X": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="skip"):
        compute_momentum_signal(prices, lookback=1, skip=-1)


def test_signal_invalid_lookback_raises():
    prices = pd.DataFrame({"X": [1.0, 2.0, 3.0]})
    with pytest.raises(ValueError, match="lookback"):
        compute_momentum_signal(prices, lookback=0, skip=0)
