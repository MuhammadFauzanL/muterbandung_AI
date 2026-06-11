"""
Script Deduplikasi Cerdas: Gabungkan Review Baru + Lama Tanpa Duplikat

Cara kerja:
1. Baca dataset review LAMA (yang sudah ada label sentimennya)
2. Baca dataset review BARU (hasil scrape Apify terbaru)
3. Gabungkan dan buang duplikat berdasarkan (location_name + review_text)
4. Simpan hasilnya ke file baru (TIDAK menimpa file lama)
"""
import pandas as pd
import sys

# ============================================================
# KONFIGURASI: Ganti path file baru sesuai hasil download Apify
# ============================================================
FILE_REVIEW_LAMA = 'Dataset/MASTER_REVIEWS_LABELED.csv'
FILE_REVIEW_BARU = 'Dataset/apify_reviews_tambahan.csv'  # <-- Ganti dengan file hasil download Apify Anda
FILE_OUTPUT      = 'Dataset/MASTER_REVIEWS_ENRICHED.csv'  # File gabungan (TIDAK menimpa file lama)

# ============================================================
# STEP 1: Baca data lama
# ============================================================
try:
    df_lama = pd.read_csv(FILE_REVIEW_LAMA)
    print(f"[OK] Data LAMA dibaca: {len(df_lama):,} baris")
except FileNotFoundError:
    print(f"[ERROR] File lama tidak ditemukan: {FILE_REVIEW_LAMA}")
    sys.exit(1)

# ============================================================
# STEP 2: Baca data baru (hasil Apify terbaru)
# ============================================================
try:
    df_baru = pd.read_csv(FILE_REVIEW_BARU)
    print(f"[OK] Data BARU dibaca: {len(df_baru):,} baris")
except FileNotFoundError:
    print(f"[SKIP] File baru tidak ditemukan: {FILE_REVIEW_BARU}")
    print("       Jalankan script ini lagi setelah download hasil Apify Anda.")
    sys.exit(0)

# ============================================================
# STEP 3: Normalisasi kolom data baru (sesuaikan dengan format lama)
# ============================================================
# Apify Google Maps Reviews biasanya punya kolom: text, stars, title, reviewUrl
# Kita map ke format yang kita punya
kolom_mapping = {
    'title': 'location_name',
    'text': 'review_text',
    'stars': 'rating',
    'name': 'reviewer_name',
}
df_baru = df_baru.rename(columns=kolom_mapping)

# Pastikan kolom yang dibutuhkan ada
for kolom in ['location_name', 'review_text', 'rating']:
    if kolom not in df_baru.columns:
        print(f"[WARNING] Kolom '{kolom}' tidak ada di data baru. Mungkin format Apify berbeda.")
        print(f"  Kolom yang tersedia: {list(df_baru.columns)}")

# ============================================================
# STEP 4: Gabungkan dan buang duplikat
# ============================================================
print("\n--- Proses Penggabungan ---")

# Tandai sumber data
df_lama['sumber'] = 'lama'
df_baru['sumber'] = 'baru'

df_gabung = pd.concat([df_lama, df_baru], ignore_index=True)
print(f"Total sebelum dedup : {len(df_gabung):,} baris")

# Kunci deduplikasi: nama lokasi + isi review (bersihkan spasi dulu)
df_gabung['_key_dedup'] = (
    df_gabung['location_name'].astype(str).str.strip().str.lower() + '|' +
    df_gabung['review_text'].astype(str).str.strip().str.lower()
)

# Pertahankan data LAMA jika ada duplikat (karena sudah ada label sentimen)
df_gabung = df_gabung.sort_values('sumber', ascending=True)  # 'baru' > 'lama' alphabetically
df_bersih = df_gabung.drop_duplicates(subset='_key_dedup', keep='last')  # keep='last' = keep 'lama'
df_bersih = df_bersih.drop(columns=['_key_dedup', 'sumber'])

print(f"Total setelah dedup : {len(df_bersih):,} baris")
print(f"Duplikat dibuang    : {len(df_gabung) - len(df_bersih):,} baris")

# ============================================================
# STEP 5: Analisis hasil per lokasi
# ============================================================
print("\n--- Distribusi Review Baru per Lokasi ---")
per_lokasi_baru = df_bersih.groupby('location_name').size()
print(f"Rata-rata review/lokasi : {per_lokasi_baru.mean():.1f}")
print(f"Lokasi dengan >= 100    : {(per_lokasi_baru >= 100).sum()}")

# ============================================================
# STEP 6: Simpan ke file baru (TIDAK menimpa file lama)
# ============================================================
df_bersih.to_csv(FILE_OUTPUT, index=False)
print(f"\n[BERHASIL] File gabungan disimpan ke: {FILE_OUTPUT}")
print(f"File LAMA tetap aman di: {FILE_REVIEW_LAMA}")
