import pandas as pd

def main():
    files = [
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_13-14-48-667.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-29-27-671.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-33-45-408.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471.csv'
    ]
    
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        df['source_file'] = f
        # Standardize columns: rating is 'stars', location name is 'title', text is 'text'
        # If 'stars' column not in columns, search for others
        # Note that df1, df3, df4 have 'stars', let's check
        dfs.append(df)
        print(f"{f}: shape={df.shape}")
        
    # Combine them
    # Let's map name discrepancies first:
    # 1. 'Inggit Garnasih Historic House' -> 'Museum Inggit Garnasih'
    # 2. 'Kampung Wisata Pangjugjugan' -> 'Pangjugjugan Sumedang'
    # 3. 'Kawasan Konservasi Taman Buru G. Masigit Kareumbi' -> 'Taman Buru Gunung Masigit Kareumbi'
    # 4. 'Kebun Teh Malabar' -> 'Perkebunan Teh Malabar'
    # 5. 'Kolam Renang Karang Setra' -> 'Karang Setra Waterland'
    # 6. 'MUARA RAHONG HILL'S' -> 'Muara Rahong Hills'
    # 7. 'Nu Art Studio' -> 'NuArt Sculpture Park'
    # 8. 'Palayangan River' -> 'Sungai Palayangan Rafting'
    # 9. 'Southland Camp' -> 'Southland Camp Ciwidey'
    
    mapping = {
        'inggit garnasih historic house': 'Museum Inggit Garnasih',
        'kampung wisata pangjugjugan': 'Pangjugjugan Sumedang',
        'kawasan konservasi taman buru g. masigit kareumbi': 'Taman Buru Gunung Masigit Kareumbi',
        'kebun teh malabar': 'Perkebunan Teh Malabar',
        'kolam renang karang setra': 'Karang Setra Waterland',
        "muara rahong hill's": 'Muara Rahong Hills',
        'nu art studio': 'NuArt Sculpture Park',
        'palayangan river': 'Sungai Palayangan Rafting',
        'southland camp': 'Southland Camp Ciwidey'
    }
    
    # We will build a unified df with key columns
    unified_rows = []
    for df in dfs:
        for idx, row in df.iterrows():
            title = str(row.get('title', '')).strip()
            # Clean title
            title_lower = title.lower()
            if title_lower in mapping:
                title = mapping[title_lower]
            elif title_lower == 'toko goberz audio mobil 97':
                continue # Outlier! Skip!
                
            reviewer_name = str(row.get('name', '')).strip()
            # Handle rating column ('stars')
            rating = row.get('stars')
            if pd.isna(rating):
                rating = row.get('rating') # fallback if rating col exists
            
            review_text = str(row.get('text', '')).strip()
            reviewer_id = str(row.get('reviewerId', '')).strip()
            published_date = str(row.get('publishedAtDate', '')).strip()
            review_id = str(row.get('reviewId', '')).strip() if 'reviewId' in row else ''
            
            unified_rows.append({
                'location_name': title,
                'reviewer_name': reviewer_name,
                'rating': rating,
                'review_text': review_text,
                'reviewer_id': reviewer_id,
                'published_date': published_date,
                'review_id': review_id,
                'source_file': row['source_file']
            })
            
    unified_df = pd.DataFrame(unified_rows)
    print(f"\nTotal unified raw rows (excluding Toko Goberz): {len(unified_df)}")
    
    # Check duplicates using unique keys: (reviewer_id, review_text)
    # We will keep the first occurrence or prioritize the one with more information
    # First, let's look at unique keys
    unique_mask = ~unified_df.duplicated(subset=['reviewer_id', 'review_text'], keep='first')
    deduped_df = unified_df[unique_mask]
    print(f"Total unique reviews: {len(deduped_df)}")
    print(f"Total duplicate reviews removed: {len(unified_df) - len(deduped_df)}")
    
    # Print value counts of locations
    print("\n--- Value counts of locations in deduped reviews ---")
    print(deduped_df['location_name'].value_counts())

if __name__ == '__main__':
    main()
