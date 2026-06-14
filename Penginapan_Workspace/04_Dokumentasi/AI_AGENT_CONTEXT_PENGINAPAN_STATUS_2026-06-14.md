# AI Agent Context - Penginapan MuterBandung

Tanggal konteks: 2026-06-14  
Workspace: `D:\File\file\Fauzan Lubada\PIJAK`

Dokumen ini dibuat agar AI agent lain memahami posisi terakhir pekerjaan penginapan/hotel MuterBandung. Jangan mulai dari asumsi baru sebelum membaca file ini.

## Tujuan Penginapan

Penginapan dipakai sebagai fitur pendukung setelah user memilih wisata. Fokus utama rekomendasi penginapan adalah:

1. lokasi dekat dengan destinasi wisata atau lokasi user,
2. tipe penginapan sesuai kebutuhan user,
3. rating dan review cukup,
4. sentiment review jika tersedia,
5. fasilitas penting seperti Wi-Fi, parkir, AC, kolam, dapur,
6. harga jika tersedia.

Harga tidak lagi dipaksa lengkap karena scraping harga hotel tidak stabil. Koordinat wajib karena ranking penginapan sangat bergantung pada jarak.

## Konteks Sistem MuterBandung

MuterBandung bukan marketplace hotel penuh. Sistem ini adalah smart tourism recommender yang urutannya seperti ini:

1. user mencari atau memilih wisata,
2. sistem memberi rekomendasi wisata,
3. setelah wisata dipilih, penginapan muncul sebagai pendukung,
4. penginapan diranking terutama dari jarak ke wisata, kualitas data, rating/review, sentiment, dan fasilitas.

Jadi penginapan tidak berdiri sendiri seperti Agoda/Traveloka. Penginapan harus membantu perjalanan wisata user.

Entitas utama sistem:

| Entitas | Peran |
|---|---|
| Wisata | Entitas utama sistem dan AI Planner |
| Penginapan | Pendukung setelah destinasi wisata dipilih |
| Oleh-oleh | Pendukung perjalanan dan belanja buah tangan |
| Persona | Untuk rekomendasi beranda, bukan untuk AI Planner utama |
| Behaviour model | Untuk sinyal pola kunjungan/next category, bukan pengganti scoring utama |

Penting: persona tidak boleh mengubah hasil pencarian utama secara agresif. Persona lebih cocok untuk homepage seperti "rekomendasi untuk kamu".

## Keputusan Produk Dan Data

| Area | Keputusan |
|---|---|
| Koordinat | Wajib. Data tanpa latitude/longitude jangan masuk rekomendasi utama. |
| Harga | Tidak wajib. Jika kosong, tampilkan sebagai tidak tersedia atau sembunyikan. |
| Sentiment | Penting, tetapi tidak boleh dipaksa jika review tidak aman. |
| Review scraping | Hanya gunakan review yang sudah lolos audit match. Jangan pakai raw JSON langsung. |
| Query scraping biasa | Rawan salah tempat, salah negara, atau cabang berbeda. |
| Exact Google Maps URL | Jauh lebih aman untuk scrape review. |
| Villa/apartment/vacation rental | Boleh ada, tetapi jangan selalu disetarakan dengan hotel reguler. |
| Apartment | Secondary option, bukan pilihan utama. |
| LLM | Jangan menentukan skor utama. LLM hanya menjelaskan rekomendasi dari evidence/data. |

## Prinsip AI Engineering Yang Dipakai

Sistem ini sengaja tidak langsung dibuat end-to-end black-box ML. Alasannya:

1. data masih hasil scraping dan manual completion,
2. kualitas sumber berbeda-beda,
3. rekomendasi harus bisa dijelaskan,
4. LLM rawan halusinasi jika diberi wewenang membuat skor,
5. user perlu tahu kenapa tempat direkomendasikan.

Karena itu pendekatan saat ini adalah hybrid:

| Layer | Fungsi |
|---|---|
| Data cleaning | Menentukan data mana aman dipakai |
| Rule/scoring | Ranking yang transparan |
| Sentiment model | Menilai komentar pengunjung |
| Confidence label | Menandai kuat/lemahnya data |
| LLM | Menjelaskan alasan berdasarkan evidence |

LLM tidak boleh mengarang harga, jarak, fasilitas, rating, atau sentiment.

## Dataset Utama Saat Ini

Dataset primary penginapan terbaru yang dipakai untuk audit terakhir:

`Penginapan_Workspace\02_Curated\PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_PLACES_RATING_COMPLETED_2026-06-13.csv`

Status dari dataset ini:

| Metrik | Nilai |
|---|---:|
| Total primary penginapan | 900 |
| Koordinat kosong | 0 |
| Region valid Bandung Raya | 900 |
| Harga kosong | 310 |
| Rating/review kosong | 228 |
| Sentiment kosong sebelum apply review baru | 301 |
| P2 sentiment missing awal | 114 |

Catatan penting:

- Semua 900 data primary sudah punya lat/lng.
- Harga kosong tidak menjadi blocker.
- Sentiment masih perlu diaplikasikan dari review aman yang sudah dikumpulkan.

## Lineage Singkat Data Penginapan

Alur penginapan sampai titik sekarang:

1. data hotel/penginapan dikumpulkan dari CSV lama dan Google Hotels JSON,
2. data diubah menjadi candidate canonical penginapan Bandung Raya,
3. dilakukan dedupe konservatif,
4. detail room/unit/listing dipisahkan dari primary property,
5. apartment/vacation rental diturunkan sebagai secondary option,
6. primary dataset difokuskan menjadi 900 data,
7. rating/review sebagian dilengkapi dari Google Places/Google Maps,
8. harga dicoba dilengkapi dari Google Hotels tetapi tidak dipaksakan,
9. sentiment P2 dicari melalui Google Maps Reviews,
10. query biasa banyak noise, lalu diganti ke exact Google Maps URL manual,
11. exact URL menghasilkan review yang jauh lebih aman,
12. sekarang review aman siap masuk model sentiment.

Jangan rebuild dari raw JSON lama tanpa alasan kuat, karena banyak keputusan manual dan data policy sudah diterapkan di file curated.

## Status Review Sentiment P2

Target awal P2 sentiment missing: 114 penginapan.

Review aman yang sudah terkumpul dari beberapa batch:

| Sumber accepted review | Review aman |
|---|---:|
| `PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-07-37_ACCEPTED_REVIEWS_V2.csv` | 540 |
| `PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-23_18-30_ACCEPTED_REVIEWS_V2.csv` | 339 |
| `PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-43_remaining83_ACCEPTED_REVIEWS_V2.csv` | 6 |
| `PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_19-31_exact79_ACCEPTED_REVIEWS.csv` | 967 |
| Total | 1852 |

Ringkasan review aman:

| Metrik | Nilai |
|---|---:|
| Accepted review rows siap model | 1852 |
| Review teks siap diprediksi | 1186 |
| Target penginapan dengan review aman | 67 |

File exact URL terakhir jauh lebih bersih:

`Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_19-31_exact79_ACCEPTED_REVIEWS.csv`

Audit file exact URL:

| Metrik | Nilai |
|---|---:|
| Target exact URL | 79 |
| Review rows keluar | 967 |
| Review dengan teks | 597 |
| Review dengan bintang | 967 |
| Review aman dipakai | 967 |
| Review ditahan | 0 |
| Target berhasil keluar | 34 |
| Target belum keluar | 45 |

Sisa target exact URL yang belum keluar:

`Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_EXACT_URL_NOT_RETURNED_45_2026-06-14.csv`

Komposisi sisa 45:

| Tipe | Jumlah |
|---|---:|
| hotel | 3 |
| guest_house | 2 |
| villa | 19 |
| vacation_rental | 21 |

Keputusan: jangan kejar semua sisa 45. Kalau perlu, kejar hanya 5 hotel/guest_house dulu. Villa dan vacation rental bisa memakai `sentiment_unavailable`.

## Mengapa Query Biasa Banyak Ditahan

Google Maps Reviews Scraper dengan query nama + koordinat tidak selalu mengembalikan tempat yang benar. Beberapa kasus yang ditemukan:

| Kasus | Risiko |
|---|---|
| `Grand Pacific Hotel` | Bisa masuk hotel luar negeri |
| `Hotel Victory` | Banyak nama sama di luar Indonesia |
| `Nice Guest House` | Nama terlalu umum |
| `Shakilla House` | Bisa masuk cabang/nomor rumah berbeda |
| Villa/house/unit | Bisa tertukar antara properti utama dan listing/unit |

Karena itu review dari raw JSON tidak boleh langsung dipakai. Harus ada audit `accepted` dan `held`.

Exact Google Maps URL jauh lebih aman karena menunjuk langsung ke entity Google Maps yang dipilih manual.

## Model Sentiment

Model lokal tersedia di:

`Penginapan_Workspace\07_Models\model_sentimen_muterbandung.pkl`

Ada juga copy di root:

`model_sentimen_muterbandung (1).pkl`

Model yang dicek:

| Properti | Nilai |
|---|---|
| Tipe | `sklearn.pipeline.Pipeline` |
| `predict_proba` | Ada |
| Classes | `Negatif`, `Netral`, `Positif` |

Catatan teknis:

- Saat load model muncul warning versi scikit-learn: model dibuat dengan scikit-learn 1.6.1, environment sekarang 1.8.0.
- Warning ini belum menghentikan proses load model.
- Tetap catat warning ini dalam summary hasil sentiment.

## Makna Sentiment Penginapan

Sentiment penginapan dihitung dari komentar Google Maps, bukan dari rating bintang saja.

Contoh interpretasi:

| Data | Makna |
|---|---|
| Review teks | Bahan utama model NLP |
| Stars | Sinyal tambahan, tapi bukan sentiment NLP |
| `hotel_sentiment_score` | Rata-rata skor sentiment dari review teks |
| `hotel_adjusted_sentiment_score` | Skor sentiment yang sudah dikalibrasi dengan Bayesian shrinkage |
| `hotel_review_count_analyzed` | Jumlah review teks yang dianalisis |
| `hotel_review_confidence_label` | Seberapa percaya sistem pada sentiment tersebut |

Kalau review teks sedikit, score tidak boleh terlalu percaya diri. Karena itu dipakai adjusted score dan confidence label.

## Tahap Yang Sudah Selesai

1. Primary penginapan dipilih dan dibersihkan sampai 900 data.
2. Koordinat semua primary lengkap.
3. Duplikasi besar sudah ditangani.
4. Apartment diturunkan sebagai secondary option.
5. Harga tidak lagi dipaksa lengkap.
6. Review scraping query biasa diaudit dan hanya accepted yang dipakai.
7. Exact Google Maps URL manual diisi untuk 79 data.
8. Scrape exact URL menghasilkan 967 review aman.
9. File accepted/held/audit sudah dipisah.

## Tahap Yang Belum Selesai

Belum dilakukan:

`accepted reviews -> model_sentimen_muterbandung.pkl -> inference per review -> agregasi per penginapan -> merge ke primary dataset`

Output yang sebaiknya dibuat berikutnya:

| Output | Fungsi |
|---|---|
| `PENGINAPAN_REVIEW_SENTIMENT_INFERENCE_2026-06-14_EXACT_ACCEPTED.csv` | Prediksi sentiment per review |
| `PENGINAPAN_SENTIMENT_AGGREGATED_2026-06-14_EXACT_ACCEPTED.csv` | Agregasi sentiment per penginapan |
| `PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_SENTIMENT_UPDATED_2026-06-14.csv` | Dataset primary baru dengan sentiment terupdate |
| `penginapan_sentiment_exact_apply_summary_2026-06-14.json` | Ringkasan hasil apply |

Jangan overwrite dataset utama lama.

## Expected Behaviour Setelah Apply Sentiment

Setelah apply sentiment selesai, dataset baru seharusnya:

1. jumlah baris tetap 900,
2. koordinat tetap lengkap,
3. `hotel_adjusted_sentiment_score` bertambah coverage,
4. `hotel_review_count_analyzed` bertambah untuk penginapan yang punya accepted review,
5. `completion_priority_data_focus` berubah untuk sebagian P2 sentiment missing,
6. review yang tidak punya teks tidak masuk model NLP,
7. data tanpa sentiment tetap boleh ada dengan fallback confidence.

Jika jumlah baris berubah dari 900, berarti ada risiko merge salah.

## Cara Apply Sentiment Berikutnya

Input accepted review:

1. `Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-07-37_ACCEPTED_REVIEWS_V2.csv`
2. `Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-23_18-30_ACCEPTED_REVIEWS_V2.csv`
3. `Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_18-43_remaining83_ACCEPTED_REVIEWS_V2.csv`
4. `Penginapan_Workspace\02_Curated\PENGINAPAN_P2_SENTIMENT_SCRAPE_2026-06-13_19-31_exact79_ACCEPTED_REVIEWS.csv`

Kolom penting:

| Kolom | Fungsi |
|---|---|
| `target_penginapan_id` | ID penginapan target |
| `target_name` | Nama penginapan target |
| `target_type` | Tipe penginapan |
| `reviewId` | ID review |
| `text` | Teks review |
| `textTranslated` | Teks terjemahan jika ada |
| `stars` | Rating bintang review |
| `title` | Nama place hasil Maps |
| `audit_status` | Status audit match |

Gunakan review dengan teks:

`cleaned_text_for_sentiment = text if text tidak kosong else textTranslated`

Drop duplicate aman:

`target_penginapan_id + reviewId + cleaned_text_for_sentiment`

Prediksi:

`model.predict(texts)`  
`model.predict_proba(texts)`

Skor sentiment per review:

`proba_positif - proba_negatif`

Agregasi per penginapan:

- `hotel_review_count_analyzed`
- `hotel_sentiment_score`
- `hotel_sentiment_confidence_mean`
- `positive_review_count`
- `neutral_review_count`
- `negative_review_count`
- `hotel_adjusted_sentiment_score`
- `hotel_sentiment_label`
- `hotel_adjusted_sentiment_label`
- `hotel_review_confidence`
- `hotel_review_confidence_label`
- `hotel_sentiment_model_source`
- `hotel_sentiment_model_version`

Gunakan Bayesian shrinkage seperti script lama:

`SENTIMENT_SHRINKAGE_K = 50.0`

## Rekomendasi Nama Script Baru

Saran script baru:

`Penginapan_Workspace\06_Scripts\apply_penginapan_exact_review_sentiment_2026_06_14.py`

Script ini sebaiknya hanya:

1. load dataset primary terbaru,
2. load semua accepted review CSV,
3. bersihkan teks review,
4. drop duplicate,
5. load model sentiment,
6. prediksi sentiment,
7. agregasi per `target_penginapan_id`,
8. merge ke primary,
9. export dataset baru dan summary.

Jangan campur lagi dengan scraping harga.

## Script Referensi

Script lama yang bisa dijadikan pola:

`Penginapan_Workspace\06_Scripts\apply_penginapan_completion_from_review_json_2026_06_13.py`

Namun script lama masih mengarah ke input dan pola JSON lama. Untuk tahap sekarang lebih aman membuat script baru khusus accepted review exact URL.

## Kolom Yang Harus Dijaga

Saat merge sentiment ke primary, jangan hilangkan kolom ini:

| Kolom | Kenapa penting |
|---|---|
| `penginapan_id` | Primary key |
| `name` | Nama penginapan |
| `property_type_final_after_p3` | Tipe final setelah policy |
| `latitude`, `longitude` | Ranking jarak |
| `price_lowest`, `price_display` | Harga jika ada |
| `overall_rating`, `reviews` | Rating/review count |
| `hotel_review_count_analyzed` | Coverage sentiment |
| `hotel_adjusted_sentiment_score` | Skor sentiment untuk ranking |
| `hotel_sentiment_label` | Label sentiment |
| `amenities` | Fasilitas |
| `primary_image_url` | UI card |
| `data_quality_score` | Confidence data |
| `completion_priority_data_focus` | Queue completion |

Merge harus berbasis `penginapan_id`, bukan nama.

## Policy Ranking Penginapan Nanti

Belum final, tetapi arah scoring penginapan:

| Komponen | Catatan |
|---|---|
| Jarak | Harus besar bobotnya |
| Rating | Dipakai jika tersedia |
| Review count | Dipakai sebagai confidence |
| Sentiment | Dipakai jika tersedia, jangan paksa jika kosong |
| Fasilitas | Dipakai untuk filter dan bonus |
| Harga | Dipakai jika tersedia, tapi tidak wajib |
| Property type | Hotel/guest house untuk user umum; villa naik jika rombongan |
| Apartment | Secondary option |

Kalau user memilih 2 orang, hotel/guest house/apartment kecil lebih relevan. Kalau user 7+ orang, villa/vacation rental bisa naik.

## Fallback Kalau Sentiment Kosong

Jika penginapan belum punya sentiment:

1. jangan error,
2. jangan dianggap buruk otomatis,
3. gunakan rating dan review count sebagai fallback,
4. beri confidence lebih rendah,
5. LLM harus menyebut dengan hati-hati: "sentiment review belum tersedia", bukan mengarang kesan tamu.

Contoh field yang bisa dibuat nanti:

| Field | Nilai |
|---|---|
| `hotel_sentiment_available` | true/false |
| `hotel_sentiment_source` | `tfidf_svm_penginapan` atau `unavailable` |
| `hotel_sentiment_fallback_reason` | `no_accepted_text_review` |

## RTK

RTK sudah tersedia di komputer user, tetapi perlu path penuh di session Codex:

`C:\Users\M Fauzan Lubada\.local\bin\rtk.exe`

Cek versi:

```powershell
& "C:\Users\M Fauzan Lubada\.local\bin\rtk.exe" --version
```

Hasil terakhir:

`rtk 0.42.4`

RTK berguna untuk command noisy seperti `git status`, logs, test output. Untuk pipeline Python data, tetap boleh menjalankan Python biasa dengan output ringkas.

## Checklist Validasi Setelah Apply

Agent berikutnya harus cek ini setelah membuat dataset sentiment-updated:

| Cek | Harapan |
|---|---|
| Row count | Tetap 900 |
| `penginapan_id` unik | Ya |
| Koordinat kosong | 0 |
| Sentiment coverage | Naik dari kondisi sebelumnya |
| Review count analyzed | Bertambah untuk target accepted |
| Harga kosong | Boleh tetap ada |
| Completion priority P2 | Harus turun |
| File lama | Tidak dioverwrite |

Kalau ada accepted review yang tidak punya teks, jangan dipaksa masuk model. Review tersebut tetap bisa dihitung sebagai audit scrape, tetapi bukan inference NLP.

## Known Risks

| Risiko | Mitigasi |
|---|---|
| Model scikit-learn beda versi | Catat warning, validasi output distribusi prediksi |
| Review duplicate | Dedup by `target_penginapan_id + reviewId + cleaned_text` |
| Review tanpa teks | Exclude dari model |
| Nama target berubah | Merge by ID, bukan nama |
| Exact URL tidak return | Jangan dipaksa, bisa `sentiment_unavailable` |
| Villa/unit listing terlalu dominan | Turunkan prioritas kecuali user rombongan |
| Harga kosong | Hide atau tampilkan tidak tersedia |

## File Yang Jangan Dipakai Langsung

Raw JSON scrape jangan langsung dipakai untuk sentiment final:

| Jenis file | Kenapa |
|---|---|
| `dataset_Google-Maps-Reviews-Scraper_*.json` | Bisa ada noise dan salah tempat |
| Held review CSV | Sengaja ditahan karena tidak aman |
| Google Hotels raw JSON | Cocok untuk metadata/harga, bukan sentiment |

Gunakan file `ACCEPTED_REVIEWS` saja untuk model sentiment.

## Aturan Untuk Agent Berikutnya

1. Jangan pakai raw review JSON langsung.
2. Pakai hanya file `ACCEPTED_REVIEWS`.
3. Jangan overwrite dataset primary lama.
4. Jangan memaksa harga kosong untuk diisi.
5. Jangan buang penginapan hanya karena harga kosong.
6. Koordinat wajib.
7. Sentiment kosong boleh diberi fallback `sentiment_unavailable`.
8. LLM tidak boleh membuat skor sendiri.
9. Ranking hotel nantinya harus memberi bobot besar ke jarak.
10. Villa/vacation rental boleh ada, tetapi jangan menjadi pilihan utama untuk user umum 2 orang.

## Status Akhir Saat Dokumen Ini Dibuat

Status penginapan: `baseline usable, location-safe, price-partial, sentiment-ready-to-apply`.

Langkah paling dekat:

Apply 1852 accepted review rows, khusus 1186 review teks, ke model sentiment lokal lalu merge hasil agregasi ke dataset primary baru.

## Ringkasan Untuk Agent Baru

Jika agent baru hanya membaca satu bagian, baca ini:

1. Dataset primary terbaru ada 900 rows dan semua punya koordinat.
2. Harga kosong tidak perlu dikejar dulu.
3. Review sentiment yang aman sudah terkumpul 1852 rows.
4. Review teks untuk model ada 1186 rows.
5. Target penginapan dengan accepted review ada 67.
6. Model sentiment lokal ada di `Penginapan_Workspace\07_Models\model_sentimen_muterbandung.pkl`.
7. Belum ada dataset primary baru hasil apply sentiment 2026-06-14.
8. Tugas berikutnya adalah apply sentiment, agregasi per penginapan, merge ke primary baru, lalu audit coverage.
9. Jangan pakai raw JSON langsung.
10. Jangan overwrite file lama.
