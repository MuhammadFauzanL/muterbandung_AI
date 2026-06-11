import pandas as pd
import json

# 1. Baca data lokasi yang masih kurang
df_sisa = pd.read_csv('Dataset/lokasi_yang_masih_kurang_final.csv')
print(f"Total lokasi masih kurang review: {len(df_sisa)}")

# 2. Baca data dari Google Maps Extractor untuk mencocokkan URL
df_extractor = pd.read_csv('dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv')

# Buat mapping nama -> url
extractor_map = df_extractor.set_index('title')['url'].to_dict()

# 3. Buat daftar target (Bisa berupa URL Google Maps atau search query string)
target_list = []
matched_count = 0
unmatched_count = 0

for _, row in df_sisa.iterrows():
    loc_name = row['location_name']
    
    # Coba cari URL langsung dari Extractor
    if loc_name in extractor_map and pd.notna(extractor_map[loc_name]):
        target_list.append(extractor_map[loc_name])
        matched_count += 1
    else:
        # Fallback manual untuk nama-nama yang tidak pas kecocokannya
        if "Kampung toga" in loc_name or "villa pancing" in loc_name:
            target_list.append("Kampung Toga Sumedang Jawa Barat")
        elif "Gn. Hawu" in loc_name:
            target_list.append("Tebing Gunung Hawu Padalarang Jawa Barat")
        elif "Nimo Resort" in loc_name:
            target_list.append("NIMO Highland Ciwidey Bandung Jawa Barat")
        else:
            # Fallback umum: gunakan pencarian nama asli + Bandung Jawa Barat
            target_list.append(f"{loc_name} Bandung Jawa Barat")
        unmatched_count += 1

print(f"Berhasil memetakan URL langsung: {matched_count}")
print(f"Menggunakan Search Query (Fallback): {unmatched_count}")

# 4. Buat konfigurasi JSON baru untuk Apify Google Maps Reviews Scraper
apify_config_v2 = {
    "language": "id",
    "maxReviews": 100,                 # Minta 100 ulasan per tempat
    "maxCrawledPlacesPerSearch": 1,    # Hanya 1 tempat per pencarian
    "reviewsSort": "newest",           # Ambil review terbaru agar melengkapi yang kurang
    "scrapePlaceDetailPage": False,    # Kita tidak butuh detail page, hanya review
    "includeWebResults": False,
    "skipClosedPlaces": False,
    "searchStringsArray": target_list  # Array berisi campuran URL Maps langsung & query string
}

# Simpan ke file config v2
output_path = 'Apify_Workspace/Inputs/apify_tambah_review_config_v2.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(apify_config_v2, f, indent=4, ensure_ascii=False)

print(f"\n[BERHASIL] Konfigurasi baru disimpan ke: {output_path}")
