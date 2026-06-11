# LLM Prompt Guard And Output Validator Audit - 2026-05-25

## Verdict

```text
PASSED
```

Tahap ini menambahkan pagar LLM setelah evidence pack stabil. LLM tetap hanya explanation layer dan belum boleh re-rank.

## Scope

- Audit media/link pada dataset aktif dan raw data.
- Implementasi `llm_prompt_guard`.
- Implementasi validator output LLM.
- Integrasi API rekomendasi dan endpoint validator.
- Regression test terhadap groundtruth dan QC live.
- Dokumentasi ke `Notebooks/wisata_training.ipynb`.

## Media Audit

Dataset curated aktif:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
media/link columns: none
```

Raw data yang memiliki kandidat media/link:

```text
Dataset/dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv
columns: imageUrl, website, url

Dataset/1_Raw_Data/apify_jam_buka_semua_lokasi_raw.csv
columns include image/link/url candidates
```

Keputusan:

- URL gambar/link tidak dimunculkan sebagai fakta aktif sebelum masuk curated dataset.
- Evidence pack sekarang membawa `candidate.media`.
- Jika media belum tervalidasi, nilai yang keluar adalah:

```json
{
  "available": false,
  "image_url": "",
  "destination_url": "",
  "website": "",
  "source": "not_available_in_curated_dataset"
}
```

## Implementasi

File utama:

- `Scripts/llm_guard.py`
- `Scripts/llm_evidence_pack.py`
- `Scripts/recommender.py`
- `Scripts/app.py`
- `Scripts/evaluate_groundtruth.py`
- `scratch_qc.py`
- `Scripts/test_llm_guard.py`
- `Scripts/test_llm_evidence_pack.py`
- `Dokumentasi_Sistem/LLM_EVIDENCE_PACK_SPEC.md`
- `Notebooks/wisata_training.ipynb`

API:

```text
POST /api/recommend
-> llm_evidence_pack
-> llm_prompt_guard

POST /api/llm/validate
-> valid/errors/warnings/sanitized_output
```

Validator menolak:

- destinasi di luar `allowed_destination_ids`
- urutan yang mengubah ranking backend
- harga yang tidak sama dengan evidence
- jarak yang tidak sama dengan evidence
- URL gambar/link/website yang tidak ada di evidence
- field fasilitas bebas seperti `facilities`
- klaim fasilitas positif yang tidak sesuai `realworld_flags`

## Verification

Syntax check:

```text
ast_ok 6
```

Unit test:

```text
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
Ran 25 tests
OK
```

Flask test client:

```text
recommend_status 200
has_pack True
has_guard True
valid_status 200 True
bad_status 422 False
```

Live validator:

```text
valid output: 200 True
fake URL output: 422 False
fake facility claim: 422 False
```

Groundtruth live:

```text
Passed: 62
Failed: 0
Errors: 0
```

QC live:

```text
Passed: 62
Failed: 0
Errors: 0
```

Operational:

```text
Initial guard validation completed; later media enrichment restarted server.
```

## Follow-Up Status

Media enrichment yang sebelumnya menjadi tahap berikutnya sudah dikerjakan pada 2026-05-25.

Dokumen lanjutan:

```text
Dokumentasi_Sistem/MEDIA_ENRICHMENT_AUDIT_2026-05-25.md
```
