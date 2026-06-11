import pandas as pd
import json
import os

# 1. Baca data lokasi yang masih di bawah 50 review saat ini
df_enriched = pd.read_csv('Dataset/MASTER_REVIEWS_ENRICHED.csv')
per_lokasi = df_enriched.groupby('location_name').size()
kurang_50 = per_lokasi[per_lokasi < 50].reset_index()
kurang_50.columns = ['location_name', 'review_count']

print(f"Total lokasi di bawah 50 review: {len(kurang_50)}")

# 2. Baca data dari Google Maps Extractor untuk mencocokkan URL
df_extractor = pd.read_csv('dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv')
extractor_map = df_extractor.set_index('title')['url'].to_dict()

# 3. Buat daftar target dalam format searchStringsArray (berisi string URL langsung)
search_strings = []
for _, row in kurang_50.iterrows():
    loc_name = row['location_name']
    
    if loc_name in extractor_map and pd.notna(extractor_map[loc_name]):
        url_target = extractor_map[loc_name]
    else:
        # Fallback pencarian manual dengan link Google Maps query
        import urllib.parse
        encoded_name = urllib.parse.quote(loc_name)
        if "Kampung toga" in loc_name or "villa pancing" in loc_name:
            url_target = "https://www.google.com/maps/search/?api=1&query=Kampung%20Toga%20Sumedang%20Jawa%20Barat"
        elif "Gn. Hawu" in loc_name:
            url_target = "https://www.google.com/maps/search/?api=1&query=Tebing%20Gunung%20Hawu%20Padalarang%20Jawa%20Barat"
        elif "Nimo Resort" in loc_name:
            url_target = "https://www.google.com/maps/search/?api=1&query=NIMO%20Highland%20Ciwidey%20Bandung%20Jawa%20Barat"
        else:
            url_target = f"https://www.google.com/maps/search/?api=1&query={encoded_name}%20Bandung%20Jawa%20Barat"
            
    search_strings.append(url_target)

# 4. Bagi menjadi 6 batch (masing-masing ~20 lokasi)
batch_size = 20
batches = [search_strings[i:i + batch_size] for i in range(0, len(search_strings), batch_size)]

print(f"Membagi menjadi {len(batches)} batch (masing-masing ~20 lokasi).")

# Buat folder jika belum ada
os.makedirs('Apify_Workspace/Inputs/Batches', exist_ok=True)

# Generate JSON untuk setiap batch dengan schema Apify yang benar
for idx, batch_urls in enumerate(batches):
    batch_config = {
        "language": "id",
        "maxReviews": 100,
        "maxCrawledPlacesPerSearch": 1,
        "reviewsSort": "newest",
        "scrapePlaceDetailPage": False,
        "includeWebResults": False,
        "skipClosedPlaces": False,
        "searchStringsArray": batch_urls
    }
    
    file_path = f'Apify_Workspace/Inputs/Batches/apify_tambah_review_batch_{idx+1}.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(batch_config, f, indent=4, ensure_ascii=False)
    print(f"  -> Terbuat: {file_path} (Berisi {len(batch_urls)} lokasi)")

print("\n[SUKSES] Semua file batch dengan skema searchStringsArray yang benar telah diperbarui.")
