import yfinance as yf
import pandas as pd
import numpy as np
import os

# Define the multi-asset universe
TICKERS = ['AAPL', 'MSFT', 'NVDA', 'PG', 'JNJ', 'GLD', 'TLT', 'SPY']
START_DATE = '2015-01-01'
END_DATE = '2025-01-01'

def main():
    print(f"Downloading 10-year data for: {', '.join(TICKERS)}...")
    
    # 1. Download Adjusted Close Prices
    raw_data = yf.download(TICKERS, start=START_DATE, end=END_DATE)
    
    if 'Adj Close' in raw_data.columns:
        df = raw_data['Adj Close']
    else:
        df = raw_data['Close']
    
    # Drop rows with any NaN to ensure consistency across the backtest
    df = df.dropna()
    
    # 2. Calculate Daily Log Returns
    returns = np.log(df / df.shift(1)).dropna()
    
    # 3. Calculate Summary Statistics (Annualized)
    mu = returns.mean() * 252
    vol = returns.std() * np.sqrt(252)
    
    stats = pd.DataFrame({
        'Average Annual Return': mu,
        'Annualized Volatility': vol,
        'Sharpe Ratio (Risk Free 2%)': (mu - 0.02) / vol
    })
    
    # 4. Correlation and Covariance (Annualized)
    corr_matrix = returns.corr()
    cov_matrix = returns.cov() * 252
    
    # 5. Output to Excel for the dissertation engine
    output_path = r'c:\Users\venni\MathIA\Dissertation_Full_Data.xlsx'
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Price Data')
        returns.to_excel(writer, sheet_name='Log Returns')
        stats.to_excel(writer, sheet_name='Summary Stats')
        corr_matrix.to_excel(writer, sheet_name='Correlation Matrix')
        cov_matrix.to_excel(writer, sheet_name='Covariance Matrix')
        
    print(f"\nSuccessfully downloaded {len(df)} days of data.")
    print(f"Saved to: {output_path}")
    print("\n--- Asset Correlations ---")
    print(corr_matrix.round(2))

if __name__ == "__main__":
    main()
