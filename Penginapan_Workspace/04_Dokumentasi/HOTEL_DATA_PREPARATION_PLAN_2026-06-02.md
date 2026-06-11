# Hotel Data Preparation Plan - MuterBandung

Tanggal: 2026-06-02  
Status: Plan kerja, belum eksekusi pipeline final  
Workspace: `Penginapan_Workspace`

## 1. Tujuan

Plan ini menyiapkan data penginapan/hotel agar siap dipakai sebagai fitur pendukung wisata di MuterBandung.

Fokus utama bukan mencari data sempurna, tetapi membuat data yang:

1. cukup aman untuk rekomendasi,
2. rapi secara struktur,
3. tervalidasi wilayah dan koordinat,
4. tidak penuh duplikasi,
5. siap dipakai untuk scraping review comment,
6. siap masuk pipeline sentiment hotel.

## 2. Status Data Saat Ini

Berdasarkan audit terakhir:

| Komponen | Status |
|---|---:|
| Total JSON Google Hotels Search | 18 |
| JSON baru tanggal 2026-06-02 | 15 |
| Total record JSON | 2946 |
| Unique gabungan CSV + JSON | 1385 |
| Net unique baru dari batch 2026-06-02 | 386 |
| Koordinat tersedia | 1384/1385 |
| Rating tersedia | 902 |
| Review count tersedia | 871 |
| Skor fase aman | 7/8 |

Keputusan: **data raw penginapan sudah cukup aman**. Tidak perlu scraping area baru untuk saat ini.

## 3. Prinsip Kerja

| Prinsip | Penjelasan |
|---|---|
| Jangan gabung mentah langsung ke sistem | Semua JSON/CSV harus lewat flatten, dedupe, dan validation. |
| Canonical adalah sumber utama | Website hanya boleh memakai dataset canonical, bukan raw JSON. |
| Review comment dibuat setelah canonical | Jangan scrape review dari data yang masih duplikat atau salah wilayah. |
| Sentiment dijalankan offline | Jangan menjalankan NLP/transformer sentiment secara realtime di server. |
| Data tidak sempurna boleh dipakai jika diberi flag | Sistem harus tahu mana data kuat dan mana data perlu caveat. |

## 4. Struktur Output Yang Diinginkan

| Output | Fungsi |
|---|---|
| `HOTEL_RAW_MASTER_2026-06-02.csv` | Semua data hotel/penginapan hasil flatten dari JSON dan CSV. |
| `HOTEL_DEDUPED_MASTER_2026-06-02.csv` | Data setelah dedupe awal. |
| `HOTEL_CANONICAL_BANDUNG_RAYA_2026-06-02.csv` | Dataset utama penginapan yang siap dipakai sistem. |
| `HOTEL_CANONICAL_VALIDATION_2026-06-02.json` | Hasil validasi schema dan quality. |
| `HOTEL_REVIEW_TARGETS_2026-06-02.csv` | Daftar target scraping Google Maps review comment. |
| `HOTEL_REVIEWS_RAW_2026-06-02.csv` | Semua review comment mentah hasil scraper. |
| `HOTEL_SENTIMENT_AGG_2026-06-02.csv` | Agregasi sentiment per penginapan. |
| `HOTEL_CANONICAL_WITH_SENTIMENT_2026-06-02.csv` | Canonical final setelah sentiment masuk. |

## 5. Tahap 1 - Inventaris Sumber Data

Tujuan: memastikan semua sumber data yang akan digabung sudah jelas.

Sumber utama:

| Sumber | Lokasi |
|---|---|
| JSON Google Hotels Search | `Penginapan_Workspace/01_Raw_Data/google_hotels_search_json/` |
| CSV hotel lama | `Penginapan_Workspace/01_Raw_Data/dataset_hotel_original/` |
| CSV generated raw | `Penginapan_Workspace/01_Raw_Data/generated_raw_csv/` |
| Canonical lama | `Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv` |
| Training lama | `Penginapan_Workspace/02_Curated/HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv` |

Catatan penting:

- File Pangalengan berikut adalah duplikat penuh:
  - `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200.json`
  - `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200 (1).json`
- Saat build, salah satu harus diabaikan atau otomatis terhapus oleh dedupe hash.

Checklist:

| Item | Status |
|---|---|
| Semua JSON terdeteksi | Belum dikerjakan |
| File duplikat hash ditandai | Belum dikerjakan |
| Semua CSV lama dicatat | Belum dikerjakan |
| Source lineage per row disiapkan | Belum dikerjakan |

## 6. Tahap 2 - Flatten JSON Ke Raw Master

Tujuan: mengubah struktur JSON Google Hotels Search menjadi CSV tabular.

Field minimal dari JSON:

| Field | Keterangan |
|---|---|
| `source_file` | Nama file JSON asal. |
| `source_query` | Query Apify yang menghasilkan data. |
| `source_page_number` | Halaman hasil. |
| `raw_type` | `hotel`, `vacation rental`, atau lainnya. |
| `name` | Nama properti. |
| `property_token` | Token unik dari Google Hotels jika tersedia. |
| `latitude` | Koordinat latitude. |
| `longitude` | Koordinat longitude. |
| `description` | Deskripsi properti. |
| `source_link` | Link properti atau provider. |
| `check_in_time` | Jam check-in. |
| `check_out_time` | Jam check-out. |
| `price_lowest` | Harga terendah numeric jika tersedia. |
| `price_display` | Harga display. |
| `hotel_class` | Kelas hotel jika tersedia. |
| `overall_rating` | Rating Google Hotels. |
| `reviews` | Jumlah review. |
| `ratings_distribution` | Distribusi bintang jika tersedia. |
| `reviews_breakdown` | Breakdown review jika tersedia. |
| `amenities` | Fasilitas. |
| `primary_image_url` | Gambar utama. |
| `all_image_urls` | Semua gambar jika tersedia. |

Output tahap ini:

`Penginapan_Workspace/01_Raw_Data/generated_raw_csv/HOTEL_RAW_MASTER_2026-06-02.csv`

## 7. Tahap 3 - Dedupe

Tujuan: menghapus duplikasi tanpa kehilangan data penting.

Urutan dedupe:

| Level | Metode | Keterangan |
|---|---|---|
| 1 | `property_token` | Jika sama, hampir pasti properti sama. |
| 2 | nama normalized + koordinat dekat | Cocok untuk data tanpa token. |
| 3 | nama normalized + source link | Cocok untuk provider yang sama. |
| 4 | fuzzy name + jarak koordinat | Dipakai hati-hati untuk villa/apartment. |

Aturan koordinat dekat:

| Jarak | Keputusan |
|---:|---|
| 0-50 meter | kemungkinan sama |
| 50-150 meter | perlu cek tipe/nama |
| >150 meter | jangan otomatis gabung kecuali token sama |

Output tahap ini:

`Penginapan_Workspace/02_Curated/HOTEL_DEDUPED_MASTER_2026-06-02.csv`

## 8. Tahap 4 - Region Validation

Tujuan: memastikan data hanya masuk rekomendasi utama jika berada di Bandung Raya atau relevan dengan itinerary Bandung.

Label yang dibuat:

| Field | Nilai |
|---|---|
| `region_validation_label` | `bandung_raya_valid`, `border_area`, `outside_bandung_raya`, `needs_review` |
| `region_bucket` | Kota Bandung, Cimahi, KBB, Kabupaten Bandung, Bandung Raya lain, luar |
| `distance_from_bandung_center_km` | Jarak dari pusat Bandung |
| `distance_from_nearest_wisata_km` | Opsional setelah integrasi wisata |

Aturan awal:

| Kondisi | Label |
|---|---|
| Koordinat jelas di Kota Bandung/Cimahi/KBB/Kab Bandung | `bandung_raya_valid` |
| Koordinat di area perbatasan dan masih relevan | `border_area` |
| Koordinat jauh di luar Bandung Raya | `outside_bandung_raya` |
| Koordinat kosong/aneh | `needs_review` |

Catatan:

- Data `outside_bandung_raya` tidak harus dihapus.
- Tapi jangan masuk rekomendasi utama kecuali user memang mencari area luar.

## 9. Tahap 5 - Property Type Classification

Tujuan: membedakan hotel formal, guest house, villa, apartment, dan room-level listing.

Field yang dibuat:

| Field | Fungsi |
|---|---|
| `property_type` | Kategori utama properti. |
| `is_room_level_listing` | True jika data adalah kamar/unit, bukan properti utama. |
| `is_apartment_listing` | True jika apartment/unit apartment. |
| `is_villa_listing` | True jika villa/rumah sewa. |
| `is_budget_chain_listing` | True jika OYO, RedDoorz, Collection O, dll. |

Kategori utama:

| Label | Contoh |
|---|---|
| `hotel` | Hotel formal, resort, convention hotel |
| `guest_house` | Guest house, homestay |
| `villa` | Villa, rumah sewa, private pool |
| `apartment` | Unit apartment, studio, 2BR |
| `vacation_rental` | Rental properti non-hotel |
| `room_level_listing` | Standard double room, one-bedroom apartment |

Catatan:

- Room-level listing boleh disimpan.
- Tapi untuk rekomendasi utama, properti utama harus diprioritaskan di atas room-level listing.

## 10. Tahap 6 - Quality Flags

Tujuan: sistem tahu mana data kuat dan mana data lemah.

Field quality:

| Field | Keterangan |
|---|---|
| `coordinate_available` | Koordinat ada/tidak. |
| `coordinate_valid` | Koordinat masuk wilayah aman. |
| `rating_available` | Rating ada/tidak. |
| `review_count_available` | Jumlah review ada/tidak. |
| `price_available` | Harga ada/tidak. |
| `amenities_available` | Fasilitas ada/tidak. |
| `image_available` | Gambar ada/tidak. |
| `description_available` | Deskripsi ada/tidak. |
| `source_link_available` | Link sumber ada/tidak. |
| `data_quality_score` | Skor 0-100. |
| `data_quality_label` | `low`, `medium`, `high`. |

Contoh skoring:

| Komponen | Bobot |
|---|---:|
| Koordinat valid | 25 |
| Rating + jumlah review | 20 |
| Harga | 15 |
| Fasilitas | 15 |
| Gambar | 10 |
| Deskripsi | 5 |
| Link sumber | 5 |
| Bukan room-level listing | 5 |

## 11. Tahap 7 - Build Canonical Hotel Dataset

Tujuan: menghasilkan dataset utama penginapan.

Kolom canonical minimal:

| Kolom | Fungsi |
|---|---|
| `hotel_id` | ID internal stabil. |
| `name` | Nama properti. |
| `property_type` | Hotel/villa/apartment/guest house. |
| `latitude` | Latitude. |
| `longitude` | Longitude. |
| `region_bucket` | Wilayah validasi. |
| `region_validation_label` | Valid/border/outside/needs review. |
| `overall_rating` | Rating. |
| `reviews` | Jumlah review. |
| `price_lowest` | Harga terendah. |
| `price_display` | Harga display. |
| `check_in_time` | Check-in. |
| `check_out_time` | Check-out. |
| `hotel_class` | Kelas hotel. |
| `amenities` | Fasilitas. |
| `primary_image_url` | Gambar utama. |
| `source_link` | Link sumber. |
| `data_quality_score` | Skor kualitas. |
| `data_quality_label` | Label kualitas. |

Output:

`Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_BANDUNG_RAYA_2026-06-02.csv`

## 12. Tahap 8 - Validation Pipeline

Tujuan: memastikan canonical tidak rusak sebelum dipakai website.

Validasi wajib:

| Validasi | Aturan |
|---|---|
| Schema | Kolom wajib harus ada. |
| Koordinat | Latitude/longitude numeric dan masuk rentang aman. |
| Rating | 0 sampai 5. |
| Review count | Numeric dan >= 0. |
| Harga | Numeric atau kosong. |
| Link gambar | URL valid atau kosong. |
| Property type | Harus masuk daftar label yang diizinkan. |
| Region validation | Harus punya label. |
| Quality score | 0 sampai 100. |
| Duplicate | Tidak boleh ada duplicate kuat. |

Gate:

| Gate | Arti |
|---|---|
| `PASS` | Siap dipakai sistem. |
| `PASS_WITH_WARNINGS` | Boleh dipakai dengan caveat. |
| `FAIL` | Jangan dipakai. |

Target awal: `PASS_WITH_WARNINGS` sudah cukup.

## 13. Tahap 9 - Review Comment Targets

Tujuan: membuat daftar penginapan yang layak discrape review comment-nya.

Jangan scrape semua data. Prioritaskan:

| Prioritas | Kriteria |
|---|---|
| P0 | Data quality high, koordinat valid, dekat wisata utama, review count tinggi. |
| P1 | Data quality medium, koordinat valid, properti populer. |
| P2 | Data quality medium/low tapi penting secara area. |

Kolom target review:

| Kolom | Fungsi |
|---|---|
| `hotel_id` | ID canonical. |
| `name` | Nama penginapan. |
| `latitude` | Latitude. |
| `longitude` | Longitude. |
| `google_maps_query` | Query untuk scraper review. |
| `source_link` | Link jika tersedia. |
| `target_review_limit` | Batas review yang ingin diambil. |
| `review_scrape_priority` | P0/P1/P2. |
| `reason` | Alasan masuk target. |

Jumlah review target:

| Kondisi | Target |
|---|---:|
| Review count tinggi | 80-150 comment |
| Review count sedang | 40-80 comment |
| Review count rendah | 20-40 comment |
| Area penting tapi data lemah | 20-30 comment |

Output:

`Penginapan_Workspace/02_Curated/HOTEL_REVIEW_TARGETS_2026-06-02.csv`

## 14. Tahap 10 - Scraping Review Comment

Tujuan: mendapatkan komentar mentah untuk sentiment.

Aturan:

1. Scrape dari target canonical, bukan raw JSON.
2. Simpan komentar mentah terpisah dari canonical.
3. Jangan menghapus review walaupun pendek, kecuali spam/error jelas.
4. Simpan metadata bahasa, rating review, tanggal, dan source.

Kolom review raw:

| Kolom | Fungsi |
|---|---|
| `hotel_id` | ID canonical. |
| `hotel_name` | Nama hotel. |
| `review_id` | ID review jika ada. |
| `review_text` | Isi komentar. |
| `review_rating` | Rating dari user. |
| `review_date` | Tanggal review. |
| `review_language` | Bahasa. |
| `reviewer_name` | Nama reviewer jika ada. |
| `source` | Google Maps. |

Output:

`Penginapan_Workspace/01_Raw_Data/reviews/HOTEL_REVIEWS_RAW_2026-06-02.csv`

## 15. Tahap 11 - Sentiment Pipeline

Tujuan: membuat skor sentiment per penginapan.

Rekomendasi:

- Untuk server realtime: jangan jalankan model sentiment berat.
- Untuk batch/offline: boleh pakai NLP model.
- Untuk awal yang aman: pakai kombinasi review rating + text sentiment ringan.

Opsi sentiment:

| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| Rating-based only | Ringan dan stabil | Tidak memahami isi komentar. |
| TF-IDF + LinearSVC | Ringan untuk batch, cukup cepat | Butuh label/training. |
| IndoBERT/transformer | Lebih kuat secara NLP | Berat, sebaiknya offline/Colab. |

Rekomendasi tahap awal:

1. Pakai rating-based sentiment sebagai baseline.
2. Tambahkan TF-IDF + LinearSVC jika review comment sudah cukup.
3. IndoBERT hanya dipakai untuk eksperimen/offline, bukan server realtime.

## 16. Tahap 12 - Sentiment Aggregation

Output per hotel:

| Kolom | Fungsi |
|---|---|
| `hotel_id` | ID canonical. |
| `review_comment_count` | Jumlah komentar yang dipakai. |
| `rating_sentiment_score` | Skor dari rating. |
| `text_sentiment_score` | Skor dari komentar. |
| `adjusted_sentiment_score` | Skor final dengan shrinkage. |
| `sentiment_label` | Positif/netral/negatif. |
| `review_confidence_label` | Low/medium/high. |

Confidence:

| Jumlah comment | Label |
|---:|---|
| 0-9 | `very_low_review_confidence` |
| 10-29 | `low_review_confidence` |
| 30-79 | `medium_review_confidence` |
| 80+ | `high_review_confidence` |

Gunakan Bayesian shrinkage agar hotel dengan review sedikit tidak terlalu percaya diri.

## 17. Tahap 13 - Integrasi Ke Website

Hotel tidak menjadi fitur utama seperti marketplace. Di MuterBandung, hotel adalah pendukung setelah user memilih wisata.

Pola integrasi:

1. User cari/rekomendasi wisata.
2. User klik destinasi.
3. Sistem tampilkan penginapan terdekat.
4. Ranking hotel berdasarkan:
   - jarak ke wisata,
   - data quality,
   - rating/sentiment,
   - harga,
   - fasilitas,
   - tipe penginapan.

Ranking awal:

| Komponen | Bobot awal |
|---|---:|
| Jarak ke wisata | 35 |
| Rating/sentiment | 25 |
| Data quality | 20 |
| Harga sesuai kebutuhan | 10 |
| Fasilitas | 10 |

## 18. Risiko Yang Harus Dijaga

| Risiko | Pencegahan |
|---|---|
| Hotel duplikat muncul berkali-kali | Dedupe token/nama/koordinat. |
| Room-level listing mengalahkan hotel utama | Tambahkan `is_room_level_listing`. |
| Data luar Bandung ikut rekomendasi | Region validation dan filter. |
| Review sedikit terlalu dipercaya | Pakai confidence label dan shrinkage. |
| Harga kosong dianggap murah | Jangan treat kosong sebagai murah. |
| Sentiment realtime berat | Sentiment offline, server hanya baca skor agregat. |
| LLM halusinasi fasilitas | LLM hanya boleh pakai field verified/available. |

## 19. Urutan Eksekusi Yang Disarankan

| Urutan | Tahap | Output |
|---:|---|---|
| 1 | Flatten semua JSON/CSV | `HOTEL_RAW_MASTER` |
| 2 | Dedupe | `HOTEL_DEDUPED_MASTER` |
| 3 | Region validation | field region valid |
| 4 | Property type classification | field tipe properti |
| 5 | Quality scoring | field quality |
| 6 | Build canonical | `HOTEL_CANONICAL_BANDUNG_RAYA` |
| 7 | Validate canonical | validation JSON/report |
| 8 | Buat review targets | `HOTEL_REVIEW_TARGETS` |
| 9 | Scrape review comment | `HOTEL_REVIEWS_RAW` |
| 10 | Sentiment offline | `HOTEL_SENTIMENT_AGG` |
| 11 | Merge sentiment ke canonical | `HOTEL_CANONICAL_WITH_SENTIMENT` |
| 12 | Integrasi ke website | hotel pendukung wisata |

## 20. Keputusan Untuk Saat Ini

Untuk saat ini:

1. Stop scraping area baru.
2. Jangan langsung sentiment.
3. Jangan langsung masukkan raw JSON ke website.
4. Lanjut ke engineering pipeline penggabungan data.
5. Setelah canonical bersih, baru scrape review comment.

Kesimpulan: **langkah berikutnya adalah penggabungan terstruktur seluruh data penginapan, bukan pencarian data baru.**
