import pandas as pd
import json

# 1. Baca database utama kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# 2. Ambil seluruh nama lokasi (232 data)
search_strings = []
for nama in df['location_name']:
    search_strings.append(f"{nama} Bandung Jawa Barat")

# 3. Bentuk JSON sesuai template Extractor yang Anda berikan
apify_extractor_payload = {
    "includeWebResults": False,
    "language": "id",               # Ubah ke bahasa Indonesia
    "locationQuery": "",            # Kosongkan karena kota sudah ada di nama
    "maxCrawledPlacesPerSearch": 1, # Pastikan hanya ambil 1 hasil paling relevan
    "maximumLeadsEnrichmentRecords": 0,
    "scrapeContacts": False,
    "scrapeDirectories": False,
    "scrapeOrderOnline": False,
    "scrapePlaceDetailPage": True,  # INI YANG PALING PENTING AGAR JAM BUKA DIAMBIL
    "scrapeSocialMediaProfiles": {
        "facebooks": False,
        "instagrams": False,
        "tiktoks": False,
        "twitters": False,
        "youtubes": False
    },
    "scrapeTableReservationProvider": False,
    "searchStringsArray": search_strings, # Masukkan 232 daftar lokasi kita
    "skipClosedPlaces": False,
    "verifyLeadsEnrichmentEmails": False
}

# 4. Simpan menjadi file JSON yang siap di-Copy-Paste
output_path = 'Apify_Workspace/Inputs/apify_extractor_full_config.json'
with open(output_path, 'w') as f:
    json.dump(apify_extractor_payload, f, indent=4)

print(f"Berhasil! File JSON siap pakai telah dibuat di: {output_path}")
