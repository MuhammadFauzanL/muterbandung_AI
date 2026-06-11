import json
import pandas as pd

path = r'c:\Users\M Fauzan Lubada\Downloads\Penginapan-20260516T043918Z-3-001\dataset_Google-Maps-Reviews-Scraper_2026-05-17_08-38-55-266 (1).json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total komentar/ulasan yang ditarik: {len(data)}")

# Cek berapa banyak lokasi yang berhasil ditarik
lokasi = set([item.get('title') for item in data if 'title' in item])
print(f"Total lokasi unik: {len(lokasi)}")

# Kita lihat beberapa contoh ulasan yang memiliki teks (bukan null)
ada_teks = [item for item in data if item.get('text')]
print(f"Total ulasan yang memiliki teks panjang: {len(ada_teks)}")
print("\n=== CONTOH ULASAN TERBARU ===")
for i in range(min(3, len(ada_teks))):
    print(f"Lokasi : {ada_teks[i].get('title')}")
    print(f"Bintang: {ada_teks[i].get('stars')}⭐")
    print(f"Review : {ada_teks[i].get('text')}")
    print("-" * 50)
