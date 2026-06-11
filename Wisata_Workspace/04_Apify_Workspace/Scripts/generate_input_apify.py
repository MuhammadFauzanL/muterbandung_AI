import pandas as pd
import json

# Baca database wisata kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Ambil nama lokasi dan tambahkan kata kunci pencarian agar akurat di Google Maps
search_queries = []
for nama in df['location_name']:
    search_queries.append({"search": f"{nama} Bandung Jawa Barat"})

# Simpan ke format JSON untuk di-copy ke Apify
with open('input_tambahan_apify.json', 'w') as f:
    json.dump(search_queries, f, indent=4)

print("Berhasil! File input_tambahan_apify.json sudah dibuat dengan 232 lokasi.")
