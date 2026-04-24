from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from volatility_targeting.data import load_returns, synthetic_returns

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_returns.csv"


def test_synthetic_seed_reproducible():
    a = synthetic_returns(seed=7)
    b = synthetic_returns(seed=7)
    pd.testing.assert_series_equal(a, b)


def test_synthetic_respects_n_days():
    assert len(synthetic_returns(n_days=100)) == 100


def test_synthetic_annualized_stats_roughly_match():
    r = synthetic_returns(n_days=5000, seed=0, mu=0.1, sigma=0.2)
    ann_mean = r.mean() * 252
    ann_std = r.std() * np.sqrt(252)
    assert abs(ann_mean - 0.1) < 0.05
    assert abs(ann_std - 0.2) < 0.02


def test_missing_data_handled():
    lines = [ln for ln in FIXTURE.read_text().splitlines() if ln.strip()]
    csv_rows = len(lines) - 1  # minus header
    with pytest.warns(UserWarning):
        r = load_returns(FIXTURE)
    assert r.isna().sum() == 0
    assert len(r) == csv_rows - 1


def test_load_sorts_and_dedupes(tmp_path):
    p = tmp_path / "test.csv"
    p.write_text("date,ret\n2024-01-05,0.01\n2024-01-03,0.02\n2024-01-03,0.99\n2024-01-04,0.03\n")
    r = load_returns(p)
    assert r.index.is_monotonic_increasing
    assert r["2024-01-03"] == pytest.approx(0.99)


def test_load_accepts_str_and_path():
    r_str = load_returns(str(FIXTURE))
    r_path = load_returns(FIXTURE)
    pd.testing.assert_series_equal(r_str, r_path)
