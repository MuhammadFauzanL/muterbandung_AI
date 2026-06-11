import json

# Baca file JSON yang baru saja user kasih (yang berisi URL asli)
path = r'c:\Users\M Fauzan Lubada\Downloads\Penginapan-20260516T043918Z-3-001\dataset_crawler-google-places_2026-05-17_08-13-57-600.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Ekstrak URL-nya saja
urls = []
for place in data:
    if 'url' in place and place['url']:
        urls.append(place['url'])

# Buat format JSON untuk 'Google Maps Reviews Scraper'
payload = {
  "startUrls": [{"url": u} for u in urls],
  "maxReviewsPerPlace": 30,
  "language": "id",
  "reviewsSort": "newest"
}

with open('apify_reviews_only.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)

print(f"Berhasil mengekstrak {len(urls)} URL rahasia!")
