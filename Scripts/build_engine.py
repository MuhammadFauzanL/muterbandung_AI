import pandas as pd
import numpy as np

print("="*65)
print("FASE 6: MUTERBANDUNG CORE RECOMMENDATION ENGINE")
print("="*65)

# 1. AGREGASI SENTIMEN
df_reviews = pd.read_csv('Dataset/MASTER_REVIEWS_LABELED_BINARY.csv')
agg_sentimen = df_reviews.groupby('location_name').agg(
    total_ulasan=('sentimen_prediksi', 'count'),
    ulasan_positif=('sentimen_prediksi', lambda x: (x == 'positif').sum()),
    ulasan_negatif=('sentimen_prediksi', lambda x: (x == 'negatif').sum()),
    mentions_pemandangan=('aspek_pemandangan', 'sum'),
    mentions_harga=('aspek_harga', 'sum'),
    mentions_fasilitas=('aspek_fasilitas', 'sum'),
    mentions_keluarga=('aspek_keluarga', 'sum')
).reset_index()

agg_sentimen['skor_sentimen_persen'] = (agg_sentimen['ulasan_positif'] / agg_sentimen['total_ulasan']) * 100
agg_sentimen['skor_sentimen_persen'] = agg_sentimen['skor_sentimen_persen'].round(1)

# 2. PENGGABUNGAN DENGAN MASTER GEOSPATIAL
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')
df_engine = df_master.merge(agg_sentimen, on='location_name', how='left')
df_engine['total_ulasan'] = df_engine['total_ulasan'].fillna(0).astype(int)
df_engine['skor_sentimen_persen'] = df_engine['skor_sentimen_persen'].fillna(0)
df_engine.to_csv('DATABASE_MUTERBANDUNG_ENGINE.csv', index=False)
print("DATABASE_MUTERBANDUNG_ENGINE.csv berhasil dibuat!")

# 3. ENGINE PROTOTYPE
def muterbandung_recommend(df, kategori=None, max_harga=None, min_sentimen=70):
    hasil = df.copy()
    if kategori:
        hasil = hasil[hasil['category'].str.lower() == kategori.lower()]
    if max_harga is not None:
        hasil = hasil[hasil['price_min'] <= max_harga]
    
    hasil = hasil[hasil['skor_sentimen_persen'] >= min_sentimen]
    hasil = hasil.sort_values(by=['skor_sentimen_persen', 'total_ulasan'], ascending=[False, False])
    
    kolom_tampil = ['location_name', 'category', 'price_min', 'skor_sentimen_persen', 'total_ulasan']
    return hasil[kolom_tampil]

# 4. TESTING
print("\\n==================================================")
print("TESTING SIMULASI ENGINE REKOMENDASI")
print("==================================================")

print("\\nSimulasi 1: Turis Backpacker")
print("Mencari: Wisata Alam, Gratis (Rp 0), Sentimen Positif > 80%")
print(muterbandung_recommend(df_engine, kategori="Wisata Alam", max_harga=0, min_sentimen=80).head(5).to_string(index=False))

print("\\nSimulasi 2: Keluarga Menengah")
print("Mencari: Rekreasi Keluarga, Budget Max Rp 30.000, Sentimen Sangat Tinggi (>90%)")
print(muterbandung_recommend(df_engine, kategori="Rekreasi Keluarga", max_harga=30000, min_sentimen=90).head(5).to_string(index=False))

print("\\nSimulasi 3: Peringkat Tertinggi se-Bandung (Budget 50.000)")
print("Mencari: Kategori Bebas, Budget Max 50.000, Sentimen 100%")
print(muterbandung_recommend(df_engine, max_harga=50000, min_sentimen=100).head(5).to_string(index=False))
