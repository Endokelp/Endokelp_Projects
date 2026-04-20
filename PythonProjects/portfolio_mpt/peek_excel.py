import pandas as pd
import os

file_path = r'c:\Users\venni\MathIA\IA_Portfolio_Data.xlsx'

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
else:
    xls = pd.ExcelFile(file_path)
    print("Sheets found:", xls.sheet_names)
    
    for sheet_name in xls.sheet_names:
        print(f"\n--- Sheet: {sheet_name} ---")
        df = pd.read_excel(xls, sheet_name=sheet_name)
        print(df.head())
