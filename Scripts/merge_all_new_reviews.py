import pandas as pd
import os
import shutil

def main():
    old_path = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
    backup_dir = 'Dataset/Archives'
    
    scraper_files = [
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_13-14-48-667.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-29-27-671.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-33-45-408.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471.csv'
    ]
    
    print("=== STARTING MERGE PROCESS ===")
    
    # 1. Load Master Dataset
    df_old = pd.read_csv(old_path, low_memory=False)
    print(f"Current reviews in master: {len(df_old)} rows")
    
    # Create matching key set from existing master reviews
    # Using (reviewerId, review_text) as unique key
    master_keys = set()
    for idx, row in df_old.iterrows():
        rev_id = str(row.get('reviewerId', '')).strip()
        text = str(row.get('review_text', '')).strip()
        if rev_id or text:
            master_keys.add((rev_id, text))
            
    print(f"Unique keys in master: {len(master_keys)}")
    
    # Name mappings for consistency
    name_map = {
        'inggit garnasih historic house': 'Museum Inggit Garnasih',
        'kampung wisata pangjugjugan': 'Pangjugjugan Sumedang',
        'kawasan konservasi taman buru g. masigit kareumbi': 'Taman Buru Gunung Masigit Kareumbi',
        'kebun teh malabar': 'Perkebunan Teh Malabar',
        'kolam renang karang setra': 'Karang Setra Waterland',
        "muara rahong hill's": 'Muara Rahong Hills',
        'nu art studio': 'NuArt Sculpture Park',
        'palayangan river': 'Sungai Palayangan Rafting',
        'southland camp': 'Southland Camp Ciwidey',
        'taman lembah dewata': 'Taman Lembah Dewata'
    }
    
    # 2. Process and deduplicate new reviews across all files
    new_reviews_list = []
    skipped_outliers = 0
    duplicate_within_new = 0
    duplicate_with_master = 0
    
    new_keys_seen = set()
    
    for f in scraper_files:
        if not os.path.exists(f):
            print(f"Warning: File {f} not found!")
            continue
        
        df_new = pd.read_csv(f, low_memory=False)
        print(f"Processing {f} ({len(df_new)} rows)")
        
        for idx, row in df_new.iterrows():
            title = str(row.get('title', '')).strip()
            title_lower = title.lower()
            
            # Filter out non-tourist spot
            if title_lower == 'toko goberz audio mobil 97':
                skipped_outliers += 1
                continue
                
            # Map names
            mapped_name = name_map.get(title_lower, title)
            
            # Review text and reviewer ID
            review_text = str(row.get('text', '')).strip()
            reviewer_id = str(row.get('reviewerId', '')).strip()
            
            key = (reviewer_id, review_text)
            
            # Check internal duplicate
            if key in new_keys_seen:
                duplicate_within_new += 1
                continue
                
            # Check duplicate with existing master
            if key in master_keys:
                duplicate_with_master += 1
                continue
                
            # Mark as seen
            new_keys_seen.add(key)
            
            # Build unified row
            # We copy all columns that match the master schema from row
            new_row_dict = {}
            for col in df_old.columns:
                # Direct match in scraper
                if col in row:
                    new_row_dict[col] = row[col]
                    
            # Set specific columns explicitly
            new_row_dict['location_name'] = mapped_name
            new_row_dict['reviewer_name'] = row.get('name')
            
            # Rating logic (stars vs rating)
            rating = row.get('stars')
            if pd.isna(rating):
                rating = row.get('rating')
            new_row_dict['rating'] = rating
            
            new_row_dict['review_text'] = review_text
            new_row_dict['source_file'] = os.path.basename(f)
            new_row_dict['panjang_teks'] = len(review_text) if pd.notna(review_text) else 0
            
            # Set default/empty NLP/Sentiment fields
            nlp_fields = [
                'review_text_clean', 'review_nlp', 'aspek_pemandangan', 'aspek_harga',
                'aspek_fasilitas', 'aspek_pelayanan', 'aspek_keluarga', 'jumlah_aspek_terdeteksi',
                'sentimen', 'sentimen_prediksi', 'sentimen_skor'
            ]
            for field in nlp_fields:
                new_row_dict[field] = None
                
            new_reviews_list.append(new_row_dict)
            
    df_new_prepared = pd.DataFrame(new_reviews_list)
    print("\n=== MERGE ANALYSIS REPORT ===")
    print(f"Skipped Outliers (Toko Goberz): {skipped_outliers}")
    print(f"Duplicates within new scraper files: {duplicate_within_new}")
    print(f"Duplicates already in master dataset: {duplicate_with_master}")
    print(f"New unique reviews ready to merge: {len(df_new_prepared)}")
    
    if len(df_new_prepared) == 0:
        print("No new reviews to merge.")
        return
        
    # 3. Create Backup of Master Enriched
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"MASTER_REVIEWS_ENRICHED_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv")
    shutil.copy2(old_path, backup_file)
    print(f"\nBackup created at: {backup_file}")
    
    # 4. Concat and Save
    # Align columns
    df_combined = pd.concat([df_old, df_new_prepared], ignore_index=True)
    df_combined.to_csv(old_path, index=False)
    print(f"Merge successful! New size of master reviews: {len(df_combined)} rows (added {len(df_new_prepared)} rows)")

if __name__ == '__main__':
    main()
