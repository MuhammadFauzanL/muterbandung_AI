import json

# Muat kembali semua URL dari file awal
path_json_lama = 'apify_reviews_only.json'
with open(path_json_lama, 'r', encoding='utf-8') as f:
    data = json.load(f)

semua_url = data['startUrls']

# Bagi menjadi 2 kelompok
batch_1 = semua_url[:90]
batch_2 = semua_url[90:]

# Template payload
def buat_payload(urls):
    return {
        "startUrls": urls,
        "maxReviewsPerPlace": 30, # Tarik 30 komentar saja per tempat
        "language": "id",
        "reviewsSort": "newest"
    }

# Simpan Batch 1
with open('apify_batch_1.json', 'w', encoding='utf-8') as f:
    json.dump(buat_payload(batch_1), f, indent=2)

# Simpan Batch 2
with open('apify_batch_2.json', 'w', encoding='utf-8') as f:
    json.dump(buat_payload(batch_2), f, indent=2)

print(f"File berhasil dibuat!")
print(f"Batch 1: {len(batch_1)} lokasi")
print(f"Batch 2: {len(batch_2)} lokasi")
