import pandas as pd

def main():
    f1 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-29-27-671.csv'
    f2 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-33-45-408.csv'
    f3 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471.csv'
    
    df1 = pd.read_csv(f1)
    df2 = pd.read_csv(f2)
    df3 = pd.read_csv(f3)
    
    print("--- INDIVIDUAL FILES ---")
    print(f"{f1}: rows={len(df1)}")
    print(f"{f2}: rows={len(df2)}")
    print(f"{f3}: rows={len(df3)}")
    
    # 1. Check duplicates within each file by key (reviewerId, text, title)
    def count_internal_dupes(df, name):
        # We use a key of (reviewerId, text, title) since reviewId might be missing in df2
        key = df.apply(lambda r: (str(r.get('reviewerId', '')), str(r.get('text', '')), str(r.get('title', ''))), axis=1)
        dupes = key.duplicated().sum()
        print(f"Duplicates within {name}: {dupes}")
        
    count_internal_dupes(df1, "df1")
    count_internal_dupes(df2, "df2")
    count_internal_dupes(df3, "df3")

    # 2. Check duplicates across all three combined
    # Let's combine them
    # First, let's normalize column naming: 'stars' is rating, 'text' is review text, 'title' is location name
    # Let's see how they overlap
    df1['source_file'] = f1
    df2['source_file'] = f2
    df3['source_file'] = f3
    
    # Standardize columns
    common_cols = ['title', 'name', 'reviewerId', 'stars', 'text', 'publishedAtDate', 'source_file']
    
    # Add missing cols to df2 or others if needed
    # Let's check how many total unique reviews by (reviewerId, text, title)
    combined = pd.concat([df1[common_cols], df2[common_cols], df3[common_cols]], ignore_index=True)
    print("\n--- COMBINED RAW STATS ---")
    print(f"Total combined rows: {len(combined)}")
    
    key_combined = combined.apply(lambda r: (str(r.get('reviewerId', '')).strip(), str(r.get('text', '')).strip(), str(r.get('title', '')).strip()), axis=1)
    unique_count = key_combined.nunique()
    dupes_combined = key_combined.duplicated().sum()
    print(f"Unique reviews in combined: {unique_count}")
    print(f"Duplicate reviews in combined: {dupes_combined}")

if __name__ == '__main__':
    main()
