import pandas as pd
import glob
import os

# 1. Baca data original yang berlabel
file_original = 'Dataset/MASTER_REVIEWS_LABELED.csv'
df_base = pd.read_csv(file_original)
df_base['sumber'] = 'original_labeled'
print(f"[BASE] Labeled original read: {len(df_base):,} rows")

# 2. Cari semua file tambahan hasil scraper Apify
# Kita cari di folder Dataset/ yang mengandung nama 'apify_reviews_tambahan'
# Dan juga file-file baru di folder Downloads user
search_paths = [
    'Dataset/apify_reviews_tambahan*.csv',
    'c:/Users/M Fauzan Lubada/Downloads/Penginapan-20260516T043918Z-3-001/dataset_Google-Maps-Reviews-Scraper_*.csv'
]

additional_files = []
for path in search_paths:
    additional_files.extend(glob.glob(path))

# Hapus duplikat path file jika ada
additional_files = list(set(additional_files))

print(f"\nDitemukan {len(additional_files)} file tambahan untuk digabungkan:")
for f in sorted(additional_files):
    print(f"  - {os.path.basename(f)} ({os.path.getsize(f):,} bytes)")

# 3. Gabungkan semua file tambahan ke base
dfs_to_concat = [df_base]

kolom_mapping = {
    'title': 'location_name',
    'text': 'review_text',
    'stars': 'rating',
    'name': 'reviewer_name',
}

for f in sorted(additional_files):
    try:
        df_temp = pd.read_csv(f)
        # Drop existing 'rating' column if 'stars' also exists, to avoid duplication after rename
        if 'rating' in df_temp.columns and 'stars' in df_temp.columns:
            df_temp = df_temp.drop(columns=['rating'])
            
        # Rename kolom agar seragam
        df_temp = df_temp.rename(columns=kolom_mapping)
        df_temp['sumber'] = os.path.basename(f)
        
        # Pastikan kolom-kolom penting ada
        if 'location_name' in df_temp.columns and 'review_text' in df_temp.columns:
            dfs_to_concat.append(df_temp)
            print(f"[MERGE] Berhasil memuat: {os.path.basename(f)} ({len(df_temp):,} rows)")
        else:
            print(f"[SKIP] Kolom wajib tidak lengkap di file: {os.path.basename(f)}")
    except Exception as e:
        print(f"[ERROR] Gagal membaca {f}: {e}")

# 4. Gabungkan dan hapus duplikat
df_merged = pd.concat(dfs_to_concat, ignore_index=True)
print(f"\nTotal sebelum deduplikasi: {len(df_merged):,} rows")

# Kunci unik untuk deduplikasi
df_merged['_key_dedup'] = (
    df_merged['location_name'].astype(str).str.strip().str.lower() + '|' +
    df_merged['review_text'].astype(str).str.strip().str.lower()
)

# Urutkan agar original_labeled berada paling bawah sehingga terpilih jika ada duplikat (menjaga label sentimen)
df_merged = df_merged.sort_values('sumber', ascending=False)
df_cleaned = df_merged.drop_duplicates(subset='_key_dedup', keep='first')
df_cleaned = df_cleaned.drop(columns=['_key_dedup', 'sumber'])

print(f"Total setelah deduplikasi: {len(df_cleaned):,} rows")
print(f"Duplikat yang dibuang: {len(df_merged) - len(df_cleaned):,} rows")

# 5. Analisis singkat ketimpangan baru
per_lokasi = df_cleaned.groupby('location_name').size().sort_values(ascending=True)
print("\n=== DISTRIBUSI BARU ===")
print(f"Rata-rata review per lokasi: {per_lokasi.mean():.1f}")
print(f"Median review per lokasi: {per_lokasi.median():.1f}")
print(f"Lokasi dengan < 30 review: {(per_lokasi < 30).sum()} lokasi")
print(f"Lokasi dengan < 50 review: {(per_lokasi < 50).sum()} lokasi")

# 6. Simpan hasil akhir
output_file = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'
df_cleaned.to_csv(output_file, index=False)
print(f"\n[SUKSES] Master dataset baru yang super lengkap disimpan ke: {output_file}")
