# UI and Recommender QA Report 2026-06-09

## Status

| Area | Hasil |
|---|---|
| Runtime API gate | `PASS_WITH_WARNINGS` |
| Query diuji | 12 |
| Pass | 11 |
| Warning | 1 |
| Failed | 0 |
| Data version | `DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv:1780976783` |

## UI Reachability

| Target | Status | Catatan |
|---|---:|---|
| `/` | 200 | brand ok |
| `/static/style.css` | 200 | - |
| `/static/script.js` | 200 | api link ok |
| `/api/recommend` | 200 | recommendations=5, fallback=false, first=Alam Wisata Cimahi |

Catatan: browser visual internal tidak tersedia di sesi ini, jadi UI dicek lewat Flask test client dan static asset reachability. API yang dipakai frontend berhasil dipanggil.

## Top 5 Query Audit

### Q001_ALAM_MURAH - wisata alam murah

Verdict: **Bagus**

Hasil sesuai: alam, murah, dan destinasi populer/ber-rating kuat.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-113` | Wayang Windu Panenjoan | 82.03 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-189` | Curug Aseupan | 81.24 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-079` | Situ Cileunca Pangalengan Bandung | 80.8 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-012` | Bukit Moko Bandung | 80.79 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 5 | `LOC-154` | Kampung Singkur | 80.36 | Rp 10.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | - |

### Q002_KELUARGA_RAMAH_ANAK - wisata keluarga ramah anak

Verdict: **Bagus**

Top 5 semuanya masuk konteks keluarga/anak dan fasilitas penting muncul.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-106` | The Nice Park Bandung | 88.68 | Rp 30.000 - Rp 60.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 2 | `LOC-002` | Alam Wisata Cimahi | 87.45 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 3 | `LOC-111` | Venus Cimahi | 87.15 | Rp 15.000 - Rp 25.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-105` | The Lodge Maribaya | 85.18 | Rp 50.000 - Rp 65.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 5 | `LOC-102` | Terminal Wisata Grafika Cikole | 84.38 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |

### Q003_MALAM_BANDUNG - wisata malam Bandung

Verdict: **Bagus**

Hasil malam cukup masuk akal; Bukit Moko, Sudut Pandang, Lawangwangi, Bukit Bintang relevan.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-012` | Bukit Moko Bandung | 77.55 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 2 | `LOC-172` | Sudut Pandang Bandung | 75.74 | Rp 75.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam |
| 3 | `LOC-126` | Lawangwangi Creative Space | 74.1 | Rp 25.000 - Rp 200.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 4 | `LOC-102` | Terminal Wisata Grafika Cikole | 72.56 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |
| 5 | `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) | 71.27 | Rp 15.000 - Rp 25.000 (Per Orang) | google_maps_stars_fallback / medium_review_confidence | mushola, parkir, malam |

### Q004_EDUKASI_ANAK - wisata edukasi anak

Verdict: **Bagus**

Hasil edukasi anak cukup tepat; Lembang Park & Zoo dan Taman Kupu-Kupu kuat.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-053` | Lembang Park & Zoo | 84.39 | Rp 65.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | anak |
| 2 | `LOC-175` | Taman Kupu-Kupu Cihanjuang | 77.89 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 3 | `LOC-005` | Amazing Artgames | 77.49 | Rp 35.000 - Rp 50.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-180` | Cimory Dairyland Lembang | 67.52 | Rp 15.000 - Rp 45.000 (Per Orang) | tfidf_linearsvc / low_review_confidence | anak |
| 5 | `LOC-178` | De'Ranch Lembang | 63.15 | Rp 26.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |

### Q005_MUSHOLA_PARKIR - wisata ada mushola dan parkir

Verdict: **Bagus**

Setelah logic fasilitas dirapikan, hasil punya mushola dan parkir, fallback false.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-002` | Alam Wisata Cimahi | 70.41 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 2 | `LOC-102` | Terminal Wisata Grafika Cikole | 67.76 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam, anak |
| 3 | `LOC-105` | The Lodge Maribaya | 67.02 | Rp 50.000 - Rp 65.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 4 | `LOC-106` | The Nice Park Bandung | 66.56 | Rp 30.000 - Rp 60.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | mushola, parkir, anak |
| 5 | `LOC-116` | Wisata Kampoeng Ciherang | 65.98 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | mushola, parkir, anak |

### Q006_GRATIS_DEKAT_ALUN_ALUN - wisata gratis dekat alun-alun bandung

Verdict: **Perlu keputusan produk**

Secara teknis benar karena gratis dan dekat, tetapi mall/shopping center ikut naik. Perlu putuskan apakah itu boleh.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-010` | Braga Citywalk | 85.93 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam |
| 2 | `LOC-061` | Museum Konferensi Asia Afrika | 85.68 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-104` | The Kings Shopping Centre | 84.73 | Gratis | tfidf_linearsvc / high_review_confidence | mushola, parkir, malam |
| 4 | `LOC-033` | Gedung Merdeka | 84.38 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 5 | `LOC-003` | Alun-Alun Kota Bandung | 83.62 | Gratis | tfidf_linearsvc / high_review_confidence | mushola |

### Q007_MUSEUM_INDOOR - museum indoor Bandung

Verdict: **Cukup baik**

Museum muncul dominan, tetapi Lawangwangi/Gedung Merdeka ikut karena konteks indoor/heritage. Masih bisa diterima.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-219` | Museum Inggit Garnasih | 87.2 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-061` | Museum Konferensi Asia Afrika | 85.66 | Gratis | tfidf_linearsvc / high_review_confidence | - |
| 3 | `LOC-060` | Museum Geologi Bandung | 84.81 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-126` | Lawangwangi Creative Space | 83.4 | Rp 25.000 - Rp 200.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 5 | `LOC-033` | Gedung Merdeka | 83.08 | Gratis | tfidf_linearsvc / high_review_confidence | - |

### Q008_SATWA_ANAK - wisata satwa untuk anak

Verdict: **Bagus**

Hasil satwa/anak relevan: zoo, kupu-kupu, dairyland, ranch, Rumah Guguk.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-053` | Lembang Park & Zoo | 84.25 | Rp 65.000 - Rp 85.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | anak |
| 2 | `LOC-175` | Taman Kupu-Kupu Cihanjuang | 73.2 | Rp 20.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 3 | `LOC-180` | Cimory Dairyland Lembang | 69.72 | Rp 15.000 - Rp 45.000 (Per Orang) | tfidf_linearsvc / low_review_confidence | anak |
| 4 | `LOC-178` | De'Ranch Lembang | 68.8 | Rp 26.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |
| 5 | `LOC-120` | Rumah Guguk | 66.71 | Rp 70.000 - Rp 90.000 (Per Orang) | tfidf_linearsvc / medium_review_confidence | anak |

### Q009_SPOT_FOTO_HEALING - spot foto healing pemandangan

Verdict: **Bagus**

Hasil pemandangan/healing kuat dan murah.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-113` | Wayang Windu Panenjoan | 87.33 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-012` | Bukit Moko Bandung | 86.33 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 3 | `LOC-189` | Curug Aseupan | 85.63 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 4 | `LOC-079` | Situ Cileunca Pangalengan Bandung | 85.42 | Rp 5.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 5 | `LOC-153` | Perkebunan Teh Malabar | 85.06 | Rp 5.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |

### Q010_CURUG_MURAH - curug murah Bandung

Verdict: **Perlu tuning**

Query menyebut curug, tetapi beberapa top result bukan curug. Perlu hard/boost lexical untuk kata curug.

| Rank | ID | Nama | Score | Harga | Sentiment | Flags |
|---:|---|---|---:|---|---|---|
| 1 | `LOC-153` | Perkebunan Teh Malabar | 71.23 | Rp 5.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 2 | `LOC-012` | Bukit Moko Bandung | 71.11 | Rp 15.000 - Rp 30.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | malam |
| 3 | `LOC-225` | Curug Ceret Pangalengan | 70.1 | Gratis | tfidf_linearsvc / medium_review_confidence | - |
| 4 | `LOC-189` | Curug Aseupan | 69.55 | Rp 10.000 - Rp 15.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |
| 5 | `LOC-113` | Wayang Windu Panenjoan | 68.76 | Rp 20.000 (Per Orang) | tfidf_linearsvc / high_review_confidence | - |

### Q011_BELANJA_OLEH_OLEH - tempat belanja oleh-oleh Bandung

Verdict: **Scope belum didukung**

Tidak ada hasil karena data oleh-oleh belum masuk entity terpisah. Ini aman, bukan crash.

Issues:
- recommendations below minimum: 0 < 1

Tidak ada rekomendasi yang dikembalikan.

### Q012_UNSUPPORTED_PANTAI - pantai di Bandung

Verdict: **Bagus**

Sistem menolak pantai di Bandung dan tidak memaksakan hasil.

Tidak ada rekomendasi yang dikembalikan.

## Saran Tuning

| Prioritas | Saran | Alasan |
|---|---|---|
| P1 | Tambah lexical hard/boost untuk kata `curug` | Query `curug murah Bandung` masih menaikkan tempat non-curug. |
| P2 | Putuskan mall boleh/tidak untuk query `wisata gratis dekat alun-alun` | Secara jarak dan harga benar, tapi rasa produk bisa berbeda. |
| P3 | Biarkan `oleh-oleh` unsupported sampai entity oleh-oleh siap | Lebih aman daripada memaksa hasil belanja umum. |
| P4 | Setelah tuning, jalankan eval set yang sama | Supaya perubahan bobot tidak merusak query yang sudah bagus. |

## Keputusan Sementara

Recommender sudah layak untuk QA user-facing awal. Jangan masuk LLM dulu sebelum P1 diputuskan, karena LLM hanya akan menjelaskan ranking yang sudah ada.

## Update Setelah Tuning Curug dan Mall

Tanggal update: `2026-06-09`

Keputusan yang diterapkan:

- Query `curug`, `air terjun`, atau `waterfall` diperlakukan sebagai intent spesifik. Jika kandidat curug tersedia, top result diprioritaskan ke destinasi curug.
- Mall tidak dihapus dari dataset, tetapi diberi ranking penalty jika user tidak meminta mall/belanja.
- Jika user memang meminta `mall` atau `belanja`, mall tetap bisa naik ranking.

Hasil cek ulang:

| Query | Hasil Setelah Tuning | Status |
|---|---|---|
| `curug murah Bandung` | Top 5 sekarang semua curug: Curug Ceret, Curug Aseupan, Curug Anom, Curug Bugbrug, Curug Dago | Membaik |
| `wisata gratis dekat alun-alun bandung` | Top 5 sekarang Museum KAA, Gedung Merdeka, Alun-Alun, Taman Dewi Sartika, Museum Inggit Garnasih | Membaik |
| `mall dekat alun-alun bandung` | Mall tetap naik: The Kings, Braga Citywalk, BIP, Ciwalk, 23 Paskal | Sesuai |

API audit setelah tuning tetap `PASS_WITH_WARNINGS`: 11 pass, 1 warning, 0 fail. Warning yang tersisa masih query oleh-oleh karena entity oleh-oleh belum masuk runtime.

