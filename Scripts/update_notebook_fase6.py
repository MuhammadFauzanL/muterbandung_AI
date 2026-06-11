import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# ============================================================
# TAMBAHKAN FASE 6 (RECOMMENDATION ENGINE)
# ============================================================
md_fase6 = """## [FASE 6] MuterBandung Core Recommendation Engine (Hybrid System)

Fase pamungkas ini menggabungkan dua kekuatan utama proyek ini:
1. **Master Database Geospatial & Harga** (Konteks Fisik/Geografis)
2. **AI Sentiment Analysis Biner** (Konteks Kepuasan Pelanggan dari 14.500 ulasan)

Output dari fase ini adalah algoritma prototipe *Hybrid Recommendation Engine* yang bisa mencari tempat wisata berdasarkan Kategori, *Budget* (Harga Maksimal), dan Tingkat Kepuasan Pelanggan Minimal (Sentimen AI)."""
nb.cells.append(nbf.v4.new_markdown_cell(md_fase6))

kode_fase6 = """import pandas as pd

# 1. Agregasi Skor Sentimen dari Data Labeled
df_reviews = pd.read_csv('Dataset/MASTER_REVIEWS_LABELED_BINARY.csv')
agg_sentimen = df_reviews.groupby('location_name').agg(
    total_ulasan=('sentimen_prediksi', 'count'),
    ulasan_positif=('sentimen_prediksi', lambda x: (x == 'positif').sum()),
    ulasan_negatif=('sentimen_prediksi', lambda x: (x == 'negatif').sum())
).reset_index()

# Hitung Persentase Sentimen Positif
agg_sentimen['skor_sentimen_persen'] = (agg_sentimen['ulasan_positif'] / agg_sentimen['total_ulasan']) * 100
agg_sentimen['skor_sentimen_persen'] = agg_sentimen['skor_sentimen_persen'].round(1)

# 2. Penggabungan dengan Master Database Wisata (GPS & Harga)
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')
df_engine = df_master.merge(agg_sentimen, on='location_name', how='left')

# Pembersihan data untuk lokasi tanpa ulasan
df_engine['total_ulasan'] = df_engine['total_ulasan'].fillna(0).astype(int)
df_engine['skor_sentimen_persen'] = df_engine['skor_sentimen_persen'].fillna(0)

df_engine.to_csv('Dataset/DATABASE_MUTERBANDUNG_ENGINE.csv', index=False)
print("Database Engine berhasil digabungkan: Dataset/DATABASE_MUTERBANDUNG_ENGINE.csv")

# 3. Fungsi Inti Recommendation Engine
def muterbandung_recommend(kategori=None, max_harga=None, min_sentimen=70):
    hasil = df_engine.copy()
    
    # Filter berbasis Atribut Fisik
    if kategori:
        hasil = hasil[hasil['category'].str.lower() == kategori.lower()]
    if max_harga is not None:
        hasil = hasil[hasil['price_min'] <= max_harga]
        
    # Filter berbasis AI Sentimen
    hasil = hasil[hasil['skor_sentimen_persen'] >= min_sentimen]
    
    # Ranking berdasarkan Kualitas (Sentimen) lalu Kuantitas Bukti (Total Ulasan)
    hasil = hasil.sort_values(by=['skor_sentimen_persen', 'total_ulasan'], ascending=[False, False])
    
    return hasil[['location_name', 'category', 'price_min', 'skor_sentimen_persen', 'total_ulasan']].head(5)

# --- SIMULASI ---
print("\\n--- SIMULASI 1: TURIS BACKPACKER ---")
print("Cari: Wisata Alam, Gratis, Kepuasan >80%")
print(muterbandung_recommend(kategori="Wisata Alam", max_harga=0, min_sentimen=80).to_string(index=False))

print("\\n--- SIMULASI 2: KELUARGA MENENGAH ---")
print("Cari: Rekreasi Keluarga, Budget Max 30rb, Kepuasan Sangat Tinggi (>90%)")
print(muterbandung_recommend(kategori="Rekreasi Keluarga", max_harga=30000, min_sentimen=90).to_string(index=False))"""
nb.cells.append(nbf.v4.new_code_cell(kode_fase6))

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil mengupdate wisata_traning.ipynb dengan Fase 6 Engine!")
