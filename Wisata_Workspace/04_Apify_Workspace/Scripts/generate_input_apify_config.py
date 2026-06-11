import pandas as pd
import json

# Baca database wisata kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Ambil 5 NAMA LOKASI PERTAMA saja untuk testing
search_strings = []
for nama in df['location_name'].head(5):
    search_strings.append(f"{nama} Bandung Jawa Barat")

# Buat payload MENGGUNAKAN TEMPLATE DEFAULT DARI USER
apify_payload = {
    "includeWebResults": False,
    "language": "id",
    "locationQuery": "",
    "maxCrawledPlacesPerSearch": 1,         # HANYA AMBIL 1 HASIL TERATAS
    "maximumLeadsEnrichmentRecords": 0,
    "scrapeContacts": False,
    "scrapeDirectories": False,
    "scrapeImageAuthors": False,
    "scrapeOrderOnline": False,
    "scrapePlaceDetailPage": True,          # INI KUNCI UTAMANYA (HARUS TRUE)
    "scrapeReviewsPersonalData": False,     # MATIKAN AGAR CEPAT
    "scrapeSocialMediaProfiles": {
        "facebooks": False,
        "instagrams": False,
        "tiktoks": False,
        "twitters": False,
        "youtubes": False
    },
    "scrapeTableReservationProvider": False,
    "searchStringsArray": search_strings,
    "skipClosedPlaces": False,
    "verifyLeadsEnrichmentEmails": False
}

# Simpan ke format JSON khusus testing (apify_5_lokasi_test_config.json)
with open('Apify_Workspace/Inputs/apify_5_lokasi_test_config.json', 'w') as f:
    json.dump(apify_payload, f, indent=4)

print("Berhasil! File JSON baru sudah disesuaikan dengan template asli Apify.")
