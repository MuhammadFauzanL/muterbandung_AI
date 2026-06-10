# Muter Bandung AI Agent Skills and Project Context

Dokumen ini adalah onboarding context untuk AI agent yang melanjutkan project Muter Bandung. Tujuannya agar agent memahami arah project, status terakhir, dataset yang dipakai, batasan data, workflow engineering, dan prioritas implementasi berikutnya.

Format dokumen dibuat seperti 25 halaman ringkas. Setiap halaman adalah satu konteks kerja yang bisa dibaca cepat oleh agent sebelum melakukan perubahan.

---

## Halaman 01 - Identitas Project

Muter Bandung adalah sistem rekomendasi wisata Bandung Raya berbasis data curated, semantic search, filter praktis, sentiment metadata, dan guardrail untuk LLM.

Tujuan utama project:

- Membantu user menemukan tempat wisata sesuai gaya liburan.
- Menyediakan alasan rekomendasi yang bisa dipercaya.
- Menyediakan data praktis: harga, jam buka, fasilitas, rating, durasi, media, dan jarak.
- Menambahkan hotel/penginapan sebagai fitur pendukung itinerary, bukan sebagai marketplace utama.
- Menjaga AI/LLM agar tidak mengarang data yang tidak tersedia.

Agent harus melihat project ini sebagai **AI travel recommender**, bukan sekadar katalog wisata.

---

## Halaman 02 - Prinsip Produk

Prinsip produk Muter Bandung:

1. Wisata adalah pusat pengalaman.
2. Hotel membantu user menginap setelah destinasi dipilih.
3. User tidak boleh dipaksa memahami semua field dataset.
4. UI harus memprioritaskan filter yang mudah dimengerti.
5. Data kosong harus ditandai, bukan ditutupi.
6. LLM hanya boleh menyampaikan klaim yang didukung payload backend.
7. Ranking harus menggabungkan relevansi, kualitas data, sentiment, rating, harga, waktu, dan jarak.

Jika ada konflik antara fitur bagus dan data yang belum kuat, pilih data safety lebih dulu.

---

## Halaman 03 - Status Terakhir Project

Status per 2026-06-01:

- Dataset wisata curated utama sudah ada.
- Dataset hotel canonical sudah ada.
- Dataset hotel training dari Google Hotels Search sudah dibuat.
- Batch JSON scraping review hotel dari CSV lama sudah dibuat.
- Server Flask Muter Bandung bisa dijalankan di `http://127.0.0.1:5000`.
- Endpoint `/api/recommend` sudah berhasil dites.
- Frontend ada di `Scripts/templates/index.html`, `Scripts/static/style.css`, dan `Scripts/static/script.js`.
- Backend entry point ada di `Scripts/app.py`.
- Core recommender ada di `Scripts/recommender.py`.

Server terakhir berhasil menampilkan rekomendasi untuk query `wisata alam keluarga murah`.

---

## Halaman 04 - File Penting

File dan folder penting:

| Path | Fungsi |
| --- | --- |
| `Scripts/app.py` | Flask app dan API utama. |
| `Scripts/recommender.py` | Core recommender wisata. |
| `Scripts/templates/index.html` | HTML frontend. |
| `Scripts/static/style.css` | Styling frontend. |
| `Scripts/static/script.js` | Logic frontend dan API call. |
| `Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv` | Dataset wisata curated utama. |
| `Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv` | Dataset hotel canonical lama. |
| `Penginapan_Workspace/02_Curated/HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv` | Dataset hotel training dari Google Hotels Search. |
| `Wisata_Workspace/02_Notebooks/wisata_training.ipynb` | Notebook utama training/curation wisata. |
| `Penginapan_Workspace/03_Notebooks/penginapan_training.ipynb` | Notebook khusus penginapan training. |
| `Dokumentasi_Sistem/` | Dokumentasi audit dan status. |

Agent harus membaca file terkait sebelum mengubah sistem.

---

## Halaman 05 - Dataset Wisata

Dataset wisata utama:

`Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`

Status:

- Total awal: 234 baris.
- Aktif setelah filter backend: 209 destinasi.
- Kolom: 87.
- Sudah punya kategori, labels, harga, jam buka, fasilitas, koordinat, sentiment, media, dan status curation.

Kolom penting:

- `location_id`
- `location_name`
- `category`
- `final_primary_intent`
- `final_core_labels`
- `price_min`
- `price_max`
- `jam_buka_weekday`
- `jam_tutup_weekday`
- `avg_rating`
- `sentiment_score`
- `total_ulasan`
- `latitude`
- `longitude`
- `media_available`
- `media_image_url`
- `display_status`
- `is_active_verified`

Dataset ini adalah sumber utama website.

---

## Halaman 06 - Kategori Wisata

Kategori besar yang tersedia di dataset wisata:

- Wisata Alam
- Rekreasi Keluarga
- Taman Kota
- Tempat Belajar
- Tempat Camping
- Tempat Belanja
- Wisata Satwa
- Tempat Kuliner
- Tempat Sejarah
- Tempat Ibadah
- Tempat Seni
- Wahana Air
- Tempat Budaya
- Penginapan Wisata
- Wisata Petualangan

Untuk UI, jangan tampilkan semua kategori sekaligus. Gunakan chip ringkas:

- Alam
- Keluarga
- Edukasi
- Kuliner
- Healing
- Malam

Kategori detail bisa masuk filter lanjutan.

---

## Halaman 07 - Intent Wisata

Intent utama dataset:

- Alam
- Keluarga
- Santai/Healing
- Edukasi
- Budaya
- Belanja
- Kuliner
- Sejarah
- Religi
- Petualangan

Agent harus membedakan `category` dan `intent`.

Contoh:

- `category = Wisata Alam`
- `intent = Healing`

User biasanya bicara dalam intent, bukan kategori formal. Query seperti "tempat sejuk buat keluarga" harus diarahkan ke intent `Alam`, `Keluarga`, dan mungkin `Santai/Healing`.

---

## Halaman 08 - Quality Flags Wisata

Beberapa field wisata digunakan sebagai guardrail:

- `price_verified`
- `night_verified`
- `indoor_verified`
- `child_friendly_verified`
- `parking_verified`
- `wheelchair_accessible_verified`
- `toilet_verified`
- `mushola_verified`
- `open_24h_verified`
- `safety_verified`
- `coordinate_verified`
- `sentiment_available`
- `media_available`

Aturan:

- Jangan klaim fasilitas jika flag tidak mendukung.
- Jangan klaim buka malam jika `night_verified` tidak benar.
- Jangan klaim murah jika harga tidak valid.
- Jangan tampilkan kartu visual utama jika `media_available` false.
- Data verifikasi harus memengaruhi ranking dan wording.

---

## Halaman 09 - Dataset Hotel Canonical

Dataset hotel canonical:

`Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv`

Status:

- 181 baris.
- 76 kolom.
- Error validasi: 0.
- Gate: `PASS_WITH_WARNINGS`.

Segment:

- `apartment`: 65
- `hotel`: 64
- `guest_house`: 36
- `villa`: 10
- `room_level_listing`: 5
- `vacation_rental`: 1

Dataset ini berasal dari file lama:

`Penginapan_Workspace/01_Raw_Data/dataset_hotel_original/dataset_hotel/dataset_hotel_cimahi_semua_kolom (2).csv`

Gunakan dataset ini untuk tahap pertama integrasi hotel karena lebih stabil dan semua koordinat terisi.

---

## Halaman 10 - Dataset Hotel Training Google Search

Dataset hotel training baru:

`Penginapan_Workspace/02_Curated/HOTEL_TRAINING_GOOGLE_SEARCH_2026-06-01.csv`

Status:

- 446 properti unik.
- 70 kolom.
- Berasal dari JSON Google Hotels Search.
- Semua raw type dari sumber terbaca sebagai `vacation rental`.
- Lebih banyak apartment, villa, dan rental listing.

Segment:

- `apartment`: 208
- `villa`: 97
- `vacation_rental`: 75
- `room_level_listing`: 24
- `guest_house`: 21
- `hotel`: 21

Jangan gabungkan langsung dengan canonical lama tanpa fuzzy matching dan dedup logic yang matang.

---

## Halaman 11 - Hotel Sebagai Fitur Pendukung

Hotel bukan fitur utama website. Hotel dipakai setelah user:

1. Memilih destinasi wisata.
2. Mengaktifkan `Butuh Penginapan`.
3. Membuat itinerary.

Cara menampilkan hotel:

- "Penginapan dekat destinasi ini"
- "Hotel terdekat dari rencana wisata"
- "Opsi menginap untuk keluarga"
- "Villa/apartment untuk rombongan"

Jangan membuat homepage seperti marketplace hotel dengan filter hotel penuh. Itu akan menggeser fokus produk.

---

## Halaman 12 - Filter Utama Website

Filter utama yang boleh terlihat langsung:

1. Search/query bebas.
2. Gaya liburan.
3. Budget.
4. Buka sekarang.
5. Dekat saya/radius.
6. Ramah anak.
7. Butuh penginapan.

Filter utama harus menggunakan bahasa user:

- Alam
- Keluarga
- Gratis
- Buka Sekarang
- Dekat Saya
- Butuh Penginapan

Jangan menampilkan field teknis seperti `sentiment_available` atau `review_confidence_label` sebagai filter utama.

---

## Halaman 13 - Filter Lanjutan

Filter lanjutan boleh berisi:

- Minimal rating.
- Mode ranking.
- Jam rencana detail.
- Indoor/outdoor.
- Toilet.
- Mushola.
- Parkir.
- Akses kursi roda.
- Crowd level.
- Sentiment confidence.
- Status verifikasi.
- Fasilitas hotel detail.

Filter lanjutan sebaiknya collapsible/drawer.

Default harus sederhana. Jika user tidak membuka advanced filter, sistem tetap harus bisa memberi rekomendasi yang baik.

---

## Halaman 14 - UI Frontend Saat Ini

Frontend saat ini:

- HTML: `Scripts/templates/index.html`
- CSS: `Scripts/static/style.css`
- JS: `Scripts/static/script.js`

UI sudah memiliki:

- Sidebar filter.
- Search bar.
- Category chips.
- Price/rating/time/radius controls.
- Result cards.
- Media image.
- Score badge.
- Explanation box.
- Score breakdown.

Masalah UX saat ini:

- Sidebar terlalu penuh.
- Banyak kategori muncul sekaligus.
- Filter teknis terlihat terlalu cepat.
- Hotel belum diintegrasikan sebagai panel pendukung.

Prioritas UI berikutnya adalah menyederhanakan filter utama.

---

## Halaman 15 - Backend API

Backend utama:

`Scripts/app.py`

Endpoint:

- `GET /`
- `POST /api/recommend`
- `POST /api/llm/validate`

Payload rekomendasi menerima:

- `query`
- `categories`
- `max_price`
- `min_rating`
- `user_lat`
- `user_lon`
- `max_distance_km`
- `sort_by`
- `free_only`
- `open_now`
- `day_type`
- `open_at_hour`
- `top_k`

Agent harus menjaga kompatibilitas API jika mengubah frontend.

---

## Halaman 16 - Recommender Engine

Core recommender:

`Scripts/recommender.py`

Fungsi utama:

- Load dataset wisata.
- Filter active candidates.
- Parse labels.
- Load SentenceTransformer.
- Encode intent labels.
- Encode corpus.
- Compute recommendation score.
- Build explanation.
- Return structured results.

Model embedding:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Catatan:

- Loading model bisa lama.
- Server perlu waktu sebelum siap.
- Jangan pindahkan model ke runtime request.
- Precompute saat startup masih diterima untuk local dev.

---

## Halaman 17 - LLM Guardrail

LLM guardrail ada di:

- `Scripts/llm_evidence_pack.py`
- `Scripts/llm_guard.py`

Prinsip:

- LLM tidak boleh menjadi sumber fakta utama.
- LLM hanya boleh merangkai payload backend.
- Harga, jarak, rating, jam buka, dan fasilitas harus berasal dari data.
- Jika data tidak tersedia, LLM harus menyatakan tidak tersedia.
- Validasi output LLM harus bisa menolak klaim yang tidak ada evidence.

Jangan menambahkan LLM langsung ke UI sebelum evidence pack dan guard aktif.

---

## Halaman 18 - Sentiment Wisata

Wisata sudah punya sentiment metadata:

- `sentiment_score`
- `sentimen_label_lokasi`
- `sentiment_model_source`
- `sentiment_model_version`
- `sentiment_available`

Sentiment wisata berasal dari pipeline NLP/review sebelumnya.

Aturan:

- Jika `sentiment_available` false, jangan tampilkan skor sentiment sebagai pasti.
- Gunakan sentiment sebagai pendukung ranking, bukan satu-satunya penentu.
- Jangan membandingkan sentiment wisata dengan hotel secara langsung jika sumber datanya berbeda.

---

## Halaman 19 - Sentiment Hotel

Hotel canonical saat ini memakai rating-based sentiment:

- `rating_sentiment_score`
- `adjusted_rating_sentiment_score`
- `rating_sentiment_label`
- `adjusted_rating_sentiment_label`
- `review_confidence_label`

Ini bukan NLP komentar.

Alasannya:

- Dataset hotel belum punya raw review comment yang cukup.
- Data yang tersedia adalah rating, jumlah review, dan distribusi bintang.

Jika review Google Maps hotel sudah berhasil discrape, baru buat pipeline NLP hotel yang terpisah dari wisata.

---

## Halaman 20 - Review Scraping Hotel

Batch scraping review hotel dari file lama sudah dibuat:

- Target CSV:
  `Penginapan_Workspace/02_Curated/hotel_old_csv_google_maps_review_targets_2026-06-01.csv`
- Batch folder:
  `Penginapan_Workspace/05_Apify_Review_Batches/Hotel_Review_Batches_Old_CSV`
- Test JSON:
  `Penginapan_Workspace/05_Apify_Review_Batches/Hotel_Review_Batches_Old_CSV/apify_hotel_google_maps_reviews_test_10.json`
- All JSON:
  `Penginapan_Workspace/05_Apify_Review_Batches/Hotel_Review_Batches_Old_CSV/apify_hotel_google_maps_reviews_all_181.json`

Aturan:

1. Jalankan test batch 10 dulu.
2. Cocokkan nama, koordinat, rating, dan alamat.
3. Baru lanjut batch 01 sampai 08.
4. Simpan hasil scraper sebagai dataset baru.
5. Jangan timpa dataset canonical.

---

## Halaman 21 - Validation Pipeline

Pipeline validasi penting:

- `Scripts/validate_curated_dataset.py`
- `Penginapan_Workspace/06_Scripts/validate_hotel_canonical_dataset.py`
- `Scripts/test_api_schema_snapshot.py`
- `Scripts/test_api_contract.py`
- `Scripts/test_recommender.py`
- `Scripts/test_llm_guard.py`
- `Scripts/test_llm_evidence_pack.py`

Agent harus menjalankan test yang relevan setelah perubahan.

Untuk frontend kecil:

- Tes server bisa dibuka.
- Tes `/api/recommend`.

Untuk perubahan recommender/API:

- Jalankan test API.
- Jalankan schema snapshot.
- Pastikan response tidak berubah diam-diam.

---

## Halaman 22 - Cara Menjalankan Project

Server lokal:

```powershell
$env:HOST='127.0.0.1'
$env:PORT='5000'
$env:FLASK_DEBUG='0'
.\.venv_clean_verify\Scripts\python.exe -u .\Scripts\app.py
```

URL:

`http://127.0.0.1:5000`

Catatan:

- Startup bisa lama karena load SentenceTransformer.
- Jika server dijalankan background, simpan log di `logs/`.
- Jika port 5000 dipakai, gunakan port lain dengan env `PORT`.

Tes API:

```powershell
$body = @{ query='wisata alam keluarga murah'; max_price=50000; min_rating=4; top_k=3 } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/recommend' -Method Post -ContentType 'application/json' -Body $body
```

---

## Halaman 23 - Prinsip Editing Code

Agent harus:

- Membaca file sebelum mengedit.
- Mengikuti pola project yang sudah ada.
- Tidak menghapus perubahan user.
- Tidak melakukan refactor besar tanpa kebutuhan.
- Menjaga kompatibilitas API.
- Menambahkan test jika mengubah behavior penting.
- Memisahkan data wisata dan hotel jika pipeline belum matang.
- Menulis dokumentasi singkat untuk perubahan penting.

Jangan:

- Mengarang data.
- Mengganti dataset utama tanpa backup.
- Menggabungkan hotel baru 446 dengan canonical 181 tanpa dedup.
- Menampilkan filter terlalu banyak di UI utama.
- Menjadikan LLM sebagai sumber fakta.

---

## Halaman 24 - Roadmap Terdekat

Roadmap yang paling masuk akal:

1. Sederhanakan filter frontend.
2. Tambahkan filter utama: gaya liburan, budget chip, buka sekarang, dekat saya, ramah anak, butuh penginapan.
3. Pindahkan filter teknis ke advanced drawer.
4. Buat panel detail destinasi.
5. Tambahkan rekomendasi hotel terdekat dari destinasi.
6. Scrape review hotel dari batch 181.
7. Build hotel NLP pipeline setelah review comment terkumpul.
8. Buat `hotel_recommendation_ready.csv`.
9. Integrasikan hotel ke API.
10. Baru masuk LLM itinerary yang menggabungkan wisata + hotel.

Prioritas sekarang adalah UX filter dan integrasi hotel sebagai pendukung, bukan memperbanyak model.

---

## Halaman 25 - Definisi Sukses

Project dianggap kuat jika:

- User bisa mengetik rencana liburan natural.
- Sistem memberi rekomendasi wisata yang relevan.
- Hasil bisa difilter tanpa membuat user bingung.
- Alasan rekomendasi jelas dan berbasis data.
- Harga, jam, fasilitas, dan rating tidak dihallucinate.
- Hotel muncul sebagai bantuan setelah wisata dipilih.
- Data kosong ditangani dengan wording aman.
- API stabil dan punya schema snapshot.
- Dataset wisata dan hotel terdokumentasi.
- Agent berikutnya bisa melanjutkan tanpa audit ulang dari nol.

Kalimat arah produk:

Muter Bandung adalah AI travel recommender untuk wisata Bandung Raya, dengan hotel sebagai pendukung itinerary, dibangun di atas dataset curated, quality flags, geospatial ranking, sentiment metadata, dan LLM guardrail.
