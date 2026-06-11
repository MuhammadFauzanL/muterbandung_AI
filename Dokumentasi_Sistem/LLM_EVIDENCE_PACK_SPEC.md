# LLM Evidence Pack Specification

## Status

```text
IMPLEMENTED - 2026-05-24
```

Evidence pack dibuat untuk memberi LLM data ringkas dan terkontrol dari backend rekomendasi. LLM tidak membaca seluruh dataset dan tidak boleh membuat fakta baru.

## Active API Field

Endpoint:

```text
POST /api/recommend
```

Response sekarang menambahkan:

```text
llm_evidence_pack
llm_prompt_guard
```

Builder:

```text
Scripts/llm_evidence_pack.py
Scripts/llm_guard.py
```

Integrasi:

```text
Scripts/app.py
```

## Schema Version

```text
muterbandung.llm_evidence_pack.v1
```

## Top-Level Fields

```json
{
  "schema_version": "muterbandung.llm_evidence_pack.v1",
  "purpose": "Evidence for LLM explanation layer. Ranking remains controlled by backend.",
  "query": "wisata alam sejuk",
  "backend_status": "success",
  "ranking_policy": {},
  "input_context": {},
  "source_fields": {},
  "global_limitations": [],
  "candidates": []
}
```

## Ranking Policy

```json
{
  "source": "deterministic_backend",
  "llm_may_explain": true,
  "llm_may_rerank": false,
  "llm_may_create_destinations": false,
  "allowed_destination_ids": ["LOC-221", "LOC-113"]
}
```

Aturan penting:

- LLM hanya boleh membahas destinasi yang ada di `allowed_destination_ids`.
- LLM tidak boleh menambah destinasi baru.
- LLM belum boleh mengubah ranking.
- Ranking tetap berasal dari backend deterministic.

## Candidate Fields

Setiap kandidat berisi:

```json
{
  "destination_id": "LOC-221",
  "rank": 1,
  "name": "Glamping Legok Kondang",
  "category": "Tempat Camping",
  "primary_intent": "Alam",
  "core_labels": ["Alam", "Petualangan", "Outdoor"],
  "secondary_labels": [],
  "multi_labels": ["Alam", "Petualangan", "Outdoor", "Kuliner", "Santai/Healing"],
  "final_score": 82.72,
  "backend_reason": "Alasan rekomendasi dari backend.",
  "practical_info": {
    "price": "Rp 250.000 - Rp 1.500.000 (Berbayar)",
    "opening_hours": {
      "weekday": "00:00 - 23:59",
      "weekend": "00:00 - 23:59"
    },
    "duration": "90 menit",
    "coordinates": [-7.1181959, 107.4202751],
    "distance_km": null,
    "distance_label": ""
  },
  "sentiment": {
    "score": 0.9615,
    "label": "Sangat Positif",
    "model_source": "tfidf_linearsvc",
    "model_version": "run_nlp_pipeline_v2",
    "available": true,
    "review_count": 52
  },
  "media": {
    "available": true,
    "image_url": "https://lh3.googleusercontent.com/...",
    "destination_url": "https://www.google.com/maps/search/?api=1&query=...",
    "website": "",
    "source": "google_maps_extractor_2026_05_19",
    "match_title": "Glamping Legok Kondang Lodge",
    "match_score": 1.0,
    "audit_status": "accepted"
  },
  "realworld_flags": {
    "coordinate_verified": true,
    "safety_verified": true,
    "crowd_level": "unknown"
  },
  "score_signals": {
    "similarity": 0.6921,
    "google_rating": 4.81,
    "confidence": 0.5611,
    "matched_intents": ["Alam"],
    "penalized_intents": [],
    "distance_score": null,
    "ranking_mode": "relevance"
  },
  "limitations": []
}
```

## Limitations

Global limitations wajib dibaca LLM:

- LLM must only discuss destinations listed in `allowed_destination_ids`.
- LLM must not invent destinations, prices, distances, opening hours, ratings, or facilities.
- LLM must not invent image URLs, destination URLs, or websites.
- Image and destination URLs may be shown only when `candidate.media.available` is `true`.
- Prices and opening hours can change and should be rechecked before visiting.
- A false facility flag can mean unavailable or not verified in the dataset.
- Active sentiment source is `tfidf_linearsvc`, not IndoBERT.

## Prompt Guard And Output Validator

Status 2026-05-25:

```text
IMPLEMENTED
```

Field API:

```text
llm_prompt_guard
```

Endpoint validator:

```text
POST /api/llm/validate
```

Modul:

```text
Scripts/llm_guard.py
```

Kontrak validator:

- output LLM harus JSON object.
- `selected_destination_ids` harus subset dari `allowed_destination_ids`.
- urutan id wajib mengikuti ranking backend selama `llm_may_rerank=false`.
- nama, harga, jam buka, jarak, sentiment, media URL, dan flag harus sama persis dengan evidence.
- URL gambar/link ditolak kalau tidak ada di `candidate.media`.
- field fasilitas bebas seperti `facilities`/`amenities` ditolak; fasilitas harus memakai `realworld_flags` yang sudah ada.
- klaim harga, jarak, URL, rating, dan fasilitas dalam teks ikut dicek dengan regex defensif.

Catatan media:

- Media enrichment aktif sejak 2026-05-25 melalui `Scripts/enrich_media_metadata.py`.
- Dataset curated aktif memiliki kolom `media_*`.
- Kandidat tanpa match aman tetap ditandai `media.available=false`.
- Raw Apify/Google Maps hanya dipakai jika match exact, fuzzy high-confidence, atau manual override eksplisit.

## Validation

Evaluator yang mengecek evidence pack:

```text
Scripts/evaluate_groundtruth.py
scratch_qc.py
Scripts/test_llm_evidence_pack.py
Scripts/test_llm_guard.py
```

Pengecekan utama:

- `llm_evidence_pack` wajib ada.
- schema version harus `muterbandung.llm_evidence_pack.v1`.
- `llm_may_create_destinations` harus `false`.
- `llm_may_rerank` harus `false`.
- `allowed_destination_ids` harus sama dengan candidate ids.
- candidate wajib membawa practical info, sentiment provenance, real-world flags, dan backend reason.
- candidate wajib membawa kontrak `media`.
- response wajib membawa `llm_prompt_guard`.
- validator wajib menolak destinasi/harga/jarak/URL/fasilitas yang tidak ada di evidence.

## Next Step

Tahap berikutnya setelah guard stabil adalah membuat pipeline enrichment media dari raw Apify/Google Maps ke curated dataset dengan audit matching nama/place id. LLM tetap explanation layer dulu, belum re-ranker.
