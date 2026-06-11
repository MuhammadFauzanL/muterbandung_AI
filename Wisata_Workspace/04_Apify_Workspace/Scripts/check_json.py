import json

path = r'c:\Users\M Fauzan Lubada\Downloads\Penginapan-20260516T043918Z-3-001\dataset_crawler-google-places_2026-05-17_07-37-40-569.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'Total lokasi di JSON: {len(data)}')
has_reviews = 0
for place in data:
    if 'reviews' in place:
        has_reviews += 1

print(f'Lokasi yang memiliki array reviews: {has_reviews}')

if has_reviews > 0:
    first_with_reviews = next(p for p in data if 'reviews' in p)
    print(f'Contoh: {first_with_reviews["title"]} memiliki {len(first_with_reviews["reviews"])} ulasan')
else:
    print('TIDAK ADA REVIEWS SAMA SEKALI DI FILE INI.')
