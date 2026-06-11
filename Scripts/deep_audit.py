import pandas as pd
import numpy as np
import json
import os

def run_audit():
    file_path = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
    print(f'=== DEEP DATA QUALITY AUDIT: {file_path} ===')

    try:
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        print(f'Gagal membaca file: {e}')
        return

    total_rows = len(df)
    print(f'1. Total Baris: {total_rows}')
    print(f'2. Total Kolom: {len(df.columns)}')
    print(f'3. Kolom: {list(df.columns)}')

    # A. Missing Values
    print('\\n=== A. CEK DATA KOSONG (MISSING VALUES) ===')
    critical_cols = ['location_name', 'review_text', 'rating']
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            print(f'- {col}: {missing} data kosong ({missing/total_rows*100:.2f}%)')
        else:
            print(f'- {col}: KOLOM TIDAK DITEMUKAN!')

    # B. Duplikat
    print('\\n=== B. CEK DUPLIKASI DATA ===')
    if 'review_text' in df.columns and 'reviewer_name' in df.columns and 'location_name' in df.columns:
        dup_subset = ['location_name', 'reviewer_name', 'review_text']
        duplicates = df.duplicated(subset=dup_subset, keep='first').sum()
        print(f'- Baris Duplikat (Lokasi + Reviewer + Teks yang sama persis): {duplicates} baris ({duplicates/total_rows*100:.2f}%)')
        
        dup_text = df.duplicated(subset=['review_text'], keep=False).sum()
        print(f'- Teks Review yang diulang-ulang (berpotensi spam/bot): {dup_text} baris')
    else:
        print('- Kolom identifikasi tidak lengkap untuk cek duplikat')

    # C. Teks Noise
    print('\\n=== C. CEK NOISE PADA TEKS REVIEW ===')
    if 'review_text' in df.columns:
        df['text_len'] = df['review_text'].astype(str).str.len()
        short_texts = df[df['text_len'] < 5]
        print(f'- Review terlalu pendek (< 5 karakter, misal "ok"): {len(short_texts)} baris')
        
        empty_spaces = df[df['review_text'].astype(str).str.strip() == '']
        print(f'- Review hanya berisi spasi kosong: {len(empty_spaces)} baris')

    # D. Validasi Nama Lokasi
    print('\\n=== D. VALIDASI NAMA LOKASI ===')
    try:
        df_locs = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv', low_memory=False)
        master_locs = set(df_locs['location_name'].unique())
    except:
        print('Gagal load master locs')
        master_locs = set()

    if 'location_name' in df.columns:
        review_locs = set(df['location_name'].dropna().unique())
        mismatched = review_locs - master_locs
        
        print(f'- Total lokasi unik di data review: {len(review_locs)}')
        print(f'- Lokasi yang TIDAK ADA di Master Database: {len(mismatched)} lokasi')
        
        try:
            with open('proposed_location_mapping.json') as f:
                auto_mapping = json.load(f)['mapping']
        except:
            auto_mapping = {}
            
        manual_mapping = {
            'Air Terjun Anom': 'Curug Anom',
            'CURUG BATU TEMPLEK CISANGGARUNG': 'Curug Batu Templek',
            'Hutan Mycelia Wahana Edukasi & Interaktif': 'Taman Main Mili-Mili & Hutan Mycelia',
            'KAWAH CIBUNI Rengganis': 'Kawah Rengganis Ciwidey',
            "MUARA RAHONG HILL'S": 'Muara Rahong Hills',
            'Gn. Hawu': 'Tebing Gunung Hawu'
        }
        to_delete = ['Punclut cafe lereng', 'TOKO GOBERZ AUDIO MOBIL 97', 'Cikahuripan', 'Curug Ngebul Cianjur Selatan', 'Curug Walanda', 'Palayangan River', 'Punclut Puncak', 'Taman Rusa']
        
        final_mapping = {**auto_mapping, **manual_mapping}
        
        unresolved = []
        resolved_count = 0
        to_delete_count = 0
        
        for loc in mismatched:
            if loc in final_mapping:
                resolved_count += 1
            elif loc in to_delete:
                to_delete_count += 1
            else:
                unresolved.append(loc)
                
        print(f'  -> Yang BISA dinormalisasi oleh Mapping sebelumnya: {resolved_count} lokasi')
        print(f'  -> Yang AKAN dihapus berdasarkan kesepakatan: {to_delete_count} lokasi')
        print(f'  -> Masalah BARU (Tidak ada di mapping & master): {len(unresolved)} lokasi')
        
        if unresolved:
            print('  Contoh masalah BARU (15 pertama):')
            for u in unresolved[:15]:
                print(f'    - {u}')

    # E. Struktur Kolom NLP
    print('\\n=== E. STATUS PELABELAN NLP ===')
    if 'review_nlp' in df.columns:
        labeled = df['review_nlp'].notna().sum()
        unlabeled = df['review_nlp'].isna().sum()
        print(f'- Teks dengan label sentimen: {labeled}')
        print(f'- Teks TANPA label sentimen: {unlabeled}')

if __name__ == '__main__':
    run_audit()
