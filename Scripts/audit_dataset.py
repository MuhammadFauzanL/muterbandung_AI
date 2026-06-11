import pandas as pd
import os
import glob

print("=" * 70)
print("  AUDIT KOMPREHENSIF DATASET PROYEK PIJAK")
print("  Tanggal: 19 Mei 2026")
print("=" * 70)

# ============================================================
# 1. DATASET REVIEW UTAMA
# ============================================================
print("\n[1] DATASET REVIEW UTAMA (MASTER_REVIEWS_ENRICHED.csv)")
print("-" * 70)
df_reviews = pd.read_csv("Dataset/MASTER_REVIEWS_ENRICHED.csv")
print(f"Total baris review        : {len(df_reviews):,}")
print(f"Kolom yang ada            : {list(df_reviews.columns)}")

per_lokasi = df_reviews.groupby("location_name").size()
print(f"\nTotal lokasi unik         : {len(per_lokasi)}")
print(f"Rata-rata review/lokasi   : {per_lokasi.mean():.1f}")
print(f"Median review/lokasi      : {per_lokasi.median():.1f}")
print(f"Min review                : {per_lokasi.min()}")
print(f"Max review                : {per_lokasi.max()}")
print(f"\nDistribusi Jumlah Review:")
print(f"  >= 100 review           : {(per_lokasi >= 100).sum()} lokasi")
print(f"  50-99 review            : {((per_lokasi >= 50) & (per_lokasi < 100)).sum()} lokasi")
print(f"  30-49 review            : {((per_lokasi >= 30) & (per_lokasi < 50)).sum()} lokasi")
print(f"  10-29 review            : {((per_lokasi >= 10) & (per_lokasi < 30)).sum()} lokasi")
print(f"  < 10 review             : {(per_lokasi < 10).sum()} lokasi")

# Cek kolom sentimen
print(f"\nKelengkapan Kolom Penting:")
rating_filled = df_reviews["rating"].notna().sum()
text_filled = df_reviews["review_text"].notna().sum()
text_empty = df_reviews["review_text"].isna().sum()
print(f"  rating terisi           : {rating_filled:,} / {len(df_reviews):,}")
print(f"  review_text terisi      : {text_filled:,} / {len(df_reviews):,} ({text_empty:,} kosong)")

for col in ["sentiment", "sentiment_label", "aspect_category", "aspect_sentiment"]:
    if col in df_reviews.columns:
        filled = df_reviews[col].notna().sum()
        empty = df_reviews[col].isna().sum()
        print(f"  {col:25s}: {filled:,} terisi | {empty:,} kosong")

# ============================================================
# 2. DATASET REVIEW BERLABEL (ASLI)
# ============================================================
print("\n\n[2] DATASET REVIEW BERLABEL (MASTER_REVIEWS_LABELED.csv)")
print("-" * 70)
if os.path.exists("Dataset/MASTER_REVIEWS_LABELED.csv"):
    df_labeled = pd.read_csv("Dataset/MASTER_REVIEWS_LABELED.csv")
    print(f"Total baris               : {len(df_labeled):,}")
    print(f"Kolom                     : {list(df_labeled.columns)}")
    for col in ["sentiment", "sentiment_label", "aspect_category", "aspect_sentiment"]:
        if col in df_labeled.columns:
            filled = df_labeled[col].notna().sum()
            print(f"  {col:25s}: {filled:,} terisi")
else:
    print("  FILE TIDAK DITEMUKAN")

# ============================================================
# 3. DATABASE WISATA UTAMA
# ============================================================
print("\n\n[3] DATABASE WISATA UTAMA (DATABASE_WISATA_FINAL_LENGKAP.csv)")
print("-" * 70)
if os.path.exists("DATABASE_WISATA_FINAL_LENGKAP.csv"):
    df_wisata = pd.read_csv("DATABASE_WISATA_FINAL_LENGKAP.csv")
    print(f"Total lokasi wisata       : {len(df_wisata)}")
    print(f"Kolom                     : {list(df_wisata.columns)}")
    for col in df_wisata.columns:
        filled = df_wisata[col].notna().sum()
        empty = df_wisata[col].isna().sum()
        if empty > 0:
            print(f"  {col:25s}: {filled} terisi | {empty} kosong")
else:
    print("  FILE TIDAK DITEMUKAN")

# ============================================================
# 4. DATABASE WISATA DENGAN METADATA
# ============================================================
print("\n\n[4] DATABASE WISATA DENGAN METADATA")
print("-" * 70)
if os.path.exists("DATABASE_WISATA_DENGAN_METADATA.csv"):
    df_meta = pd.read_csv("DATABASE_WISATA_DENGAN_METADATA.csv")
    print(f"Total lokasi              : {len(df_meta)}")
    print(f"Kolom                     : {list(df_meta.columns)}")
    for col in df_meta.columns:
        filled = df_meta[col].notna().sum()
        empty = df_meta[col].isna().sum()
        if empty > 0:
            print(f"  {col:25s}: {filled} terisi | {empty} kosong")
else:
    print("  FILE TIDAK DITEMUKAN")

# ============================================================
# 5. TEMPLATE SCRAPER MURNI (UNTUK AI AGENT)
# ============================================================
print("\n\n[5] TEMPLATE SCRAPER MURNI (template_scraper_murni.csv)")
print("-" * 70)
template_path = "Apify_Workspace/Inputs/template_scraper_murni.csv"
if os.path.exists(template_path):
    df_template = pd.read_csv(template_path)
    print(f"Total lokasi              : {len(df_template)}")
    print(f"Kolom                     : {list(df_template.columns)}")
    for col in df_template.columns:
        filled = df_template[col].notna().sum()
        empty = df_template[col].isna().sum()
        pct = filled / len(df_template) * 100
        print(f"  {col:25s}: {filled}/{len(df_template)} ({pct:.0f}%) terisi")
else:
    print("  FILE TIDAK DITEMUKAN")

# ============================================================
# 6. DATA GOOGLE MAPS EXTRACTOR (METADATA TEMPAT)
# ============================================================
print("\n\n[6] DATA GOOGLE MAPS EXTRACTOR")
print("-" * 70)
extractor_path = "dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv"
if os.path.exists(extractor_path):
    df_ext = pd.read_csv(extractor_path)
    print(f"Total lokasi              : {len(df_ext)}")
    print(f"Kolom                     : {list(df_ext.columns)}")
    for col in df_ext.columns:
        filled = df_ext[col].notna().sum()
        empty = df_ext[col].isna().sum()
        if empty > 0:
            print(f"  {col:25s}: {filled} terisi | {empty} kosong")
else:
    print("  FILE TIDAK DITEMUKAN")

# ============================================================
# 7. CROSS-CHECK: Lokasi di Review vs Database Wisata
# ============================================================
print("\n\n[7] CROSS-CHECK: LOKASI DI REVIEW vs DATABASE WISATA")
print("-" * 70)
if os.path.exists("DATABASE_WISATA_FINAL_LENGKAP.csv"):
    df_wisata = pd.read_csv("DATABASE_WISATA_FINAL_LENGKAP.csv")
    lokasi_review = set(df_reviews["location_name"].unique())
    lokasi_wisata = set(df_wisata["location_name"].unique())
    
    di_review_tapi_bukan_wisata = lokasi_review - lokasi_wisata
    di_wisata_tapi_tanpa_review = lokasi_wisata - lokasi_review
    keduanya = lokasi_review & lokasi_wisata
    
    print(f"Lokasi di kedua dataset    : {len(keduanya)}")
    print(f"Di review tapi bukan wisata: {len(di_review_tapi_bukan_wisata)}")
    if di_review_tapi_bukan_wisata:
        for loc in sorted(di_review_tapi_bukan_wisata)[:10]:
            print(f"  - {loc}")
    print(f"Di wisata tapi tanpa review: {len(di_wisata_tapi_tanpa_review)}")
    if di_wisata_tapi_tanpa_review:
        for loc in sorted(di_wisata_tapi_tanpa_review)[:10]:
            print(f"  - {loc}")

# ============================================================
# 8. BATCH SCRAPING YANG MASIH TERSISA
# ============================================================
print("\n\n[8] BATCH SCRAPING YANG MASIH TERSISA")
print("-" * 70)
batch_dir = "Apify_Workspace/Inputs/Batches"
if os.path.exists(batch_dir):
    batch_files = sorted(glob.glob(os.path.join(batch_dir, "*.json")))
    print(f"Jumlah file batch         : {len(batch_files)}")
    
    import json
    total_urls = 0
    for bf in batch_files:
        with open(bf, "r") as f:
            config = json.load(f)
        urls = config.get("startUrls", [])
        total_urls += len(urls)
        print(f"  {os.path.basename(bf):45s}: {len(urls)} lokasi")
    print(f"Total lokasi belum discrape: {total_urls}")

# ============================================================
# 9. RINGKASAN PROGRESS KESELURUHAN
# ============================================================
print("\n\n" + "=" * 70)
print("  RINGKASAN PROGRESS KESELURUHAN")
print("=" * 70)
print(f"  Total Review Unik       : {len(df_reviews):,} baris")
print(f"  Total Lokasi Wisata     : {len(per_lokasi)} lokasi")
print(f"  Lokasi >= 50 Review     : {(per_lokasi >= 50).sum()} ({(per_lokasi >= 50).sum()/len(per_lokasi)*100:.1f}%)")
print(f"  Lokasi < 50 Review      : {(per_lokasi < 50).sum()} ({(per_lokasi < 50).sum()/len(per_lokasi)*100:.1f}%)")

# Hitung review dengan teks vs tanpa teks
with_text = df_reviews["review_text"].notna().sum()
without_text = df_reviews["review_text"].isna().sum()
print(f"  Review dengan teks      : {with_text:,} ({with_text/len(df_reviews)*100:.1f}%)")
print(f"  Review tanpa teks       : {without_text:,} ({without_text/len(df_reviews)*100:.1f}%)")

print("\n" + "=" * 70)
print("  DAFTAR PEKERJAAN YANG MASIH HARUS DISELESAIKAN")
print("=" * 70)
print("  [1] Scraping Batch 1-5 review tambahan (100 lokasi @ 20 per batch)")
print("  [2] Klasifikasi Sentimen NLP untuk review baru (~6,347 review)")
print("  [3] Pengisian Metadata (Jam Buka/Tutup, Deskripsi, Tags) via AI Agent")
print("  [4] Pembersihan data final & quality check sebelum modeling")
print("  [5] Pembuatan model rekomendasi wisata")
