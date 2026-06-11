import pandas as pd

def main():
    f1 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-29-27-671.csv'
    f2 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-33-45-408.csv'
    f3 = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471.csv'
    
    # Load new scraper data
    df1 = pd.read_csv(f1)
    df2 = pd.read_csv(f2)
    df3 = pd.read_csv(f3)
    
    # Standardize column naming
    df1['source_file'] = f1
    df2['source_file'] = f2
    df3['source_file'] = f3
    
    common_cols = ['title', 'name', 'reviewerId', 'stars', 'text', 'publishedAtDate', 'source_file']
    combined = pd.concat([df1[common_cols], df2[common_cols], df3[common_cols]], ignore_index=True)
    
    # Create matching key
    new_keys = set(combined.apply(lambda r: (str(r.get('reviewerId', '')).strip(), str(r.get('text', '')).strip()), axis=1))
    print(f"Total new reviews key-set size: {len(new_keys)}")
    
    # Load Master Reviews Enriched
    master_path = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
    df_master = pd.read_csv(master_path)
    print(f"Master Reviews Enriched size: {len(df_master)}")
    
    master_keys = set(df_master.apply(lambda r: (str(r.get('reviewerId', '')).strip(), str(r.get('review_text', '')).strip()), axis=1))
    
    overlap = new_keys.intersection(master_keys)
    print(f"Overlap with Master Reviews Enriched: {len(overlap)}")
    
    # Also check Master Reviews Labeled Binary
    binary_path = 'Dataset/MASTER_REVIEWS_LABELED_BINARY.csv'
    df_binary = pd.read_csv(binary_path)
    print(f"Master Reviews Labeled Binary size: {len(df_binary)}")
    
    binary_keys = set(df_binary.apply(lambda r: (str(r.get('reviewerId', '')).strip(), str(r.get('review_text', '')).strip()), axis=1))
    overlap_binary = new_keys.intersection(binary_keys)
    print(f"Overlap with Master Reviews Labeled Binary: {len(overlap_binary)}")

if __name__ == '__main__':
    main()
