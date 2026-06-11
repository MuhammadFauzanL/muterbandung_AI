import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

# Load existing notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# ---------------------------------------------------------
# BAGIAN 1: PENGGABUNGAN DATASET REVIEW (APIFY + LAMA)
# ---------------------------------------------------------
nb.cells.append(nbf.v4.new_markdown_cell("## [TAHAP BARU] Penggabungan Master Data Ulasan (Cold Start Solved)\nBagian ini menggabungkan data ulasan lama dengan data hasil scraping terbaru dari Apify untuk mengatasi *Cold Start Problem* pada sistem rekomendasi."))

kode_merge = """import pandas as pd
import json

print("Memulai Proses Penggabungan Master Reviews...")

# 1. Load Data Lama
file_lama = 'Dataset/master_reviews_gabungan.csv'
df_lama = pd.read_csv(file_lama)

# 2. Load Data Apify Baru
file_apify_1 = 'Dataset/apify_reviews_part1.json'
file_apify_2 = 'Dataset/apify_reviews_part2.json'

with open(file_apify_1, 'r', encoding='utf-8') as f1:
    apify_1 = json.load(f1)
with open(file_apify_2, 'r', encoding='utf-8') as f2:
    apify_2 = json.load(f2)

# 3. Bersihkan Data Apify
df_apify_bersih = pd.DataFrame(apify_1 + apify_2).dropna(subset=['text']).copy()
df_apify_bersih.rename(columns={'title': 'location_name', 'name': 'reviewer_name', 'stars': 'rating', 'text': 'review_text'}, inplace=True)
df_apify_bersih['source_file'] = 'Apify_New_Scrape'

kolom_penting = ['location_name', 'reviewer_name', 'rating', 'review_text', 'source_file']
df_apify_final = df_apify_bersih[kolom_penting]

# 4. Gabungkan & Hapus Duplikat
kolom_irisan = [col for col in kolom_penting if col in df_lama.columns]
df_master_final = pd.concat([df_lama[kolom_irisan], df_apify_final], ignore_index=True)
df_master_final = df_master_final.drop_duplicates(subset=['location_name', 'reviewer_name', 'review_text'])

# 5. Export
df_master_final.to_csv('Dataset/MASTER_REVIEWS_FINAL.csv', index=False)

print(f"PENGGABUNGAN SUKSES! Total Ulasan: {len(df_master_final)} Baris")"""
nb.cells.append(nbf.v4.new_code_cell(kode_merge))

# ---------------------------------------------------------
# BAGIAN 2: AUDIT MASTER GEOSPATIAL & PRICING
# ---------------------------------------------------------
nb.cells.append(nbf.v4.new_markdown_cell("## [TAHAP BARU] Audit Kelengkapan Master Data Geospatial & Pricing\nSebelum melatih model NLP dan Recommendation Engine, sangat krusial untuk memastikan tidak ada titik koordinat atau harga yang kosong (Data Readiness Audit)."))

kode_audit = """# Load Database Master Lengkap
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

print("=== AUDIT GEOSPATIAL (GPS) ===")
lat_kosong = df_master['latitude'].isnull().sum()
lon_kosong = df_master['longitude'].isnull().sum()
print(f"Lokasi tanpa Latitude: {lat_kosong}")
print(f"Lokasi tanpa Longitude: {lon_kosong}")

print("\\n=== AUDIT HARGA TIKET (PRICING) ===")
if 'price_min' in df_master.columns:
    price_min_kosong = df_master['price_min'].isnull().sum()
    print(f"Harga Min kosong: {price_min_kosong}")
else:
    print("Kolom price_min tidak ditemukan, harap sesuaikan nama kolom harga.")

print("\\n=== AUDIT KATEGORI PARIWISATA ===")
print(df_master['category'].value_counts(dropna=False).head())

print("\\nKESIMPULAN AUDIT:")
if lat_kosong == 0 and lon_kosong == 0:
    print("[AMAN] Seluruh lokasi siap dipetakan pada engine!")
else:
    print("[WARNING] Ditemukan data bocor, butuh imputasi.")"""
nb.cells.append(nbf.v4.new_code_cell(kode_audit))

# Save the notebook back
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil menyisipkan kode ke dalam wisata_traning.ipynb!")
