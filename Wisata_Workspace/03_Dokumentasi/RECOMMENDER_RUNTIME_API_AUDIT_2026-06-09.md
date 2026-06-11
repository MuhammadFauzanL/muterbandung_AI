# Recommender Runtime API Audit 2026-06-09

Generated at: `2026-06-10T07:24:16.538804Z`
Dataset: `D:\File\file\Fauzan Lubada\PIJAK\Wisata_Workspace\01_Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv`
Data version: `DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv:1780976783`
Gate: `PASS_WITH_WARNINGS`

## Summary

| Metric | Value |
|---|---:|
| Total queries | 12 |
| Passed | 11 |
| Warnings | 1 |
| Failed | 0 |

## Query Results

### Q001_ALAM_MURAH

Query: `wisata alam murah`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-113` | Wayang Windu Panenjoan | 82.03 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-189` | Curug Aseupan | 81.24 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-079` | Situ Cileunca Pangalengan Bandung | 80.8 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-012` | Bukit Moko Bandung | 80.79 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 5 | `LOC-154` | Kampung Singkur | 80.36 | Rp 10.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | - |

### Q002_KELUARGA_RAMAH_ANAK

Query: `wisata keluarga ramah anak`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-106` | The Nice Park Bandung | 88.68 | Rp 30.000 - Rp 60.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 2 | `LOC-002` | Alam Wisata Cimahi | 87.45 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 3 | `LOC-111` | Venus Cimahi | 87.15 | Rp 15.000 - Rp 25.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-105` | The Lodge Maribaya | 85.18 | Rp 50.000 - Rp 65.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 5 | `LOC-102` | Terminal Wisata Grafika Cikole | 84.38 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |

### Q003_MALAM_BANDUNG

Query: `wisata malam Bandung`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-012` | Bukit Moko Bandung | 77.55 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 2 | `LOC-172` | Sudut Pandang Bandung | 75.74 | Rp 75.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam |
| 3 | `LOC-126` | Lawangwangi Creative Space | 74.1 | Rp 25.000 - Rp 200.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 4 | `LOC-102` | Terminal Wisata Grafika Cikole | 72.56 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |
| 5 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) | 71.27 | Rp 15.000 - Rp 25.000 (Per Orang) | google_maps_stars_fallback / medium_review_confidence | mushola, parkir, malam |

### Q004_EDUKASI_ANAK

Query: `wisata edukasi anak`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-053` | Lembang Park & Zoo | 84.39 | Rp 65.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | anak |
| 2 | `LOC-175` | Taman Kupu-Kupu Cihanjuang | 77.89 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 3 | `LOC-005` | Amazing Artgames | 77.49 | Rp 35.000 - Rp 50.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-180` | Cimory Dairyland Lembang | 67.52 | Rp 15.000 - Rp 45.000 (Per Orang) | tfidf_linearsvc / low_review_confidence | anak |
| 5 | `LOC-178` | De'Ranch Lembang | 63.15 | Rp 26.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |

### Q005_MUSHOLA_PARKIR

Query: `wisata ada mushola dan parkir`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-002` | Alam Wisata Cimahi | 70.41 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 2 | `LOC-102` | Terminal Wisata Grafika Cikole | 67.76 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |
| 3 | `LOC-105` | The Lodge Maribaya | 67.02 | Rp 50.000 - Rp 65.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-106` | The Nice Park Bandung | 66.56 | Rp 30.000 - Rp 60.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 5 | `LOC-116` | Wisata Kampoeng Ciherang | 65.98 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | mushola, parkir, anak |

### Q006_GRATIS_DEKAT_ALUN_ALUN

Query: `wisata gratis dekat alun-alun bandung`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-061` | Museum Konferensi Asia Afrika | 85.68 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-033` | Gedung Merdeka | 84.38 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-003` | Alun-Alun Kota Bandung | 83.62 | Gratis | tfidf_linearsvc / high_review_confidence | mushola |
| 4 | `LOC-119` | Taman Dewi Sartika | 83.46 | Gratis | tfidf_linearsvc / high_review_confidence | anak |
| 5 | `LOC-219` | Museum Inggit Garnasih | 82.64 | Gratis | tfidf_linearsvc / high_review_confidence | - |

### Q007_MUSEUM_INDOOR

Query: `museum indoor Bandung`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-219` | Museum Inggit Garnasih | 87.2 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-061` | Museum Konferensi Asia Afrika | 85.66 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-060` | Museum Geologi Bandung | 84.81 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-126` | Lawangwangi Creative Space | 83.4 | Rp 25.000 - Rp 200.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 5 | `LOC-033` | Gedung Merdeka | 83.08 | Gratis | tfidf_linearsvc / high_review_confidence | - |

### Q008_SATWA_ANAK

Query: `wisata satwa untuk anak`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-053` | Lembang Park & Zoo | 84.25 | Rp 65.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | anak |
| 2 | `LOC-175` | Taman Kupu-Kupu Cihanjuang | 73.2 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 3 | `LOC-180` | Cimory Dairyland Lembang | 69.72 | Rp 15.000 - Rp 45.000 (Per Orang) | tfidf_linearsvc / low_review_confidence | anak |
| 4 | `LOC-178` | De'Ranch Lembang | 68.8 | Rp 26.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 5 | `LOC-120` | Rumah Guguk | 66.71 | Rp 70.000 - Rp 90.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |

### Q009_SPOT_FOTO_HEALING

Query: `spot foto healing pemandangan`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-113` | Wayang Windu Panenjoan | 87.33 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-012` | Bukit Moko Bandung | 86.33 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 3 | `LOC-189` | Curug Aseupan | 85.63 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-079` | Situ Cileunca Pangalengan Bandung | 85.42 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 5 | `LOC-153` | Perkebunan Teh Malabar | 85.06 | Rp 5.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |

### Q010_CURUG_MURAH

Query: `curug murah Bandung`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-225` | Curug Ceret Pangalengan | 70.1 | Gratis | tfidf_linearsvc / medium_review_confidence | - |
| 2 | `LOC-189` | Curug Aseupan | 69.55 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-190` | Curug Anom | 68.35 | Rp 30.000 - Rp 35.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-188` | Curug Bugbrug | 65.76 | Rp 10.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 5 | `LOC-129` | Curug Dago | 63.3 | Rp 15.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | - |

### Q011_BELANJA_OLEH_OLEH

Query: `tempat belanja oleh-oleh Bandung`

Status: `WARNING`

Issues:
- recommendations below minimum: 0 < 1

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|

### Q012_UNSUPPORTED_PANTAI

Query: `pantai di Bandung`

Status: `PASS`

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|

## Decision

Runtime API sudah memakai dataset candidate terbaru. Query dasar berjalan, tetapi item WARNING perlu dibaca sebagai bahan tuning, bukan blocker langsung.
