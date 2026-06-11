import json

path = r'c:\Users\M Fauzan Lubada\Downloads\Penginapan-20260516T043918Z-3-001\dataset_fauszan_2026-05-17_09-30-30-039 (1).json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"File Berhasil Dibaca!")
print(f"Total ulasan (mentah): {len(data)}")

lokasi_unik = set([item.get('title') for item in data if 'title' in item])
print(f"Total Lokasi yang berhasil ditarik: {len(lokasi_unik)}")

ada_teks = [item for item in data if item.get('text')]
print(f"Total ulasan ber-teks (siap NLP): {len(ada_teks)}")

print("\n--- 5 Lokasi Pertama ---")
for loc in list(lokasi_unik)[:5]:
    print(f"- {loc}")
