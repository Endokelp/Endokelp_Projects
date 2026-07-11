import pandas as pd

from overfit_aware_signals import data as oas_data


def test_synthetic_seed_reproducible():
    a = oas_data.make_synthetic_prices(n_assets=5, n_years=2, seed=7)
    b = oas_data.make_synthetic_prices(n_assets=5, n_years=2, seed=7)
    pd.testing.assert_frame_equal(a, b)


def test_synthetic_shape():
    a = oas_data.make_synthetic_prices(n_assets=5, n_years=2, seed=0)
    assert a.shape == (25, 5)  # n_years*12 + 1 rows
    assert list(a.columns) == [f"ASSET_{i:02d}" for i in range(5)]


def test_synthetic_starts_at_one():
    a = oas_data.make_synthetic_prices(n_assets=3, n_years=1, seed=0)
    assert (a.iloc[0] == 1.0).all()


def _fake_yf_frame(tickers, fields, value):
    idx = pd.date_range("2020-01-01", periods=5, freq="D")
    cols = pd.MultiIndex.from_product([fields, tickers])
    return pd.DataFrame(value, index=idx, columns=cols)


def test_fetch_prices_prefers_adj_close(tmp_path, monkeypatch):
    monkeypatch.setattr(
        oas_data.yf,
        "download",
        lambda *a, **k: _fake_yf_frame(["A", "B"], ["Adj Close", "Close"], 1.0),
    )
    px = oas_data.fetch_prices(["A", "B"], "2020-01-01", "2020-01-05", cache_dir=tmp_path)
    assert (px == 1.0).all(axis=None)


def test_fetch_prices_falls_back_to_close(tmp_path, monkeypatch):
    monkeypatch.setattr(
        oas_data.yf, "download", lambda *a, **k: _fake_yf_frame(["A", "B"], ["Close"], 2.0)
    )
    px = oas_data.fetch_prices(["A", "B"], "2020-01-01", "2020-01-05", cache_dir=tmp_path)
    assert (px == 2.0).all(axis=None)


def test_fetch_prices_uses_cache_on_second_call(tmp_path, monkeypatch):
    monkeypatch.setattr(
        oas_data.yf, "download", lambda *a, **k: _fake_yf_frame(["A", "B"], ["Close"], 3.0)
    )
    oas_data.fetch_prices(["A", "B"], "2020-01-01", "2020-01-05", cache_dir=tmp_path)

    def _boom(*a, **k):
        raise AssertionError("network hit on a cached call")

    monkeypatch.setattr(oas_data.yf, "download", _boom)
    px = oas_data.fetch_prices(["A", "B"], "2020-01-01", "2020-01-05", cache_dir=tmp_path)
    assert (px == 3.0).all(axis=None)


def test_fetch_prices_resamples_to_month_end(tmp_path, monkeypatch):
    monkeypatch.setattr(
        oas_data.yf, "download", lambda *a, **k: _fake_yf_frame(["A"], ["Close"], 5.0)
    )
    px = oas_data.fetch_prices(["A"], "2020-01-01", "2020-01-05", cache_dir=tmp_path)
    assert len(px) == 1
    assert px.index[0] == pd.Timestamp("2020-01-31")


def test_fetch_prices_drops_incomplete_trailing_month(tmp_path, monkeypatch):
    idx = pd.date_range("2020-01-01", periods=45, freq="D")  # into mid-Feb
    cols = pd.MultiIndex.from_product([["Close"], ["A"]])
    raw = pd.DataFrame(1.0, index=idx, columns=cols)

    monkeypatch.setattr(oas_data.yf, "download", lambda *a, **k: raw)
    px = oas_data.fetch_prices(
        ["A"], "2020-01-01", "2020-02-15", cache_dir=tmp_path
    )
    assert list(px.index) == [pd.Timestamp("2020-01-31")]
