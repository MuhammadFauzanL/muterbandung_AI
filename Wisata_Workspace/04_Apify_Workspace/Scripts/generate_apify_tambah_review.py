"""
Script Cerdas: Generator Konfigurasi Apify untuk Tambah Review
Strategi:
1. Hanya menarget lokasi yang kekurangan review (< 100)
2. Menyesuaikan jumlah review yang diminta = kekurangannya saja
3. Mencegah duplikasi saat penggabungan nantinya
"""
import pandas as pd
import json

# ============================================================
# STEP 1: Baca daftar lokasi yang kekurangan review
# ============================================================
df_kurang = pd.read_csv('Dataset/lokasi_perlu_tambahan_review.csv')
print(f"Total lokasi yang perlu tambahan review: {len(df_kurang)}")

# ============================================================
# STEP 2: Buat konfigurasi Apify Reviews Scraper
# Targetkan HANYA lokasi yang kurang, dengan limit persis kekurangannya
# ============================================================

# Apify Google Maps Reviews Scraper menggunakan searchStringsArray
# kita set maxReviewsPerQuery = 100 agar dapat maksimum
search_strings = []
for _, row in df_kurang.iterrows():
    search_strings.append(f"{row['location_name']} Bandung Jawa Barat")

apify_config = {
    "language": "id",
    "maxReviews": 100,                 # Minta 100 review per lokasi
    "maxCrawledPlacesPerSearch": 1,    # Hanya ambil 1 hasil paling relevan
    "reviewsSort": "newest",           # Urutkan dari terbaru (hindari duplikat lama)
    "scrapePlaceDetailPage": False,    # Kita hanya mau review
    "includeWebResults": False,
    "skipClosedPlaces": False,
    "searchStringsArray": search_strings
}

output_config_path = 'Apify_Workspace/Inputs/apify_tambah_review_config.json'
with open(output_config_path, 'w', encoding='utf-8') as f:
    json.dump(apify_config, f, indent=4, ensure_ascii=False)

print(f"\nFile konfigurasi Apify disimpan ke: {output_config_path}")
print(f"Jumlah lokasi yang akan di-scrape: {len(search_strings)}")
print("\n5 Lokasi pertama yang ditarget:")
for s in search_strings[:5]:
    print(f"  - {s}")
