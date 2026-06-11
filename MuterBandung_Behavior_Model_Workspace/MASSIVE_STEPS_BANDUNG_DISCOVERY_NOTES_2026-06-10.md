# Massive-STEPS Bandung - Discovery Notes

Tanggal: 2026-06-10

## Sumber

Dataset: `CRUISEResearchGroup/Massive-STEPS-Bandung`

Dataset ini berisi pola check-in/trajectory POI Bandung, bukan review.

## File Yang Dicek

| Config | Split | Rows | Kolom Utama |
|---|---:|---:|---|
| default | train | 38.732 | user_id, trail_id, inputs, targets |
| default | validation | 5.534 | user_id, trail_id, inputs, targets |
| default | test | 11.067 | user_id, trail_id, inputs, targets |
| tabular | train | 113.058 | trail_id, user_id, venue_id, koordinat, kategori, timestamp |
| tabular | validation | 16.018 | trail_id, user_id, venue_id, koordinat, kategori, timestamp |
| tabular | test | 32.208 | trail_id, user_id, venue_id, koordinat, kategori, timestamp |

## Temuan Data

| Item | Nilai |
|---|---:|
| Total baris tabular | 161.284 |
| Users | 3.377 |
| Trails | 55.333 |
| Venues unik | 26.559 |
| Kategori unik | 421 |
| Rentang waktu | 2012-04-03 sampai 2018-10-19 |
| Missing latitude/name | 37.937 baris (23,52%) |
| Missing address | 42.654 baris (26,45%) |

## Kategori Terbanyak

| Kategori | Count |
|---|---:|
| Home (private) | 18.844 |
| Shopping Mall | 17.021 |
| High School | 5.647 |
| Road | 5.342 |
| Cafe | 4.390 |
| Indonesian Restaurant | 3.925 |
| Multiplex | 3.444 |
| College Classroom | 3.102 |
| Food Truck | 2.300 |
| Office | 2.294 |

## Catatan Penting

- Dataset ini cocok untuk training behavior model, terutama `next-category` atau `next-POI`.
- Banyak kategori bukan wisata langsung, seperti rumah, sekolah, road, office.
- Mapping langsung ke destinasi MuterBandung belum aman karena 23,52% baris tidak punya koordinat/nama.
- Langkah awal paling aman: gunakan kategori/sequence dulu, bukan POI detail.
- Model baseline yang paling cocok: Markov transition atau next-category classifier.

## Keputusan Awal

Gunakan Massive-STEPS Bandung untuk eksperimen behavior layer:

`history category -> next category`

Belum digunakan untuk mengganti recommender utama. Dipakai sebagai layer tambahan setelah mapping kategori dibuat.
