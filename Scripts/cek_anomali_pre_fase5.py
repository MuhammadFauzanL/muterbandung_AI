import pandas as pd
import numpy as np

print("="*65)
print("PRE-FASE 5: CEK ANOMALI DATA MASTER_REVIEWS_NLP.csv")
print("="*65)

df = pd.read_csv('Dataset/MASTER_REVIEWS_NLP.csv')

print(f"\nTotal Baris: {len(df)}")
print(f"Kolom: {df.columns.tolist()}")

# ============================================================
# CEK 1: Nilai Null / Missing Value
# ============================================================
print("\n[CEK 1] Missing Values per Kolom:")
null_report = df.isnull().sum()
ada_null = null_report[null_report > 0]
if len(ada_null) == 0:
    print("  ✅ Tidak ada missing value sama sekali!")
else:
    print("  ⚠️  DITEMUKAN MISSING VALUE:")
    print(ada_null.to_string())

# ============================================================
# CEK 2: Kolom review_nlp kosong / terlalu pendek
# ============================================================
print("\n[CEK 2] Kualitas Kolom review_nlp (Hasil Preprocessing):")
df['len_nlp'] = df['review_nlp'].astype(str).apply(len)
kosong_nlp = (df['review_nlp'].astype(str).str.strip() == '').sum()
sangat_pendek = (df['len_nlp'] < 3).sum()
print(f"  review_nlp kosong (hasil preprocessing hilang semua): {kosong_nlp}")
print(f"  review_nlp sangat pendek < 3 karakter (noise): {sangat_pendek}")
print(f"  Rata-rata panjang review_nlp: {df['len_nlp'].mean():.0f} karakter")
print(f"  Terpendek: {df['len_nlp'].min()} karakter | Terpanjang: {df['len_nlp'].max()} karakter")

# Tampilkan 5 contoh yang sangat pendek (jika ada)
if sangat_pendek > 0:
    print("\n  Contoh review_nlp yang terlalu pendek:")
    print(df[df['len_nlp'] < 3][['review_text', 'review_nlp']].head())

# ============================================================
# CEK 3: Distribusi Rating (Apakah masuk akal?)
# ============================================================
print("\n[CEK 3] Distribusi Rating:")
print(df['rating'].value_counts().sort_index().to_string())
print(f"  Min Rating: {df['rating'].min()} | Max Rating: {df['rating'].max()}")
# Cek apakah ada rating di luar skala 1-5
outlier_rating = df[(df['rating'] < 1) | (df['rating'] > 5)]
if len(outlier_rating) > 0:
    print(f"  ⚠️  ADA {len(outlier_rating)} rating di luar skala 1-5!")
else:
    print("  ✅ Semua rating dalam skala 1-5 (normal)")

# ============================================================
# CEK 4: Duplikat tersembunyi
# ============================================================
print("\n[CEK 4] Pengecekan Duplikat Tersembunyi:")
dup = df.duplicated(subset=['location_name', 'reviewer_name', 'review_text'])
print(f"  Jumlah baris duplikat: {dup.sum()}")
if dup.sum() == 0:
    print("  ✅ Tidak ada duplikat tersembunyi!")
else:
    print("  ⚠️  Ada duplikat yang lolos!")

# ============================================================
# CEK 5: Anomali Aspek (Ada ulasan yg tidak terdeteksi aspek apapun)
# ============================================================
print("\n[CEK 5] Ulasan Tanpa Deteksi Aspek Apapun:")
zero_aspek = df[df['jumlah_aspek_terdeteksi'] == 0]
print(f"  Jumlah: {len(zero_aspek)} ulasan ({len(zero_aspek)/len(df)*100:.1f}%)")
print("  Contoh 5 ulasan tanpa aspek (cek manual apakah wajar):")
sample_zero = zero_aspek[['review_text', 'review_nlp']].sample(min(5, len(zero_aspek)), random_state=42)
for i, row in sample_zero.iterrows():
    print(f"    [{i}] '{row['review_text'][:80]}' → NLP: '{row['review_nlp'][:50]}'")

# ============================================================
# CEK 6: Inkonsistensi Nama Lokasi
# ============================================================
print("\n[CEK 6] Nama Lokasi — Cek Inkonsistensi Penulisan:")
lokasi_unik = df['location_name'].unique()
print(f"  Total lokasi unik: {len(lokasi_unik)}")
# Cari potensi duplikat nama (case sensitivity)
lower_counts = pd.Series([l.lower() for l in lokasi_unik])
dup_lower = lower_counts[lower_counts.duplicated()]
if len(dup_lower) > 0:
    print(f"  ⚠️  Potensi inkonsistensi kapitalisasi ditemukan: {dup_lower.tolist()}")
else:
    print("  ✅ Tidak ada inkonsistensi penulisan nama lokasi!")

# ============================================================
# CEK 7: Distribusi Sumber Data (Apakah seimbang?)
# ============================================================
print("\n[CEK 7] Distribusi Sumber Data:")
print(df['source_file'].value_counts().to_string())

# ============================================================
# RINGKASAN
# ============================================================
print("\n" + "="*65)
print("RINGKASAN AUDIT DATA PRE-FASE 5")
print("="*65)
