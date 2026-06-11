import pandas as pd
import json

# Baca database wisata kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Ambil 5 NAMA LOKASI PERTAMA saja untuk testing
search_queries = []
for nama in df['location_name'].head(5):
    search_queries.append({"search": f"{nama} Bandung Jawa Barat"})

# Simpan ke format JSON khusus testing (apify_10_lokasi_test.json)
with open('apify_5_lokasi_test.json', 'w') as f:
    json.dump(search_queries, f, indent=4)

print("Berhasil! File apify_5_lokasi_test.json sudah dibuat khusus untuk testing 5 lokasi.")
