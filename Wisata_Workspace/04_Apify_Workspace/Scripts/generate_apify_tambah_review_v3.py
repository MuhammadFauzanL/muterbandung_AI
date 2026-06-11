import pandas as pd
import json

# 1. Baca data lokasi yang masih di bawah 50 review saat ini
df_enriched = pd.read_csv('Dataset/MASTER_REVIEWS_ENRICHED.csv')
per_lokasi = df_enriched.groupby('location_name').size()
kurang_50 = per_lokasi[per_lokasi < 50].reset_index()
kurang_50.columns = ['location_name', 'review_count']

print(f"Total lokasi yang masih di bawah 50 review: {len(kurang_50)}")

# 2. Baca data dari Google Maps Extractor untuk mencocokkan URL
df_extractor = pd.read_csv('dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv')
extractor_map = df_extractor.set_index('title')['url'].to_dict()

# 3. Buat daftar target URL
target_list = []
matched_count = 0
unmatched_count = 0

for _, row in kurang_50.iterrows():
    loc_name = row['location_name']
    
    # Cari URL Google Maps
    if loc_name in extractor_map and pd.notna(extractor_map[loc_name]):
        target_list.append(extractor_map[loc_name])
        matched_count += 1
    else:
        # Fallback pencarian spesifik
        if "Kampung toga" in loc_name or "villa pancing" in loc_name:
            target_list.append("Kampung Toga Sumedang Jawa Barat")
        elif "Gn. Hawu" in loc_name:
            target_list.append("Tebing Gunung Hawu Padalarang Jawa Barat")
        elif "Nimo Resort" in loc_name:
            target_list.append("NIMO Highland Ciwidey Bandung Jawa Barat")
        else:
            target_list.append(f"{loc_name} Bandung Jawa Barat")
        unmatched_count += 1

print(f"Berhasil memetakan URL langsung: {matched_count}")
print(f"Menggunakan Search Query (Fallback): {unmatched_count}")

# 4. Buat konfigurasi JSON V3 (Fokus 113 lokasi saja)
apify_config_v3 = {
    "language": "id",
    "maxReviews": 50,                  # Ambil 50 review saja per lokasi biar hemat kuota Apify
    "maxCrawledPlacesPerSearch": 1,
    "reviewsSort": "newest",
    "scrapePlaceDetailPage": False,
    "includeWebResults": False,
    "skipClosedPlaces": False,
    "searchStringsArray": target_list
}

# Simpan ke file config v3
output_path = 'Apify_Workspace/Inputs/apify_tambah_review_config_v3.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(apify_config_v3, f, indent=4, ensure_ascii=False)

print(f"\n[SUKSES] Konfigurasi V3 disimpan ke: {output_path}")
