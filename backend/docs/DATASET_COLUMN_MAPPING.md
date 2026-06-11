# Dataset Column Mapping

> **Document version:** 1.1
> **Last updated:** 2026-06-11
> **Phase:** Phase 1 — Dataset Column Mapping & Naming Contract

---

## 1. Purpose

Dokumen ini adalah **kontrak mapping** resmi antara dataset CSV hasil AI/data pipeline dengan struktur backend (database, API, dan service layer).

Prinsip utama:

- **Dataset CSV tidak diedit langsung.** File CSV adalah raw source yang dihasilkan oleh AI/data pipeline. Tidak boleh ada edit manual terhadap header, isi kolom, atau urutan baris.
- **Backend melakukan transformasi saat proses import.** Semua konversi nama kolom, format data, parsing semicolon-delimited labels, dan filtering dilakukan oleh import script pada phase berikutnya.
- **File CSV tetap menjadi raw source.** Jika ada perubahan data, pipeline upstream yang menghasilkan CSV baru — bukan edit manual.
- **Dokumen ini menjadi acuan** untuk membuat model database, migration, import script, dan API endpoint pada phase-phase berikutnya.

---

## 2. Naming Convention

### Backend (English, snake_case)

Semua komponen teknis backend menggunakan **Bahasa Inggris**:

| Komponen | Convention | Contoh |
|----------|-----------|--------|
| Database table | English, plural, snake_case | `destinations`, `destination_media` |
| Database column | English, snake_case | `external_id`, `total_reviews`, `avg_rating` |
| API route | English, plural resource, lowercase | `GET /destinations`, `GET /destinations/{slug}` |
| Pydantic schema | English, PascalCase | `DestinationCreate`, `DestinationResponse` |
| Service class/function | English, snake_case | `destination_service.py`, `get_popular()` |
| Python file | English, snake_case | `destination.py`, `import_destinations.py` |

### Frontend Response (camelCase)

API response untuk frontend Next.js/TypeScript menggunakan **camelCase**:

| Contoh Key | Tipe |
|------------|------|
| `imageUrl` | string |
| `priceLabel` | string |
| `totalReviews` | integer |
| `heroImageUrl` | string |
| `mapsUrl` | string |

### Content yang Tampil ke User (Bahasa Indonesia)

Konten yang ditampilkan ke pengguna akhir tetap menggunakan **Bahasa Indonesia**:

| Contoh | Konteks |
|--------|---------|
| Wisata Alam | Kategori destinasi |
| Gratis | Label harga |
| Ramah Anak | Label fasilitas |
| Destinasi Populer Bandung | Section title di homepage |

---

## 3. Source Dataset

**Path:**

```
backend/data/wisata_populer.csv
```

**Origin:**

```
ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv
```

| Properti | Nilai |
|----------|-------|
| Total kolom | 88 |
| Total baris data | 234 (excl. header) |
| Encoding | UTF-8 with BOM |
| Delimiter | Comma (`,`) |
| Quoting | Double-quote (`"`) |

> [!CAUTION]
> File ini adalah **raw source** dan **tidak boleh diedit manual**. Semua transformasi dilakukan oleh import script pada phase berikutnya.

---

## 4. MVP Columns

Berikut adalah mapping kolom dataset yang digunakan untuk MVP awal, dikelompokkan per domain.

---

### 4.1 Destination Main Data

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `location_id` | `destinations.external_id` | VARCHAR(20) | ID asli dari dataset (e.g. `LOC-001`) |
| `location_name` | `destinations.name` | VARCHAR(255) | Nama destinasi |
| `category` | `destinations.category` | VARCHAR(100) | Kategori utama (e.g. `Tempat Belanja`) |
| `subcategory` | `destinations.subcategory` | VARCHAR(100) | Subkategori (e.g. `Mall`) |
| `deskripsi_google` | `destinations.description` | TEXT | Deskripsi destinasi |
| `estimasi_durasi_menit` | `destinations.estimated_duration_minutes` | INTEGER | Estimasi durasi kunjungan |
| `crowd_level` | `destinations.crowd_level` | VARCHAR(20) | Tingkat keramaian (`low` / `medium` / `high`) |
| `tags_sintetis` | `destinations.synthetic_tags` | JSONB | Comma-separated tags sintetis, diubah menjadi array saat import |
| `zona_wisata` | `destinations.tourism_zone` | VARCHAR(100) | Zona/area wisata, digunakan untuk label lokasi pada card dan halaman detail |

> [!NOTE]
> **`tags_sintetis`** pada CSV berbentuk comma-separated string. Saat import, field ini sebaiknya diubah menjadi JSON array agar lebih mudah digunakan untuk filtering, search, dan recommendation logic.
>
> ```
> CSV:  "Belanja, Indoor, Kuliner, Modern"
> DB:   ["Belanja", "Indoor", "Kuliner", "Modern"]
> ```

> [!NOTE]
> **`zona_wisata`** digunakan untuk menampilkan lokasi ringkas seperti Ciwidey, Lembang, Cimahi, Bandung Kota, atau area wisata lain. Jika nilai `zona_wisata` kosong, frontend boleh fallback ke `"Bandung Raya"`.

---

### 4.2 Location and Maps

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `latitude` | `destinations.latitude` | FLOAT | Latitude destinasi |
| `longitude` | `destinations.longitude` | FLOAT | Longitude destinasi |
| `media_destination_url` | `destination_media.maps_url` | TEXT | Link Google Maps |
| `coordinate_verified` | `destinations.coordinate_verified` | BOOLEAN | Status validasi koordinat |
| `distance_from_alun_alun_km` | `destinations.distance_from_center_km` | FLOAT | Jarak dari Alun-Alun Bandung (pusat kota) |

---

### 4.3 Price

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `price_min` | `destinations.price_min` | INTEGER | Harga minimum (Rupiah) |
| `price_max` | `destinations.price_max` | INTEGER | Harga maksimum (Rupiah) |
| `price_type` | `destinations.price_type` | VARCHAR(50) | Jenis harga (`Gratis` / `Per Orang` / etc.) |

**Frontend price label logic:**

| Kondisi | Label Frontend |
|---------|---------------|
| `price_min = 0` dan `price_max = 0` | `Gratis` |
| `price_min = price_max` (> 0) | `Rp xx.xxx` |
| `price_min ≠ price_max` | `Rp xx.xxx - Rp yy.yyy` |

---

### 4.4 Opening Hours

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `jam_buka` | `destinations.opening_time` | VARCHAR(10) | Jam buka umum (e.g. `10:00`) |
| `jam_tutup` | `destinations.closing_time` | VARCHAR(10) | Jam tutup umum |
| `jam_buka_weekday` | `destinations.weekday_opening_time` | VARCHAR(10) | Jam buka weekday |
| `jam_tutup_weekday` | `destinations.weekday_closing_time` | VARCHAR(10) | Jam tutup weekday |
| `jam_buka_weekend` | `destinations.weekend_opening_time` | VARCHAR(10) | Jam buka weekend |
| `jam_tutup_weekend` | `destinations.weekend_closing_time` | VARCHAR(10) | Jam tutup weekend |
| `open_24h_verified` | `destination_facilities.open_24h` | BOOLEAN | Status buka 24 jam |

---

### 4.5 Rating and Sentiment

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `avg_rating` | `destinations.avg_rating` | FLOAT | Rating rata-rata (skala 1-5) |
| `total_ulasan` | `destinations.total_reviews` | INTEGER | Jumlah ulasan |
| `ulasan_positif` | `destinations.positive_reviews` | INTEGER | Jumlah ulasan positif |
| `ulasan_negatif` | `destinations.negative_reviews` | INTEGER | Jumlah ulasan negatif |
| `sentimen_label_lokasi` | `destinations.sentiment_label` | VARCHAR(20) | Label sentimen (`Positif` / `Negatif` / `Netral`) |
| `sentiment_score` | `destinations.sentiment_score` | FLOAT | Skor sentimen utama (0.0 - 1.0) |
| `avg_sentimen_skor` | `destinations.avg_sentiment_score` | FLOAT | Fallback skor sentimen |
| `sentiment_available` | `destinations.sentiment_available` | BOOLEAN | Status ketersediaan data sentiment |

> [!NOTE]
> **Prioritas sentiment score:** `sentiment_score` adalah nilai utama. `avg_sentimen_skor` hanya digunakan sebagai fallback jika `sentiment_score` kosong atau null.

---

### 4.6 AI Labels

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `final_primary_intent` | `destination_labels.primary_intent` | VARCHAR(100) | Intent utama hasil AI |
| `final_core_labels` | `destination_labels.core_labels` | JSONB | Label utama hasil AI |
| `final_secondary_labels` | `destination_labels.secondary_labels` | JSONB | Label tambahan |
| `final_avoid_labels` | `destination_labels.avoid_labels` | JSONB | Label yang harus dihindari |
| `label_confidence` | `destination_labels.label_confidence` | FLOAT | Confidence score (0.0 - 1.0) |
| `final_label_source` | `destination_labels.label_source` | VARCHAR(50) | Sumber label final (`auto_rule_v1` / `manual`) |
| `label_scores_json` | `destination_labels.label_scores` | JSONB | Skor per-label dalam JSON |

> [!IMPORTANT]
> **Transformasi saat import:** Kolom `final_core_labels`, `final_secondary_labels`, dan `final_avoid_labels` di CSV berbentuk string yang dipisah dengan **semicolon (`;`)**.
> Saat import, string ini harus diubah menjadi array JSON.
>
> **Contoh:**
> ```
> CSV:  "Belanja;Indoor;Gratis"
> DB:   ["Belanja", "Indoor", "Gratis"]
> ```

---

### 4.7 Media

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `media_available` | `destination_media.media_available` | BOOLEAN | Status ketersediaan media |
| `media_image_url` | `destination_media.image_url` | TEXT | URL gambar utama |
| `media_destination_url` | `destination_media.maps_url` | TEXT | URL Google Maps |
| `media_website` | `destination_media.website_url` | TEXT | Website resmi (jika ada) |
| `media_source` | `destination_media.media_source` | VARCHAR(100) | Sumber media (e.g. `google_maps_extractor_2026_05_19`) |
| `media_place_id` | `destination_media.place_id` | VARCHAR(100) | Google Place ID |
| `media_audit_status` | `destination_media.media_audit_status` | VARCHAR(20) | Status audit media (`accepted` / `rejected` / `pending`) |

---

### 4.8 Facilities

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `parking_verified` | `destination_facilities.parking_available` | BOOLEAN | Parkir tersedia |
| `wheelchair_accessible_verified` | `destination_facilities.wheelchair_accessible` | BOOLEAN | Akses difabel |
| `toilet_verified` | `destination_facilities.toilet_available` | BOOLEAN | Toilet tersedia |
| `mushola_verified` | `destination_facilities.mushola_available` | BOOLEAN | Mushola tersedia |
| `pet_friendly_verified` | `destination_facilities.pet_friendly` | BOOLEAN | Pet friendly |
| `open_24h_verified` | `destination_facilities.open_24h` | BOOLEAN | Buka 24 jam |
| `child_friendly_verified` | `destination_facilities.child_friendly` | BOOLEAN | Ramah anak |
| `night_verified` | `destination_facilities.night_available` | BOOLEAN | Cocok untuk kunjungan malam |
| `indoor_verified` | `destination_facilities.indoor_available` | BOOLEAN | Indoor / ruangan tertutup |
| `safety_verified` | `destination_facilities.safety_verified` | BOOLEAN | Keamanan terverifikasi |

---

### 4.9 Data Display Status

| Dataset Column | Backend Target | Type | Notes |
|---------------|---------------|------|-------|
| `curation_action` | `destinations.curation_action` | VARCHAR(20) | Status kurasi (`keep` / `remove`) |
| `display_status` | `destinations.display_status` | VARCHAR(30) | Status tampil (`active_candidate` / `exclude_scope` / `temporarily_hidden`) |
| `is_active_verified` | `destinations.is_active` | BOOLEAN | Status aktif (diverifikasi) |
| `media_available` | `destination_media.media_available` | BOOLEAN | Status ketersediaan media |
| `coordinate_verified` | `destinations.coordinate_verified` | BOOLEAN | Status koordinat terverifikasi |

**Active Data Filter untuk MVP:**

Data **boleh ditampilkan** ke frontend jika:

```
curation_action       = "keep"
display_status        = "active_candidate"
media_available       = True
coordinate_verified   = True
```

Data **tidak boleh ditampilkan** ke frontend jika salah satu terpenuhi:

```
curation_action       = "remove"
display_status        = "exclude_scope"
display_status        = "temporarily_hidden"
media_available       = False
```

> [!NOTE]
> `is_active_verified` tetap disimpan ke `destinations.is_active`, tetapi **tidak menjadi filter wajib pada MVP** karena sebagian data aktif masih dapat memiliki nilai kosong. Filter utama MVP tetap menggunakan `curation_action`, `display_status`, `media_available`, dan `coordinate_verified`.

---

## 5. Internal Metadata Columns

Kolom-kolom berikut **tidak dikirim ke frontend pada MVP**, tetapi disimpan di database sebagai raw metadata (JSONB) atau audit trail untuk keperluan debugging dan monitoring kualitas data.

| Dataset Column | Kategori | Notes |
|---------------|----------|-------|
| `label_reason` | AI Audit | Alasan penentuan label oleh AI rule engine |
| `review_reason` | AI Audit | Alasan jika label butuh manual review |
| `curation_note` | Curation | Catatan kurasi dataset |
| `qa_flag_reason` | QA | Alasan flag quality assurance |
| `coordinate_audit_reason` | Geo Audit | Alasan audit koordinat |
| `media_audit_note` | Media Audit | Catatan audit media |
| `sentiment_model_source` | ML Metadata | Sumber model sentiment (e.g. `tfidf_linearsvc`) |
| `sentiment_model_version` | ML Metadata | Versi pipeline sentiment (e.g. `run_nlp_pipeline_v2`) |
| `manual_primary_intent` | Manual Review | Intent dari manual review (jika ada) |
| `manual_core_labels` | Manual Review | Core labels dari manual review |
| `manual_secondary_labels` | Manual Review | Secondary labels dari manual review |
| `manual_avoid_labels` | Manual Review | Avoid labels dari manual review |
| `manual_review_confidence` | Manual Review | Confidence score reviewer |
| `media_match_title` | Media Matching | Judul yang di-match untuk media |
| `media_match_score` | Media Matching | Skor kecocokan media match |
| `media_match_method` | Media Matching | Metode matching (e.g. `exact_normalized_title`) |
| `label_scores_json` | AI Scores | Skor detail per-label dalam JSON |
| `media_audit_status` | Media Audit | Status audit media |
| `multi_labels` | Legacy | Multi-label lama (sebelum AI labeling v2) |
| `sumber_deskripsi` | Data Source | Sumber deskripsi |
| `sumber_jam` | Data Source | Sumber data jam operasional |
| `status_deskripsi` | Data Source | Status kelengkapan deskripsi |
| `status_jam` | Data Source | Status kelengkapan jam |
| `catatan_jam` | Data Source | Catatan khusus jadwal |
| `primary_intent` | Legacy AI | Intent awal sebelum review (raw) |
| `core_labels` | Legacy AI | Core labels awal sebelum review (raw) |
| `secondary_labels` | Legacy AI | Secondary labels awal sebelum review (raw) |
| `avoid_labels` | Legacy AI | Avoid labels awal sebelum review (raw) |
| `label_source` | Legacy AI | Sumber label awal |
| `needs_manual_review` | Review Flow | Flag kebutuhan manual review |
| `review_status` | Review Flow | Status review (`auto_approved` / `manually_reviewed`) |
| `price_verified` | Verification | Status verifikasi harga |
| `shopping_subtype` | Extra | Sub-tipe belanja jika kategori belanja |

> [!NOTE]
> - Kolom-kolom di atas **tidak digunakan langsung untuk UI** pada MVP.
> - Berguna untuk **audit, debugging, dan monitoring** kualitas hasil AI/data pipeline.
> - Pada phase awal, cukup didokumentasikan di sini.
> - Penyimpanan ke tabel metadata database (misalnya sebagai JSONB column `raw_metadata`) bisa dilakukan di phase berikutnya jika diperlukan.
> - Beberapa kolom seperti `label_scores_json` dan `media_audit_status` tetap boleh disimpan pada tabel domain masing-masing, misalnya `destination_labels.label_scores` dan `destination_media.media_audit_status`, tetapi **tidak dikirim ke frontend pada MVP**. Jadi, "disimpan di database" tidak selalu berarti "diekspos ke frontend".

---

## 6. Planned Backend Tables

Tabel-tabel berikut akan dibuat pada phase berikutnya. **Jangan membuat model/migration sekarang.**

### `destinations`

Tabel utama yang menyimpan data inti setiap destinasi wisata:
- Identitas: `external_id`, `name`, `slug`, `description`
- Klasifikasi: `category`, `subcategory`, `crowd_level`, `synthetic_tags`
- Lokasi: `latitude`, `longitude`, `tourism_zone`, `distance_from_center_km`, `coordinate_verified`
- Harga: `price_min`, `price_max`, `price_type`
- Jam operasional: `opening_time`, `closing_time`, `weekday_*`, `weekend_*`
- Rating & sentiment: `avg_rating`, `total_reviews`, `positive_reviews`, `negative_reviews`, `sentiment_score`, `sentiment_label`, `sentiment_available`
- Durasi: `estimated_duration_minutes`
- Status: `curation_action`, `display_status`, `is_active`
- Timestamps: `created_at`, `updated_at`

### `destination_media`

Menyimpan informasi media (gambar, link, website) per destinasi:
- `destination_id` (FK ke `destinations`)
- `image_url`, `maps_url`, `website_url`
- `media_available`, `media_source`, `place_id`
- `media_audit_status`

### `destination_labels`

Menyimpan label AI dan confidence score per destinasi:
- `destination_id` (FK ke `destinations`)
- `primary_intent`, `core_labels`, `secondary_labels`, `avoid_labels`
- `label_confidence`, `label_source`, `label_scores`

### `destination_facilities`

Menyimpan data fasilitas per destinasi:
- `destination_id` (FK ke `destinations`)
- `parking_available`, `wheelchair_accessible`, `toilet_available`
- `mushola_available`, `pet_friendly`, `open_24h`
- `child_friendly`, `night_available`, `indoor_available`
- `safety_verified`

---

## 7. Planned API Routes

Route berikut akan diimplementasikan pada phase berikutnya. **Jangan buat sekarang.**

Semua route menggunakan **Bahasa Inggris** dan **plural resource**.

| Method | Route | Description | Phase |
|--------|-------|-------------|-------|
| `GET` | `/destinations/popular` | Homepage "Destinasi Populer Bandung" | Phase 3 |
| `GET` | `/destinations/{slug}` | Detail halaman destinasi | Phase 3 |
| `GET` | `/destinations` | List & filter destinasi (query params) | Phase 3 |
| `GET` | `/destination-categories/highlights` | Section kategori di homepage | Phase 3 |

**Query parameters untuk `GET /destinations`:**

```
?category=Wisata+Alam
&price_type=Gratis
&child_friendly=true
&page=1
&limit=10
&sort=rating
```

---

## 8. Planned Frontend Response Shape

### 8.1 Popular Destination Card Response

Digunakan untuk card destinasi di homepage dan list view:

```json
{
  "id": "LOC-002",
  "slug": "alam-wisata-cimahi",
  "name": "Alam Wisata Cimahi",
  "category": "Rekreasi Keluarga",
  "imageUrl": "https://lh3.googleusercontent.com/...",
  "rating": 4.4,
  "priceLabel": "Gratis",
  "location": "Cimahi",
  "tourismZone": "Cimahi",
  "isFavorite": false
}
```

> [!NOTE]
> - `location` adalah label lokasi siap tampil untuk UI.
> - `tourismZone` berasal dari kolom `zona_wisata` di dataset.
> - Jika `tourismZone` kosong, backend boleh fallback ke `"Bandung Raya"`.

### 8.2 Destination Detail Response

Digunakan untuk halaman detail destinasi:

```json
{
  "id": "LOC-002",
  "slug": "alam-wisata-cimahi",
  "name": "Alam Wisata Cimahi",
  "category": "Rekreasi Keluarga",
  "tourismZone": "Cimahi",
  "description": "Destinasi eduwisata populer di Cimahi yang menawarkan berbagai wahana permainan...",
  "heroImageUrl": "https://lh3.googleusercontent.com/...",
  "rating": {
    "value": 4.4,
    "totalReviews": 1068,
    "label": "4.4 / 5.0"
  },
  "ticket": {
    "priceMin": 0,
    "priceMax": 0,
    "priceType": "Gratis",
    "label": "Gratis"
  },
  "openingHours": {
    "weekday": "08:00 - 17:00",
    "weekend": "08:00 - 21:00"
  },
  "location": {
    "label": "Cimahi",
    "latitude": -6.8408401,
    "longitude": 107.5512452,
    "mapsUrl": "https://www.google.com/maps/search/?api=1&query=..."
  },
  "aiRecommendation": {
    "title": "Mengapa Cepot AI Merekomendasikan Ini?",
    "reason": "Destinasi ini cocok untuk wisata keluarga karena memiliki label Keluarga, Kuliner, Alam, Ramah Anak, dan Edukasi.",
    "tags": ["Keluarga", "Kuliner", "Alam", "Ramah Anak", "Edukasi"]
  },
  "facilities": [
    { "key": "parking", "label": "Parkir", "available": true },
    { "key": "toilet", "label": "Toilet", "available": true },
    { "key": "mushola", "label": "Mushola", "available": true },
    { "key": "wheelchair", "label": "Akses Difabel", "available": false },
    { "key": "childFriendly", "label": "Ramah Anak", "available": true },
    { "key": "petFriendly", "label": "Pet Friendly", "available": false },
    { "key": "indoor", "label": "Indoor", "available": true },
    { "key": "nightVisit", "label": "Kunjungan Malam", "available": false }
  ]
}
```

---

## 9. Phase 1 Output

Phase ini **hanya** menghasilkan file berikut:

```
backend/docs/DATASET_COLUMN_MAPPING.md   ← dokumen ini
```

**Tidak dibuat pada phase ini:**

- ❌ Model SQLAlchemy
- ❌ Migration Alembic
- ❌ Script import CSV
- ❌ Endpoint API / Router FastAPI
- ❌ Service layer
- ❌ Schema Pydantic
- ❌ Perubahan database
- ❌ Cleaned / transformed CSV

---

## 10. Acceptance Criteria

| # | Kriteria | Status |
|---|----------|--------|
| 1 | File `backend/docs/DATASET_COLUMN_MAPPING.md` dibuat | ✅ |
| 2 | Naming convention backend didokumentasikan | ✅ |
| 3 | Kolom CSV dipetakan ke nama kolom backend | ✅ |
| 4 | Kolom MVP didokumentasikan per domain | ✅ |
| 5 | Kolom internal metadata didokumentasikan | ✅ |
| 6 | Active data filter didokumentasikan | ✅ |
| 7 | Planned backend tables didokumentasikan | ✅ |
| 8 | Planned API routes didokumentasikan | ✅ |
| 9 | Planned frontend response shape didokumentasikan | ✅ |
| 10 | CSV asli tidak diubah | ✅ |
| 11 | Tidak ada model/migration/endpoint/service/schema dibuat | ✅ |
| 12 | Revisi audit kecil sudah diterapkan: total kolom, `zona_wisata`, `tags_sintetis` JSONB, catatan `is_active_verified`, dan response `tourismZone` | ✅ |
