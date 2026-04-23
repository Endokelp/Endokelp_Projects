import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import yfinance as yf

from src.paths import MULTI_ASSET_DATA

# Multi-asset universe for extended MPT / HRP-style analysis
TICKERS = ["AAPL", "MSFT", "NVDA", "PG", "JNJ", "GLD", "TLT", "SPY"]
START_DATE = "2015-01-01"
END_DATE = "2025-01-01"


def main():
    print(f"Downloading 10-year data for: {', '.join(TICKERS)}...")

    raw_data = yf.download(TICKERS, start=START_DATE, end=END_DATE)

    if "Adj Close" in raw_data.columns:
        df = raw_data["Adj Close"]
    else:
        df = raw_data["Close"]

    df = df.dropna()
    returns = np.log(df / df.shift(1)).dropna()

    mu = returns.mean() * 252
    vol = returns.std() * np.sqrt(252)

    stats = pd.DataFrame(
        {
            "Average Annual Return": mu,
            "Annualized Volatility": vol,
            "Sharpe Ratio (Risk Free 2%)": (mu - 0.02) / vol,
        }
    )

    corr_matrix = returns.corr()
    cov_matrix = returns.cov() * 252

    output_path = str(MULTI_ASSET_DATA)
    os.makedirs(MULTI_ASSET_DATA.parent, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Price Data")
        returns.to_excel(writer, sheet_name="Log Returns")
        stats.to_excel(writer, sheet_name="Summary Stats")
        corr_matrix.to_excel(writer, sheet_name="Correlation Matrix")
        cov_matrix.to_excel(writer, sheet_name="Covariance Matrix")

    print(f"\nSuccessfully downloaded {len(df)} days of data.")
    print(f"Saved to: {output_path}")
    print("\n--- Asset Correlations ---")
    print(corr_matrix.round(2))


if __name__ == "__main__":
    main()
