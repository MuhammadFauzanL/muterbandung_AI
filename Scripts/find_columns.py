import pandas as pd
import glob
import os

def main():
    paths = glob.glob('*.csv') + glob.glob('Dataset/*.csv')
    for p in paths:
        try:
            df = pd.read_csv(p, nrows=1)
            # Find matching column names
            matching = [c for c in df.columns if 'deskripsi' in c.lower() or 'google' in c.lower()]
            print(f"File: {p}")
            print(f"  All Columns: {df.columns.tolist()[:10]}...")
            print(f"  Matching Columns: {matching}")
        except Exception as e:
            print(f"Error reading {p}: {e}")

if __name__ == '__main__':
    main()
