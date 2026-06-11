import pandas as pd
import json
import numpy as np

print("="*70)
print("DEEP EXPLORATORY DATA ANALYSIS (EDA) - MUTERBANDUNG CAPSTONE")
print("="*70)

# ============================================================
# BAGIAN A: ANALISIS DATABASE MASTER (232 Lokasi)
# ============================================================
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

print("\n[A] ANALISIS DATABASE MASTER WISATA")
print("-"*50)
print(f"Total Lokasi: {len(df_master)}")
print(f"Kolom: {df_master.columns.tolist()}")

# A1. Distribusi Kategori Lengkap
print("\n[A1] DISTRIBUSI KATEGORI LENGKAP:")
print(df_master['category'].value_counts())

# A2. Distribusi Sub-Kategori
print("\n[A2] DISTRIBUSI SUB-KATEGORI:")
print(df_master['subcategory'].value_counts())

# A3. Analisis Harga
print("\n[A3] ANALISIS HARGA TIKET:")
print(f"  Rata-rata Harga Min: Rp {df_master['price_min'].mean():,.0f}")
print(f"  Rata-rata Harga Max: Rp {df_master['price_max'].mean():,.0f}")
print(f"  Lokasi Gratis (price_min=0): {(df_master['price_min']==0).sum()}")
print(f"  Termahal (price_max): Rp {df_master['price_max'].max():,.0f}")
print(f"  Price Type unik: {df_master['price_type'].unique().tolist()}")

# A4. Analisis Geospatial (Sebaran Koordinat)
print("\n[A4] SEBARAN GEOSPATIAL:")
print(f"  Latitude range:  {df_master['latitude'].min():.6f} - {df_master['latitude'].max():.6f}")
print(f"  Longitude range: {df_master['longitude'].min():.6f} - {df_master['longitude'].max():.6f}")

# Hitung jarak antar titik terjauh (sebaran)
from math import radians, cos, sin, asin, sqrt
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * 6371 * asin(sqrt(a))

max_dist = haversine(df_master['latitude'].min(), df_master['longitude'].min(),
                     df_master['latitude'].max(), df_master['longitude'].max())
print(f"  Diameter sebaran lokasi: {max_dist:.1f} km")

# A5. Harga per Kategori
print("\n[A5] RATA-RATA HARGA PER KATEGORI:")
harga_kategori = df_master.groupby('category')['price_min'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False)
print(harga_kategori.to_string())

# ============================================================
# BAGIAN B: ANALISIS REVIEW DATA (16.120 Ulasan)
# ============================================================
df_reviews = pd.read_csv('Dataset/MASTER_REVIEWS_FINAL.csv')

print("\n\n[B] ANALISIS REVIEW DATA")
print("-"*50)
print(f"Total Ulasan: {len(df_reviews)}")
print(f"Lokasi Unik (ada ulasan): {df_reviews['location_name'].nunique()}")

# B1. Distribusi Rating
print("\n[B1] DISTRIBUSI RATING:")
print(df_reviews['rating'].value_counts().sort_index())
print(f"  Rating Rata-rata: {df_reviews['rating'].mean():.2f}")

# B2. Panjang Teks
df_reviews['panjang'] = df_reviews['review_text'].astype(str).apply(len)
print("\n[B2] STATISTIK PANJANG TEKS ULASAN:")
print(f"  Rata-rata: {df_reviews['panjang'].mean():.0f} karakter")
print(f"  Median: {df_reviews['panjang'].median():.0f} karakter")
print(f"  Max: {df_reviews['panjang'].max()} karakter")
print(f"  Teks < 10 karakter: {(df_reviews['panjang'] < 10).sum()} (risiko noise)")
print(f"  Teks > 100 karakter: {(df_reviews['panjang'] > 100).sum()} (bermakna)")

# B3. Top Lokasi dengan Ulasan Terbanyak
print("\n[B3] TOP 10 LOKASI PALING BANYAK DIULAS:")
top_lokasi = df_reviews['location_name'].value_counts().head(10)
for i, (nama, jumlah) in enumerate(top_lokasi.items(), 1):
    print(f"  {i}. {nama}: {jumlah} ulasan")

# B4. Lokasi dengan Ulasan Paling Sedikit
print("\n[B4] 10 LOKASI PALING JARANG DIULAS:")
bottom_lokasi = df_reviews['location_name'].value_counts().tail(10)
for nama, jumlah in bottom_lokasi.items():
    print(f"  - {nama}: {jumlah} ulasan")

# B5. Rating per Lokasi (Rata-rata)
avg_rating = df_reviews.groupby('location_name')['rating'].mean()
print("\n[B5] TOP 5 LOKASI RATING TERTINGGI (dengan >5 ulasan):")
count_per_loc = df_reviews.groupby('location_name')['rating'].count()
valid = count_per_loc[count_per_loc >= 5].index
top_rated = avg_rating[valid].sort_values(ascending=False).head(5)
for nama, rating in top_rated.items():
    print(f"  - {nama}: {rating:.2f}")

print("\n[B5b] TOP 5 LOKASI RATING TERENDAH (dengan >5 ulasan):")
bottom_rated = avg_rating[valid].sort_values().head(5)
for nama, rating in bottom_rated.items():
    print(f"  - {nama}: {rating:.2f}")

# B6. Deteksi Bahasa
sample = df_reviews['review_text'].dropna().sample(min(500, len(df_reviews)), random_state=42).str.lower()
indo_words = 'bagus|tempat|indah|bersih|kotor|enak|pemandangan|keren|mantap|seru|nyaman|jelek|buruk|luas|ramah|ramai|sepi|mahal|murah|asri'
eng_words = 'good|beautiful|nice|great|clean|amazing|view|place|bad|ugly|dirty|expensive|cheap|lovely|wonderful|terrible'
indo_count = sample.str.contains(indo_words).sum()
eng_count = sample.str.contains(eng_words).sum()
print(f"\n[B6] DETEKSI BAHASA (Sampel {len(sample)}):")
print(f"  Mengandung kata Indonesia: {indo_count} ({indo_count/len(sample)*100:.1f}%)")
print(f"  Mengandung kata Inggris: {eng_count} ({eng_count/len(sample)*100:.1f}%)")

# B7. Kata yang paling sering muncul
from collections import Counter
all_text = ' '.join(df_reviews['review_text'].dropna().astype(str).str.lower())
words = all_text.split()
stopwords_id = {'yang', 'di', 'dan', 'ini', 'itu', 'dari', 'ke', 'untuk', 'dengan', 'ya', 'ada', 'juga', 'saya', 'nya', 'tidak', 'bisa', 'sangat', 'sudah', 'kami', 'kita', 'lagi', 'aja', 'banget', 'udah', 'deh', 'dong', 'sih', 'lah', 'tapi', 'jadi', 'sama', 'kalau', 'mau', 'karena', 'lebih', 'sekali', 'akan', 'seperti', 'waktu', 'tahun', 'atau', 'hanya', 'mereka', 'semua', 'punya', 'masih', 'terlalu', 'orang', 'satu', 'dia', 'banyak', 'cukup', 'apa', 'kali', 'nggak', 'gak', 'si', 'se', 'ter', 'ber', 'me', 'the', 'and', 'is', 'to', 'of', 'a', 'in', 'for', 'it', 'on', 'are', 'was', 'but'}
filtered = [w for w in words if w not in stopwords_id and len(w) > 2]
word_counts = Counter(filtered)
print("\n[B7] TOP 20 KATA PALING SERING MUNCUL (Setelah Filter):")
for kata, count in word_counts.most_common(20):
    print(f"  '{kata}': {count}x")

# ============================================================
# BAGIAN C: ANALISIS DATA KAWASAN WISATA PRIMER
# ============================================================
try:
    df_kawasan = pd.read_csv('Dataset/jenis_kawasan_wisata_primer_di_kota_bandung_2.csv')
    print("\n\n[C] ANALISIS KAWASAN WISATA PRIMER")
    print("-"*50)
    print(f"Kolom: {df_kawasan.columns.tolist()}")
    print(f"Total: {len(df_kawasan)}")
    print(df_kawasan.head())
except:
    print("\n[C] File kawasan wisata primer tidak ditemukan/error.")

# ============================================================
# BAGIAN D: ANALISIS DATA PERUSAHAAN JASA PERJALANAN
# ============================================================
try:
    df_jasa = pd.read_csv('Dataset/daftar_perusahaan_jasa_perjalanan_wisata_di_kota_bandung.csv')
    print("\n\n[D] ANALISIS PERUSAHAAN JASA PERJALANAN")
    print("-"*50)
    print(f"Kolom: {df_jasa.columns.tolist()}")
    print(f"Total: {len(df_jasa)}")
    print(df_jasa.head(3))
except:
    print("\n[D] File jasa perjalanan tidak ditemukan/error.")

# ============================================================
# BAGIAN E: POTENSI FITUR BARU (Feature Engineering Ideas)
# ============================================================
print("\n\n" + "="*70)
print("POTENSI KEBARUAN & FITUR TAMBAHAN")
print("="*70)

# E1. Price Range Category
df_master['price_range'] = pd.cut(df_master['price_min'], bins=[-1, 0, 15000, 50000, 200000, 1000000],
                                   labels=['Gratis', 'Murah', 'Menengah', 'Premium', 'Eksklusif'])
print("\n[E1] DISTRIBUSI PRICE RANGE (Fitur Baru):")
print(df_master['price_range'].value_counts())

# E2. Review Density (Kepadatan ulasan per lokasi)
review_count = df_reviews.groupby('location_name').size().reset_index(name='review_count')
merged = df_master.merge(review_count, on='location_name', how='left')
merged['review_count'] = merged['review_count'].fillna(0).astype(int)
print("\n[E2] DISTRIBUSI KEPADATAN ULASAN PER LOKASI:")
print(f"  Lokasi tanpa ulasan: {(merged['review_count']==0).sum()}")
print(f"  Lokasi 1-10 ulasan: {((merged['review_count']>=1) & (merged['review_count']<=10)).sum()}")
print(f"  Lokasi 11-50 ulasan: {((merged['review_count']>=11) & (merged['review_count']<=50)).sum()}")
print(f"  Lokasi 50+ ulasan: {(merged['review_count']>=50).sum()}")

# E3. Cross-Analysis: Rating vs Harga
print("\n[E3] KORELASI RATING & HARGA:")
avg_per_loc = df_reviews.groupby('location_name')['rating'].mean().reset_index(name='avg_rating')
cross = df_master.merge(avg_per_loc, on='location_name', how='left')
corr = cross[['price_min', 'avg_rating']].dropna().corr().iloc[0, 1]
print(f"  Korelasi Pearson (price_min vs avg_rating): {corr:.4f}")
if abs(corr) < 0.1:
    print("  Interpretasi: Hampir TIDAK ADA korelasi! (Mahal != Bagus)")
elif corr > 0:
    print("  Interpretasi: Korelasi POSITIF lemah (sedikit lebih mahal = sedikit lebih bagus)")
else:
    print("  Interpretasi: Korelasi NEGATIF (tempat mahal justru lebih sering dikritik)")

print("\n" + "="*70)
print("ANALISIS SELESAI!")
print("="*70)
