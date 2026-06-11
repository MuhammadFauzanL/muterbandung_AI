import json

# 1. Baca semua 179 URL asli
with open('apify_reviews_only.json', 'r', encoding='utf-8') as f:
    semua_url = json.load(f)['startUrls']

# 2. Baca 13 lokasi yang SUDAH BERHASIL (agar tidak double/buang kuota)
path_hasil_raksasa = r'c:\Users\M Fauzan Lubada\Downloads\Penginapan-20260516T043918Z-3-001\dataset_Google-Maps-Reviews-Scraper_2026-05-17_08-49-58-993.json'
with open(path_hasil_raksasa, 'r', encoding='utf-8') as f:
    data_selesai = json.load(f)

# Ambil nama-nama yang sudah selesai
lokasi_selesai = set([item.get('title') for item in data_selesai if item.get('title')])

# 3. Filter URL yang BUKAN bagian dari lokasi_selesai
url_sisa = []
for u in semua_url:
    # Cek apakah nama URL ini ada di daftar yang sudah selesai
    # (Cara kasarnya, kita cocokkan sedikit string urlnya, tapi lebih aman simpan semua sisa yang urlnya tidak ada di data_selesai)
    
    # Kumpulkan semua URL yang sudah discrape
    url_selesai = set([item.get('url') for item in data_selesai if item.get('url')])
    
    if u['url'] not in url_selesai:
        url_sisa.append(u)

# 4. Buat payload baru dengan Parameter Pembatas yang BENAR
payload_baru = {
  "startUrls": url_sisa,
  "maxReviews": 30,  # INI KUNCI AGAR TIDAK SERAKAH (Bukan maxReviewsPerPlace)
  "language": "id",
  "reviewsSort": "newest"
}

with open('apify_sisa_lokasi.json', 'w', encoding='utf-8') as f:
    json.dump(payload_baru, f, indent=2)

print(f"Dari 179 lokasi, 13 sudah selesai.")
print(f"Tersisa {len(url_sisa)} lokasi lagi.")
print("File apify_sisa_lokasi.json berhasil dibuat!")
