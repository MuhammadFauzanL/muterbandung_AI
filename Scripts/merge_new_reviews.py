import pandas as pd
import os
import shutil

def main():
    old_path = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
    new_path = 'dataset_Google-Maps-Reviews-Scraper_2026-05-20_13-14-48-667.csv'
    backup_dir = 'Dataset/Archives'
    
    print("=== STARTING MERGE PROCESS ===")
    
    # 1. Read files
    df_old = pd.read_csv(old_path, low_memory=False)
    df_new = pd.read_csv(new_path, low_memory=False)
    
    print(f"Current reviews in master: {len(df_old)} rows")
    print(f"Scraped reviews to process: {len(df_new)} rows")
    
    # 2. Filter out non-tourist spots
    excluded_spot = 'TOKO GOBERZ AUDIO MOBIL 97'
    df_new_filtered = df_new[df_new['title'] != excluded_spot].copy()
    print(f"Filtered out '{excluded_spot}': remaining {len(df_new_filtered)} reviews to merge")
    
    # 3. Map Names
    # Southland Camp -> Southland Camp Ciwidey, others remain identical
    name_map = {
        'Southland Camp': 'Southland Camp Ciwidey'
    }
    df_new_filtered['mapped_name'] = df_new_filtered['title'].apply(lambda x: name_map.get(x, x))
    
    # 4. Prepare new rows matching the schema of MASTER_REVIEWS_ENRICHED
    # Create empty dataframe with same columns
    new_rows = pd.DataFrame(columns=df_old.columns)
    
    # Copy identical columns
    common_cols = list(set(df_old.columns).intersection(set(df_new_filtered.columns)))
    for col in common_cols:
        new_rows[col] = df_new_filtered[col]
        
    # Map specific renamed/custom columns
    new_rows['location_name'] = df_new_filtered['mapped_name']
    new_rows['reviewer_name'] = df_new_filtered['name']
    new_rows['rating'] = df_new_filtered['stars']
    new_rows['review_text'] = df_new_filtered['text']
    new_rows['source_file'] = os.path.basename(new_path)
    
    # Calculate text length
    new_rows['panjang_teks'] = new_rows['review_text'].fillna('').apply(len)
    
    # Fill default/empty NLP and Sentiment fields with NaN/default
    nlp_fields = [
        'review_text_clean', 'review_nlp', 'aspek_pemandangan', 'aspek_harga',
        'aspek_fasilitas', 'aspek_pelayanan', 'aspek_keluarga', 'jumlah_aspek_terdeteksi',
        'sentimen', 'sentimen_prediksi', 'sentimen_skor'
    ]
    for field in nlp_fields:
        if field in new_rows.columns:
            new_rows[field] = None
            
    print(f"Prepared {len(new_rows)} rows matching schema.")
    
    # 5. Backup current master file
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"MASTER_REVIEWS_ENRICHED_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv")
    shutil.copy2(old_path, backup_file)
    print(f"Backup created at: {backup_file}")
    
    # 6. Concat and Save
    df_combined = pd.concat([df_old, new_rows], ignore_index=True)
    df_combined.to_csv(old_path, index=False)
    print(f"Merge successful! New size of master reviews: {len(df_combined)} rows (added {len(new_rows)} rows)")

if __name__ == '__main__':
    main()
