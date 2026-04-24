import numpy as np
import pandas as pd
import pytest

from volatility_targeting.vol import ewma_vol, rolling_vol


def _const(val=0.01, n=100):
    return pd.Series([val] * n)


def test_rolling_vol_constant_returns_is_zero():
    w = 20
    s = _const(0.01, 100)
    result = rolling_vol(s, window=w, annualize=False)
    assert result.iloc[:w - 1].isna().all()
    assert (result.tail(5) == 0.0).all()


def test_rolling_vol_annualization():
    rng = np.random.default_rng(42)
    s = pd.Series(rng.normal(0, 0.01, 500))
    daily_std = s.rolling(20).std().dropna().iloc[-1]
    ann = rolling_vol(s, window=20, annualize=True).dropna().iloc[-1]
    assert abs(ann - daily_std * np.sqrt(252)) < 1e-9


def test_ewma_vol_produces_series():
    s = pd.Series(np.random.default_rng(1).normal(0, 0.01, 60))
    result = ewma_vol(s)
    assert isinstance(result, pd.Series)
    assert len(result) == len(s)
    assert result.name == "vol_ewma"
    assert result.iloc[5:].notna().all()


def test_ewma_matches_rolling_limit():
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(0, 0.01, 5000))
    hl = 1000
    roll = rolling_vol(s, window=hl, annualize=False).dropna()
    ewma = ewma_vol(s, halflife=hl, annualize=False)
    tail_roll = roll.tail(500).mean()
    tail_ewma = ewma.iloc[-500:].mean()
    assert abs(tail_ewma - tail_roll) / tail_roll < 0.05


def test_empty_raises():
    empty = pd.Series([], dtype=float)
    with pytest.raises(ValueError):
        rolling_vol(empty)
    with pytest.raises(ValueError):
        ewma_vol(empty)


def test_annualize_false_returns_daily():
    rng = np.random.default_rng(7)
    s = pd.Series(rng.normal(0, 0.01, 200))
    daily_std = s.rolling(20).std().dropna().iloc[-1]
    result = rolling_vol(s, window=20, annualize=False).dropna().iloc[-1]
    assert abs(result - daily_std) < 1e-9
