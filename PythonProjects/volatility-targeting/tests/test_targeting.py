import numpy as np
import pandas as pd

from volatility_targeting.data import synthetic_returns
from volatility_targeting.targeting import VolTargetConfig, VolTargeter


def _make_returns(values, start="2020-01-02"):
    idx = pd.bdate_range(start=start, periods=len(values))
    return pd.Series(values, index=idx, name="ret")


def test_no_lookahead():
    rng = np.random.default_rng(0)
    low_vol = rng.normal(0, 0.001, 60)
    high_vol = rng.normal(0, 0.05, 200)
    r = _make_returns(np.concatenate([low_vol, high_vol]))

    cfg = VolTargetConfig(window=20, lag=1, method="rolling", leverage_cap=3.0)
    result = VolTargeter(cfg).fit(r)

    # at index 60 the scale is based on the low-vol window (lagged) — pegged at cap
    assert result.scale.iloc[60] == cfg.leverage_cap
    # once the high-vol window fills, leverage collapses below the cap
    assert result.scale.iloc[60] > result.scale.iloc[70]


def test_cap_and_floor_applied():
    r = _make_returns([0.0] * 100)
    cfg = VolTargetConfig(leverage_cap=3.0, leverage_floor=0.0)
    result = VolTargeter(cfg).fit(r)
    valid = result.scale.dropna()
    assert valid.max() <= cfg.leverage_cap + 1e-12
    assert valid.min() >= cfg.leverage_floor - 1e-12


def test_identity_when_returns_already_at_target():
    r = synthetic_returns(n_days=5000, mu=0.0, sigma=0.10, seed=0)
    cfg = VolTargetConfig(target_vol=0.10, method="rolling", window=20)
    result = VolTargeter(cfg).fit(r)
    mean_scale = result.scale.dropna().mean()
    assert abs(mean_scale - 1.0) < 0.15


def test_to_frame_columns():
    r = synthetic_returns(n_days=500)
    result = VolTargeter().fit(r)
    df = result.to_frame()
    assert list(df.columns) == ["est_vol", "raw_scale", "scale", "scaled_returns", "raw_returns"]


def test_ewma_method_runs():
    r = synthetic_returns(n_days=300)
    cfg = VolTargetConfig(method="ewma", halflife=20.0)
    result = VolTargeter(cfg).fit(r)
    assert not result.scaled_returns.dropna().empty
