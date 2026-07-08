import hashlib
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


def fetch_prices(
    tickers: list[str],
    start: str,
    end: str | None = None,
    cache_dir: str | Path = "data_cache",
) -> pd.DataFrame:
    end = end or date.today().isoformat()
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = hashlib.sha1("|".join([*sorted(tickers), start, end]).encode()).hexdigest()[:16]
    cache_file = cache_dir / f"{key}.csv"

    if cache_file.exists():
        px = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        raw = yf.download(tickers, start=start, end=end)
        px = raw["Adj Close"] if "Adj Close" in raw.columns else raw["Close"]
        px = px.dropna(how="all")
        px.to_csv(cache_file)

    # ponytail: cache keyed on resolved end-date, so an open-ended (end=None) fetch
    # grows one file per calendar day it's run. Fine for research use; prune
    # data_cache/ by hand, or key on ticker-set only, if this matters later.
    return px.resample("ME").last()


def make_synthetic_prices(
    n_assets: int = 20,
    n_years: int = 15,
    seed: int = 42,
    annual_mu: float = 0.08,
    annual_sigma: float = 0.25,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n_periods = n_years * 12 + 1

    drifts = rng.normal(annual_mu, 0.05, n_assets)
    sigmas = rng.uniform(0.15, 0.40, n_assets)

    m_mean = drifts / 12 - sigmas**2 / 24
    m_std = sigmas / np.sqrt(12)

    log_rets = rng.normal(m_mean[:, None], m_std[:, None], size=(n_assets, n_periods - 1))

    prices = np.ones((n_assets, n_periods))
    prices[:, 1:] = np.cumprod(np.exp(log_rets), axis=1)

    dates = pd.date_range(start="2005-01-31", periods=n_periods, freq="ME")
    cols = [f"ASSET_{i:02d}" for i in range(n_assets)]
    return pd.DataFrame(prices.T, index=dates, columns=cols)
