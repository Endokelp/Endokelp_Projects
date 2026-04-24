from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from volatility_targeting.vol import ewma_vol, rolling_vol


@dataclass(frozen=True)
class VolTargetConfig:
    target_vol: float = 0.10
    method: Literal["rolling", "ewma"] = "rolling"
    window: int = 20
    halflife: float = 20.0
    lag: int = 1
    leverage_cap: float = 3.0
    leverage_floor: float = 0.0
    periods_per_year: int = 252
    min_vol_floor: float = 1e-6


@dataclass
class VolTargetResult:
    est_vol: pd.Series
    raw_scale: pd.Series
    scale: pd.Series
    scaled_returns: pd.Series
    config: VolTargetConfig

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame({
            "est_vol": self.est_vol,
            "raw_scale": self.raw_scale,
            "scale": self.scale,
            "scaled_returns": self.scaled_returns,
            "raw_returns": self.scaled_returns / self.scale.replace(0, float("nan")),
        })


class VolTargeter:
    # TODO: support custom vol function injection

    def __init__(self, config: VolTargetConfig | None = None):
        self.config = config or VolTargetConfig()

    def fit(self, returns: pd.Series) -> VolTargetResult:
        cfg = self.config
        r = returns

        if cfg.method == "ewma":
            ev = ewma_vol(r, halflife=cfg.halflife, periods_per_year=cfg.periods_per_year)
        else:
            ev = rolling_vol(r, window=cfg.window, periods_per_year=cfg.periods_per_year)

        rs = (cfg.target_vol / ev.clip(lower=cfg.min_vol_floor)).rename("raw_scale")
        s = rs.clip(lower=cfg.leverage_floor, upper=cfg.leverage_cap)
        # no lookahead: use est_vol known at close of t-lag to scale returns at t
        s = s.shift(cfg.lag).rename("scale")
        ret_scaled = (s * r).rename("ret_scaled")

        return VolTargetResult(
            est_vol=ev,
            raw_scale=rs,
            scale=s,
            scaled_returns=ret_scaled,
            config=cfg,
        )
