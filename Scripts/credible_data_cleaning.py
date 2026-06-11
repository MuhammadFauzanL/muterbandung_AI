import pandas as pd
import json
import os
import shutil
from datetime import datetime

def credible_data_cleaning():
    file_path = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
    backup_path = f'Dataset/Archives/MASTER_REVIEWS_ENRICHED_backup_preclean_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    master_db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'

    print("="*60)
    print("MUTERBANDUNG DATA SCIENCE PIPELINE - CREDIBLE CLEANSING")
    print("="*60)

    # 1. Create Backup
    print(f"\n[1] Membuat backup dataset utama ke: {backup_path}")
    os.makedirs('Dataset/Archives', exist_ok=True)
    shutil.copy2(file_path, backup_path)

    # 2. Load Data
    print(f"\n[2] Memuat dataset ulasan dari: {file_path}")
    df = pd.read_csv(file_path, low_memory=False)
    initial_rows = len(df)
    initial_cols = len(df.columns)
    print(f"    -> Ditemukan {initial_rows} baris dan {initial_cols} kolom.")

    # 3. Column Selection (Dimensionality Reduction)
    print("\n[3] Memangkas kolom metadata yang tidak relevan (Feature Selection)")
    target_columns = [
        'location_name', 'reviewer_name', 'rating', 'review_text', 
        'source_file', 'panjang_teks', 'review_text_clean', 'review_nlp', 
        'aspek_pemandangan', 'aspek_harga', 'aspek_fasilitas', 
        'aspek_pelayanan', 'aspek_keluarga', 'jumlah_aspek_terdeteksi'
    ]
    
    # Ensure columns exist, if not create them with NaN to maintain schema
    for col in target_columns:
        if col not in df.columns:
            df[col] = pd.NA
            
    df = df[target_columns]
    print(f"    -> Berhasil menyisakan {len(df.columns)} kolom inti untuk NLP.")

    # 4. Handling Missing Values
    print("\n[4] Menghapus data kosong (Handling Missing Values)")
    df = df.dropna(subset=['review_text', 'rating', 'location_name'])
    dropped_missing = initial_rows - len(df)
    print(f"    -> Membuang {dropped_missing} baris tanpa teks/rating/lokasi.")

    # 5. Noise Filtering
    print("\n[5] Menyaring noise dan teks spam (Noise Filtering)")
    prev_len = len(df)
    df['review_text'] = df['review_text'].astype(str).str.strip()
    df = df[df['review_text'].str.len() >= 5]
    dropped_noise = prev_len - len(df)
    print(f"    -> Membuang {dropped_noise} baris dengan teks < 5 karakter (spam/pendek).")

    # 6. Deduplication
    print("\n[6] Menghapus ulasan duplikat (Deduplication)")
    prev_len = len(df)
    df = df.drop_duplicates(subset=['location_name', 'reviewer_name', 'review_text'], keep='first')
    dropped_dupes = prev_len - len(df)
    print(f"    -> Membuang {dropped_dupes} baris duplikat identik.")

    # 7. Out-of-Scope & Invalid Locations Deletion
    print("\n[7] Menghapus lokasi tidak relevan/luar kota (Outliers Removal)")
    to_delete = [
        'Taman Wisata Alam Gunung Pancar', 'Google Ann Arbor', 
        'Punclut cafe lereng', 'TOKO GOBERZ AUDIO MOBIL 97', 
        'Cikahuripan', 'Curug Ngebul Cianjur Selatan', 
        'Curug Walanda', 'Palayangan River', 'Punclut Puncak', 'Taman Rusa'
    ]
    prev_len = len(df)
    df = df[~df['location_name'].isin(to_delete)]
    dropped_invalid = prev_len - len(df)
    print(f"    -> Membuang {dropped_invalid} baris dari lokasi tidak valid.")

    # 8. Location Name Normalization (Entity Resolution)
    print("\n[8] Menormalisasi nama lokasi (Entity Resolution & Fuzzy Mapping)")
    try:
        with open('proposed_location_mapping.json') as f:
            auto_mapping = json.load(f)['mapping']
    except:
        auto_mapping = {}
        print("    -> Warning: mapping otomatis JSON tidak ditemukan.")

    # Remove overridden keys from auto_mapping
    for k in list(auto_mapping.keys()):
        if k in to_delete:
            del auto_mapping[k]

    manual_mapping = {
        'Air Terjun Anom': 'Curug Anom',
        'CURUG BATU TEMPLEK CISANGGARUNG': 'Curug Batu Templek',
        'Hutan Mycelia Wahana Edukasi & Interaktif': 'Taman Main Mili-Mili & Hutan Mycelia',
        'KAWAH CIBUNI Rengganis': 'Kawah Rengganis Ciwidey',
        "MUARA RAHONG HILL'S": 'Muara Rahong Hills',
        'Gn. Hawu': 'Tebing Gunung Hawu'
    }
    
    final_mapping = {**auto_mapping, **manual_mapping}
    
    mapped_count = df['location_name'].isin(final_mapping.keys()).sum()
    df['location_name'] = df['location_name'].replace(final_mapping)
    print(f"    -> Berhasil menormalisasi {mapped_count} baris nama lokasi.")

    # 9. Referential Integrity Check (Foreign Key Constraint)
    print("\n[9] Menegakkan Integritas Referensial (Referential Integrity Check)")
    df_locs = pd.read_csv(master_db_path, low_memory=False)
    master_locs = set(df_locs['location_name'].unique())
    
    prev_len = len(df)
    # Filter rows where location_name is strictly in master_locs
    df = df[df['location_name'].isin(master_locs)]
    dropped_unlinked = prev_len - len(df)
    
    if dropped_unlinked > 0:
        print(f"    -> Membuang {dropped_unlinked} baris yang gagal dihubungkan ke Master Database (Enforce FK).")
    else:
        print("    -> Sempurna! Semua baris ulasan terhubung 100% ke Master Database.")

    # 10. Save Final Cleaned Data
    print(f"\n[10] Menyimpan dataset bersih (Final Export)")
    df.to_csv(file_path, index=False)
    final_rows = len(df)
    print(f"    -> Dataset bersih berhasil disimpan ke: {file_path}")
    print(f"    -> Total Baris Akhir: {final_rows} (Menyusut {(initial_rows - final_rows)/initial_rows*100:.2f}%)")
    
    # Calculate how many need NLP
    unlabeled = df['review_nlp'].isna().sum()
    print(f"    -> Jumlah ulasan yang SIAP dilabeli NLP: {unlabeled}")
    print("="*60)
    print("PROSES CLEANSING SELESAI")
    print("="*60)

if __name__ == "__main__":
    credible_data_cleaning()
