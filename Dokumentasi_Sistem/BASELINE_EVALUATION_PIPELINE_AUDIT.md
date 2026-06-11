# Audit Baseline Evaluation Pipeline MuterBandung

Tanggal audit: 2026-05-24

## Executive Verdict

Status: **PASSED WITH CONTROLLED RISKS**

Pipeline evaluasi baseline MuterBandung sudah layak dipakai sebagai fondasi sebelum integrasi LLM. QC operasional, ground truth, evaluator formal, report JSON/Markdown, dan notebook audit sudah tersedia serta dapat dijalankan ulang.

Catatan tegas: status ini bukan berarti seluruh sistem wisata sudah final secara data real-world. Status ini berarti **alat ukur deterministic baseline sudah sehat**. Risiko berikutnya berada pada data verified, lineage sentiment, dan guardrail LLM.

## Scope Audit

Artefak yang diaudit:

- `scratch_qc.py`
- `Dataset/3_Curated/groundtruth_queries.csv`
- `Scripts/evaluate_groundtruth.py`
- `qc_report.md`
- `groundtruth_eval_report.md`
- `groundtruth_eval_results.json`
- `Notebooks/wisata_training.ipynb`

## Evidence Summary

### 1. Artefak Evaluasi

Semua artefak utama tersedia.

| Artefak | Status | Catatan |
|---|---|---|
| `scratch_qc.py` | PASS | Memiliki API preflight dan tidak menimpa report saat API down |
| `groundtruth_queries.csv` | PASS | 62 kasus, schema konsisten, ID unik |
| `evaluate_groundtruth.py` | PASS | Membaca ground truth dan menghasilkan report Markdown + JSON |
| `qc_report.md` | PASS | Baseline QC terbaru tersimpan |
| `groundtruth_eval_report.md` | PASS | Evaluasi formal terbaru tersimpan |
| `groundtruth_eval_results.json` | PASS | Output machine-readable tersedia |
| `wisata_training.ipynb` | PASS | Notebook audit valid, 14 cell, mencatat proses evaluasi |

### 2. Validasi Ground Truth

Hasil validasi:

```text
Rows: 62
Unique IDs: 62
Blank IDs: 0
Blank queries: 0
Bad boolean values: 0
Bad min result values: 0
Blank notes: 0
Header columns: 22
Bad column lines: 0
No-strong-match cases: 12
Landmark rows: 3
Flag expectation rows: 4
Price expectation rows: 6
Shopping subtype rows: 4
```

Coverage skenario:

| Scenario | Cases |
|---|---:|
| Attribute Filters | 11 |
| Culinary / Cafe / Hangout | 6 |
| Culture / History / Education | 5 |
| Family / Children | 5 |
| Location / Distance | 9 |
| Nature / Healing | 5 |
| Negative Tests | 6 |
| Night / Budget | 6 |
| Shopping | 3 |
| Specific Guard Tests | 6 |

### 3. QC Operasional

Command:

```powershell
python -B .\scratch_qc.py
```

Hasil:

```text
Total queries tested: 62
Passed: 62
Failed: 0
Errors: 0
Needs review: 0
Final status: PASSED WITH NOTES
```

### 4. Ground Truth Evaluator

Command:

```powershell
python -B .\Scripts\evaluate_groundtruth.py
```

Hasil:

```text
Total cases: 62
Passed: 62
Failed: 0
Errors: 0
Pass rate: 100.0%
```

Evaluator mengecek:

- expected intent
- minimum result count
- `no_strong_match`
- required/forbidden category
- required/forbidden label
- landmark detection
- distance metadata
- verified coordinates
- shopping subtype
- real-world flags
- crowd level
- price expectation

### 5. Failure Mode / Preflight

Skenario uji:

```powershell
MUTERBANDUNG_API_URL=http://127.0.0.1:5999/api/recommend
```

Hasil:

```text
scratch_qc.py exit code: 2
evaluate_groundtruth.py exit code: 2
qc_report.md unchanged: True
groundtruth_eval_report.md unchanged: True
groundtruth_eval_results.json unchanged: True
```

Kesimpulan: report baseline tidak rusak saat API tidak tersedia.

## Findings

### Finding 1 - Evaluation Foundation Is Stable

Severity: Low

QC dan evaluator formal sama-sama berjalan dengan hasil 62/62 PASS. Ini cukup kuat untuk menjadi baseline deterministic sebelum eksperimen LLM.

### Finding 2 - Preflight Protection Works

Severity: Low

Kedua script berhenti sebelum menulis report jika API tidak tersedia. Ini mencegah baseline valid tertimpa error koneksi massal.

### Finding 3 - Ground Truth Already Useful, But Still Version 1

Severity: Medium

Ground truth saat ini sudah mencakup intent utama, guard negatif, lokasi, fasilitas, dan subtype. Namun ini masih baseline V1 dari 62 kasus. Untuk integrasi LLM, jumlah query sebaiknya dinaikkan bertahap ke 100-150 kasus dengan variasi bahasa natural yang lebih liar.

### Finding 4 - Data Verified Remains The Main Product Risk

Severity: High

Evaluator membuktikan logic baseline stabil, tetapi tidak menyelesaikan kekosongan data verified. Risiko utama berikutnya:

- `wheelchair_accessible_verified` masih minim/kosong
- `toilet_verified` masih minim/kosong
- `pet_friendly_verified` masih minim/kosong
- `parking_verified` sangat tipis
- factory outlet dan oleh-oleh belum cukup
- beberapa fasilitas masih perlu browser/manual verification

### Finding 5 - Sentiment Lineage Must Be Resolved Before Academic/Production Claim

Severity: High

Dokumentasi menyebut IndoBERT, tetapi histori pipeline menunjukkan kemungkinan ada TF-IDF + LinearSVC pada proses labeling sentiment. Sebelum klaim akademik atau production-grade AI, sumber sentiment aktif harus diluruskan:

- model source
- model version
- confidence
- tanggal training/inference
- file output yang dipakai recommender

## Residual Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Ground truth masih 62 kasus | LLM bisa lolos pada kasus mudah saja | Tambah query menjadi 100-150 kasus |
| Data verified kosong/tipis | Rekomendasi fasilitas bisa terlalu konservatif atau kosong | Buat facility review queue dan browser/manual verification |
| Sentiment lineage ambigu | Laporan akademik/produk bisa tidak kuat | Audit pipeline sentiment dan tambahkan metadata model |
| Evaluator belum membandingkan mode LLM | Belum bisa menilai LLM improvement | Tambah evaluator mode deterministic vs LLM |
| Real-world data berubah | Jam buka/harga/status bisa berubah | Periodic manual/browser QA |

## Next Recommended Stage

Prioritas berikutnya:

1. Audit sentiment lineage secara tegas.
2. Audit data verified/facility coverage.
3. Tambahkan evaluator mode `deterministic` vs `deterministic + LLM`.
4. Tambahkan LLM guarded layer hanya setelah validator output siap.

## Audit Conclusion

Baseline evaluation pipeline **siap dipakai** untuk menjaga kualitas saat pengembangan berikutnya. Jangan langsung memberi LLM kontrol penuh. LLM harus masuk setelah data lineage dan verified data lebih kuat, dan output LLM wajib divalidasi backend.
