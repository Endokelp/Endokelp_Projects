import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
import yfinance as yf

from src.paths import IA_DATA

# Define stocks and timeframe
STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'PLTR']
START_DATE = '2020-01-01'
END_DATE = '2025-01-01'

def main():
    print(f"Downloading data for: {', '.join(STOCKS)}...")
    
    # 1. Download Adjusted Close Prices
    # In newer yfinance, we use 'Close' or explicitly check for 'Adj Close'
    raw_data = yf.download(STOCKS, start=START_DATE, end=END_DATE)
    
    # Check if 'Adj Close' exists, otherwise use 'Close'
    if 'Adj Close' in raw_data.columns:
        data = raw_data['Adj Close']
    else:
        data = raw_data['Close']
    
    # Handle potential missing data (PLTR IPO was late 2020)
    # We will truncate the start date to when all stocks have data for a balanced panel
    data = data.dropna()
    
    # 2. Daily Log Returns
    # Formula: ln(P_t / P_{t-1})
    returns = np.log(data / data.shift(1)).dropna()
    
    # 3. Summary Statistics (Annualized)
    # Mean returns * 252 trading days
    mu = returns.mean() * 252
    # Standard deviation (Volatility) * sqrt(252)
    vol = returns.std() * np.sqrt(252)
    
    stats = pd.DataFrame({
        'Annualized Mean Return': mu,
        'Annualized Volatility (Risk)': vol
    })
    
    # 4. Covariance Matrix (Annualized)
    cov_matrix = returns.cov() * 252
    
    # 5. Output to Excel
    output_path = str(IA_DATA)
    os.makedirs(IA_DATA.parent, exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name='Raw Prices')
        returns.to_excel(writer, sheet_name='Daily Returns')
        stats.to_excel(writer, sheet_name='Summary Stats')
        cov_matrix.to_excel(writer, sheet_name='Covariance Matrix')
        
        # Auto-adjust column widths for all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
    print("\n--- Summary Stats ---")
    print(stats)
    print("\n--- Covariance Matrix ---")
    print(cov_matrix)
    print(f"\nSuccessfully created: {output_path}")

if __name__ == "__main__":
    main()
