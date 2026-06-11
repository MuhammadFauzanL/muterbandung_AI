import json

# Baca file txt yang sebelumnya
with open('daftar_lokasi_untuk_apify.txt', 'r', encoding='utf-8') as f:
    lokasi_list = [line.strip() for line in f if line.strip()]

# Buat format JSON yang dipahami Apify
apify_payload = {
  "searchStringsArray": lokasi_list,
  "language": "id",
  "maxCrawledPlacesPerSearch": 1,
  "extractReviews": True,
  "reviewsMaxRetrieved": 30
}

# Simpan sebagai JSON
with open('apify_input_langsung.json', 'w', encoding='utf-8') as f:
    json.dump(apify_payload, f, indent=2, ensure_ascii=False)

print("File apify_input_langsung.json berhasil dibuat!")
