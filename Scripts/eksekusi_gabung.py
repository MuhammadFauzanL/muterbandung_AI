import pandas as pd
import json

print("Memulai Proses Penggabungan...")

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

apify_semua = apify_1 + apify_2
df_apify_mentah = pd.DataFrame(apify_semua)

# 3. Bersihkan Data Apify
df_apify_bersih = df_apify_mentah.dropna(subset=['text']).copy()
df_apify_bersih.rename(columns={
    'title': 'location_name',
    'name': 'reviewer_name',
    'stars': 'rating',
    'text': 'review_text'
}, inplace=True)
df_apify_bersih['source_file'] = 'Apify_New_Scrape'

kolom_penting = ['location_name', 'reviewer_name', 'rating', 'review_text', 'source_file']
df_apify_final = df_apify_bersih[kolom_penting]

# 4. Gabungkan Data Lama dan Baru
# Pastikan data lama juga hanya mengambil kolom yang relevan agar rapi
kolom_irisan = [col for col in kolom_penting if col in df_lama.columns]
df_lama_final = df_lama[kolom_irisan]

df_master_final = pd.concat([df_lama_final, df_apify_final], ignore_index=True)

# Hapus duplikat jika ada
df_master_final = df_master_final.drop_duplicates(subset=['location_name', 'reviewer_name', 'review_text'])

# 5. Export ke CSV Final
df_master_final.to_csv('Dataset/MASTER_REVIEWS_FINAL.csv', index=False, encoding='utf-8')

print("PENGGABUNGAN SUKSES!")
print(f"Total Baris Data Lama: {len(df_lama)}")
print(f"Total Baris Data Baru: {len(df_apify_final)}")
print(f"TOTAL ULASAN FINAL (Setelah Hapus Duplikat): {len(df_master_final)} Baris")
print(f"Total Lokasi Unik: {df_master_final['location_name'].nunique()}")
