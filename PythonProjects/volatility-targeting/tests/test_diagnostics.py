import pandas as pd

from volatility_targeting.diagnostics import max_drawdown, summary_stats, turnover_proxy


def test_drawdown_zero_returns():
    assert max_drawdown(pd.Series([0.0] * 100)) == 0.0


def test_drawdown_constant_negative():
    r = pd.Series([-0.01] * 100)
    dd = max_drawdown(r)
    expected = (0.99**100) - 1
    assert dd < 0.0
    assert abs(dd - expected) < 1e-9


def test_sharpe_zero_vol_safe():
    stats = summary_stats(pd.Series([0.0] * 50))
    assert stats["sharpe"] == 0.0


def test_summary_stats_keys():
    stats = summary_stats(pd.Series([0.01, -0.01] * 50))
    expected_keys = {"mean_ann", "vol_ann", "sharpe", "max_drawdown", "skew", "kurtosis", "n_obs"}
    assert set(stats.keys()) == expected_keys


def test_turnover_proxy_basic():
    s = pd.Series([1.0, 1.5, 1.5, 2.0])
    expected = (0.5 + 0.0 + 0.5) / 3
    assert abs(turnover_proxy(s) - expected) < 1e-12


def test_turnover_proxy_empty_safe():
    assert turnover_proxy(pd.Series([], dtype=float)) == 0.0
