import nbformat as nbf

# Buat notebook baru
nb = nbf.v4.new_notebook()

# Tambahkan cell Markdown
nb.cells.append(nbf.v4.new_markdown_cell("# Penggabungan Master Data Ulasan MuterBandung\nNotebook ini dibuat untuk menggabungkan **Data Lama (9.557 Ulasan)** dengan **Data Apify Baru (175 Lokasi)**."))

# Cell 1: Import library
kode_1 = """import pandas as pd
import json

print("Pandas siap digunakan!")"""
nb.cells.append(nbf.v4.new_code_cell(kode_1))

# Cell 2: Memuat Data Lama
kode_2 = """# Load Data Lama
file_lama = 'Dataset/master_reviews_gabungan.csv'
df_lama = pd.read_csv(file_lama)

print(f"Data Lama berhasil dimuat: {len(df_lama)} baris.")
df_lama.head(2)"""
nb.cells.append(nbf.v4.new_code_cell(kode_2))

# Cell 3: Memuat Data Apify Baru
kode_3 = """# Load Data Baru (JSON Apify)
file_apify_1 = 'Dataset/apify_reviews_part1.json'
file_apify_2 = 'Dataset/apify_reviews_part2.json'

with open(file_apify_1, 'r', encoding='utf-8') as f1:
    apify_1 = json.load(f1)
with open(file_apify_2, 'r', encoding='utf-8') as f2:
    apify_2 = json.load(f2)

# Gabungkan kedua data list Python
apify_semua = apify_1 + apify_2
print(f"Total ulasan mentah dari Apify: {len(apify_semua)}")

# Jadikan DataFrame
df_apify_mentah = pd.DataFrame(apify_semua)
df_apify_mentah.head(2)"""
nb.cells.append(nbf.v4.new_code_cell(kode_3))

# Cell 4: Membersihkan dan Menyelaraskan Kolom
kode_4 = """# 1. Buang ulasan yang tidak ada teks (text = null/NaN)
df_apify_bersih = df_apify_mentah.dropna(subset=['text']).copy()

# 2. Ubah nama kolom agar cocok dengan Dataset Lama
df_apify_bersih.rename(columns={
    'title': 'location_name',
    'name': 'reviewer_name',
    'stars': 'rating',
    'text': 'review_text'
}, inplace=True)

# 3. Tambahkan kolom penanda sumber
df_apify_bersih['source_file'] = 'Apify_New_Scrape'

# 4. Pilih hanya kolom yang dibutuhkan
kolom_penting = ['location_name', 'reviewer_name', 'rating', 'review_text', 'source_file']
df_apify_final = df_apify_bersih[kolom_penting]

print(f"Data Baru yang bersih (ada teks): {len(df_apify_final)} baris.")
df_apify_final.head(2)"""
nb.cells.append(nbf.v4.new_code_cell(kode_4))

# Cell 5: PENGGABUNGAN (The Grand Merge)
kode_5 = """# Pastikan df_lama juga hanya mengambil kolom yang relevan (jika ada kolom ekstra)
kolom_irisan = [col for col in kolom_penting if col in df_lama.columns]

# Gabungkan!
df_master_final = pd.concat([df_lama, df_apify_final], ignore_index=True)

print(f"PENGGABUNGAN SUKSES!")
print(f"TOTAL ULASAN SAAT INI: {len(df_master_final)} Baris")

# Hitung jumlah unik lokasi
print(f"Total Lokasi Unik yang Tercakup: {df_master_final['location_name'].nunique()}")"""
nb.cells.append(nbf.v4.new_code_cell(kode_5))

# Cell 6: Export ke CSV
kode_6 = """# Simpan ke CSV untuk proses Sentiment Analysis selanjutnya
df_master_final.to_csv('Dataset/MASTER_REVIEWS_FINAL.csv', index=False, encoding='utf-8')
print("File tersimpan: Dataset/MASTER_REVIEWS_FINAL.csv")"""
nb.cells.append(nbf.v4.new_code_cell(kode_6))

# Tulis ke file .ipynb
with open('d:/File/file/Fauzan Lubada/PIJAK/Penggabungan_Master_Reviews.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook berhasil dibuat!")
