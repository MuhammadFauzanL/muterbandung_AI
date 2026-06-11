# Full System Audit Stage 2 - Dataset, Lineage, and Data Integrity

## Scope

Tahap 2 mengaudit dataset aktif dan lineage data MuterBandung. Fokusnya adalah kesiapan data sebagai pondasi sistem rekomendasi dan evidence pack LLM.

## Source Documents Reviewed

- `Dokumentasi_Sistem/DATA_LINEAGE_REPORT.md`
- `Dokumentasi_Sistem/SENTIMENT_LINEAGE_AUDIT.md`
- `Dokumentasi_Sistem/MEDIA_ENRICHMENT_AUDIT_2026-05-25.md`
- `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
- queue/audit CSV di `Dataset/3_Curated/`

## Active Dataset

Dataset aktif yang dipakai runtime:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Ringkasan:

```text
rows: 234
columns: 87
unique location_id: 234
duplicate location_id: 0
active_candidate: 213
exclude_scope: 17
status_uncertain: 3
temporarily_hidden: 1
```

Dataset ini adalah versi paling lengkap dibanding versi sebelumnya:

| File | Rows | Status |
|---|---:|---|
| `Dataset/2_Intermediate/DATABASE_WISATA_FINAL_LENGKAP.csv` | 232 | lama/minimal |
| `Dataset/2_Intermediate/DATABASE_MUTERBANDUNG_ENGINE.csv` | 232 | prototipe lama |
| `DATABASE_WISATA_DENGAN_METADATA.csv` | 234 | metadata dasar |
| `DATABASE_WISATA_FINAL_PARIPURNA.csv` | 234 | final lama, belum media/status reviewed |
| `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2.csv` | 234 | curated sebelum review |
| `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv` | 234 | aktif, paling lengkap |

## Integrity Checks

### Identity and Core Fields

```text
location_id: 234/234
location_name: 234/234
category: 234/234
latitude: 234/234
longitude: 234/234
deskripsi_google: 234/234
tags_sintetis: 234/234
multi_labels: 234/234
primary_intent: 234/234
core_labels: 234/234
```

Tidak ada koordinat kosong dan tidak ada koordinat yang keluar dari broad Bandung Raya bounds yang diuji saat audit.

### Active Candidate Distribution

Untuk 213 destinasi aktif:

```text
Wisata Alam: 78
Rekreasi Keluarga: 35
Taman Kota: 18
Tempat Belajar: 15
Tempat Camping: 10
Tempat Belanja: 9
Tempat Kuliner: 6
Wisata Satwa: 6
Tempat Sejarah: 6
Tempat Seni: 5
Tempat Ibadah: 5
Tempat Budaya: 4
Penginapan Wisata: 4
Wisata Petualangan: 4
Wahana Air: 4
Desa Wisata: 3
Rekreasi Alam: 1
```

Primary intent aktif:

```text
Alam: 93
Keluarga: 42
Santai/Healing: 19
Edukasi: 16
Budaya: 12
Belanja: 9
Kuliner: 6
Religi: 5
Sejarah: 5
Petualangan: 3
Ramah Anak: 3
```

## Price Data

Harga sudah konsisten secara struktur:

```text
price_min: 234/234
price_max: 234/234
price_type: 234/234
price_min_negative: 0
price_max_lt_min: 0
free_price_inconsistent: 0
```

Distribusi aktif:

```text
Per Orang: 161
Gratis: 51
Berbayar: 1
```

Verdict: **strong enough for deterministic budget filtering**, tetapi tetap perlu disclaimer karena harga wisata berubah.

## Opening Hours

Kelengkapan jam:

```text
jam_buka_weekday: 233/234
jam_tutup_weekday: 233/234
jam_buka_weekend: 232/234
jam_tutup_weekend: 232/234
```

Active candidates yang masih kurang:

```text
active_missing_weekday_hours: 2 cell
active_missing_weekend_hours: 4 cell
```

Lokasi aktif dengan jam weekend kosong:

```text
LOC-016 Chinatown Bandung
LOC-123 Museum Pendidikan Nasional UPI
```

Verdict: **mostly strong**, tetapi LLM tidak boleh mengklaim jam buka pasti tanpa evidence.

## Sentiment Data

Status sentiment aktif:

```text
sentiment_available true: 212
sentiment_available false: 22
sentiment_model_source tfidf_linearsvc: 212
sentiment_model_source unavailable: 22
sentiment_model_version run_nlp_pipeline_v2: 212
```

Untuk active candidates:

```text
active_sentiment_unavailable: 17
```

Lineage sentiment yang benar:

```text
MASTER_REVIEWS_ENRICHED.csv
-> Scripts/run_nlp_pipeline_v2.py
-> TF-IDF + LinearSVC
-> MASTER_REVIEWS_LABELED.csv
-> SENTIMENT_SCORES_PER_LOKASI.csv
-> DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Verdict: **acceptable and honest after metadata correction**. Jangan klaim skor aktif sebagai IndoBERT.

## Review Data

Review datasets:

```text
Dataset/MASTER_REVIEWS_ENRICHED.csv
- rows: 34,150
- location_name unique: 212
- duplicate location_name + review_text: 281

Dataset/MASTER_REVIEWS_LABELED.csv
- rows: 34,003
- location_name unique: 212
- duplicate location_name + review_text: 280

Dataset/SENTIMENT_SCORES_PER_LOKASI.csv
- rows: 212
- location_name unique: 212
```

Catatan: masih ada duplicate `location_name + review_text` sekitar 280 baris pada file review final/labeled. Ini tidak otomatis fatal karena reviewer berbeda bisa menulis teks sama, tetapi untuk rigor akademik sebaiknya audit dedup key diperketat ke:

```text
location_name + reviewer_name + review_text
```

atau dibuat laporan eksplisit bahwa duplikasi residual tidak memengaruhi agregasi secara signifikan.

## Media Data

Status media:

```text
media_available true: 181/234
media_available false: 53/234
active_media_unavailable: 44/213
media_image_url: 181/234
media_destination_url: 181/234
media_website: 75/234
```

Media enrichment konservatif:

```text
accepted media rows: 181/234
active candidate rows with media: 169/213
needs review/missing: 53
```

Verdict: **safe for LLM because unavailable media is explicitly marked**, tetapi belum lengkap untuk pengalaman UI yang kaya.

## Real-World Verification

Ini titik paling rawan.

```text
is_active_verified true: 15/234
is_active_verified false: 21/234
is_active_verified missing: 198/234
manual_realworld_verification_queue: 213 rows
HIGH priority: 144
MEDIUM priority: 69
```

Artinya hampir semua destinasi aktif masih punya item verifikasi real-world yang belum selesai, terutama fasilitas, status aktif, dan konteks penggunaan.

Verdict: **not yet strong enough for confident real-world claims by LLM**.

LLM harus memakai phrasing konservatif:

```text
"berdasarkan data yang tersedia"
"perlu dicek ulang sebelum berangkat"
"fasilitas belum terverifikasi"
```

## Manual Queues

Queue tersisa:

```text
manual_realworld_verification_queue.csv: 213 rows
manual_data_fill_queue.csv: 60 rows
manual_media_fill_queue.csv: 53 rows
local_scrape_unresolved_queue.csv: 78 rows
label_review_queue.csv: 18 rows
coordinate_audit.csv: 14 rows
```

Queue prioritas tinggi:

```text
manual_realworld_verification_queue: 144 HIGH
manual_media_fill_queue: 44 HIGH
local_scrape_unresolved_queue: 37 HIGH
manual_data_fill_queue: 16 HIGH
```

## Stage 2 Verdict

```text
DATA FOUNDATION FOR RECOMMENDATION: STRONG
DATA FOUNDATION FOR LLM EVIDENCE: GOOD WITH DISCLAIMERS
DATA FOUNDATION FOR REAL-WORLD CLAIMS: STILL WEAK
BIGGEST RISK: incomplete real-world verification, not missing core metadata
```

## Key Risks

### High

- `manual_realworld_verification_queue.csv` masih 213 baris.
- `is_active_verified` masih kosong untuk 198/234 baris.
- LLM bisa terdorong membuat klaim fasilitas/status bila prompt tidak sangat ketat.

### Medium

- 44 active candidates belum punya media.
- 17 active candidates belum punya sentiment.
- 2 active locations punya jam weekend kosong.
- Review labeled masih punya sekitar 280 duplicate `location_name + review_text`.

### Low

- 14 coordinate audit rows masih butuh review, tetapi broad coordinate bounds tidak menunjukkan titik keluar Bandung Raya pada dataset aktif.

## Recommended Fixes Before Full LLM

1. Selesaikan minimal HIGH priority di `manual_realworld_verification_queue.csv`.
2. Selesaikan 44 active media missing yang HIGH priority jika UI/LLM itinerary ingin visual.
3. Tambahkan explicit `verification_summary` di evidence pack:

```json
{
  "active_verified": true,
  "facilities_verified_count": 3,
  "facilities_unverified": ["parking", "toilet"],
  "safe_to_claim_realworld": false
}
```

4. Audit residual duplicate review rows dan dokumentasikan apakah aman.
5. Tambahkan `data_version` dan `curated_at` pada response API/evidence pack.

## Next Stage

Tahap 3 harus fokus ke:

- backend recommender,
- API contract,
- filter/scoring,
- no strong match,
- evidence pack integration,
- frontend/API surface.
