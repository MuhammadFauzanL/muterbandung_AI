import nbformat as nbf

nb = nbf.v4.new_notebook()

# Markdown: Header
nb.cells.append(nbf.v4.new_markdown_cell("# [Wisata Training] Tahap 1: Audit & Validasi Master Data Geospatial\nNotebook ini didesain khusus untuk melakukan validasi kesiapan data sebelum masuk ke tahap *Sentiment Analysis (NLP)* dan *Hybrid Recommendation Engine*. \n\n**Tujuan Audit:**\n1. Memastikan tidak ada titik koordinat (Latitude/Longitude) yang kosong (Mencegah *error* pada Geospatial Engine).\n2. Memastikan data Harga (Pricing) terisi dengan baik.\n3. Menganalisis kebersihan Kategori Pariwisata."))

# Cell 1: Import & Load
kode_1 = """import pandas as pd
import numpy as np

# Load Database Master
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

print(f"Total Destinasi Wisata: {len(df_master)} Lokasi")
df_master.head()"""
nb.cells.append(nbf.v4.new_code_cell(kode_1))

# Cell 2: Audit Geospatial
kode_2 = """# Audit Kolom Latitude & Longitude
print("=== AUDIT GEOSPATIAL (GPS) ===")
lat_kosong = df_master['latitude'].isnull().sum()
lon_kosong = df_master['longitude'].isnull().sum()

print(f"Lokasi tanpa Latitude: {lat_kosong}")
print(f"Lokasi tanpa Longitude: {lon_kosong}")

if lat_kosong > 0 or lon_kosong > 0:
    print("\\n[WARNING] Ada lokasi tanpa koordinat! Harus diimputasi sebelum masuk ke Map Engine.")
    display(df_master[df_master['latitude'].isnull() | df_master['longitude'].isnull()][['location_name', 'latitude', 'longitude']])
else:
    print("\\n[AMAN] Seluruh lokasi memiliki titik koordinat GPS yang valid! Siap untuk Geospatial Recommendation.")"""
nb.cells.append(nbf.v4.new_code_cell(kode_2))

# Cell 3: Audit Harga (Pricing)
kode_3 = """# Audit Kolom Harga (price_min & price_max)
print("=== AUDIT HARGA TIKET (PRICING) ===")
price_min_kosong = df_master['price_min'].isnull().sum()
price_max_kosong = df_master['price_max'].isnull().sum()

print(f"Harga Min kosong (Null): {price_min_kosong}")
print(f"Harga Max kosong (Null): {price_max_kosong}")

# Cek apakah ada harga yang terisi "0" (Kemungkinan Gratis)
gratis_count = (df_master['price_min'] == 0).sum()
print(f"Lokasi dengan harga Rp 0 (Gratis): {gratis_count} Lokasi")

if price_min_kosong > 0:
    print("\\n[WARNING] Terdapat data harga yang kosong (NaN). Sebaiknya diisi dengan 0 (jika gratis) atau nilai rata-rata kategorinya.")
else:
    print("\\n[AMAN] Seluruh data harga sudah terisi!")"""
nb.cells.append(nbf.v4.new_code_cell(kode_3))

# Cell 4: Audit Kategori
kode_4 = """# Audit Kelengkapan Kategori
print("=== AUDIT KATEGORI PARIWISATA ===")
print("\\nDistribusi Kategori Utama (Category):")
print(df_master['category'].value_counts(dropna=False))

print("\\nDistribusi Sub-Kategori (Subcategory):")
print(df_master['subcategory'].value_counts(dropna=False).head(10)) # Tampilkan top 10 saja

kategori_kosong = df_master['category'].isnull().sum()
if kategori_kosong > 0:
    print(f"\\n[WARNING] Ada {kategori_kosong} lokasi yang belum memiliki Kategori.")"""
nb.cells.append(nbf.v4.new_code_cell(kode_4))

# Cell 5: Kesimpulan
nb.cells.append(nbf.v4.new_markdown_cell("### Kesimpulan & Tindakan Selanjutnya\nJika semua indikator di atas menunjukkan status **[AMAN]**, maka *Database Master* ini sudah **Siap Tempur**.\nJika ada yang berstatus **[WARNING]**, kita harus menambalnya (Imputation) dengan Notebook tahap 2 sebelum mengeksekusi model NLP kita."))

# Simpan Notebook
with open('d:/File/file/Fauzan Lubada/PIJAK/Wisata_Training_1_Audit_Master_Data.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Notebook Audit berhasil dibuat!")
