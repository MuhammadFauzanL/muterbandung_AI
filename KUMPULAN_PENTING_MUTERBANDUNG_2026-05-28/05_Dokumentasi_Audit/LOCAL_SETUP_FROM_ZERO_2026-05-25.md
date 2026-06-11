# Local Setup From Zero - 2026-05-25

Panduan ini membuat project MuterBandung/PIJAK bisa dijalankan ulang dari environment kosong.

## Prasyarat

- Python 3.13.x
- PowerShell
- Node.js hanya diperlukan untuk syntax check frontend
- Internet diperlukan pada instalasi pertama dan saat model embedding belum ada di cache lokal

## 1. Buat Virtual Environment

```powershell
cd "D:\File\file\Fauzan Lubada\PIJAK"
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Jika command `py -3.13` tidak tersedia, gunakan:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Buat Konfigurasi Lokal

```powershell
Copy-Item .env.example .env
```

Default `.env.example` menjalankan server di:

```text
http://127.0.0.1:5000
```

Jika ingin mode offline, isi `MUTERBANDUNG_MODEL_PATH` dengan folder snapshot model:

```text
MUTERBANDUNG_MODEL_PATH=C:\path\to\sentence-transformer-snapshot
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
```

Jika dibiarkan kosong, `sentence-transformers` akan memakai cache Hugging Face lokal atau mengunduh model saat pertama kali dijalankan.

## 3. Jalankan Server

```powershell
python .\Scripts\app.py
```

Buka:

```text
http://127.0.0.1:5000
```

Endpoint utama:

```text
POST http://127.0.0.1:5000/api/recommend
POST http://127.0.0.1:5000/api/llm/validate
```

## 4. Verifikasi Dasar

Jalankan syntax check:

```powershell
python -B -m py_compile .\Scripts\app.py .\Scripts\recommender.py .\Scripts\llm_evidence_pack.py .\Scripts\llm_guard.py
node --check .\Scripts\static\script.js
```

Jalankan unit test:

```powershell
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard Scripts.test_api_contract Scripts.test_api_schema_snapshot Scripts.test_data_validation Scripts.test_targeted_completion_queue
```

Dengan server masih menyala, jalankan evaluasi API:

```powershell
python -B .\Scripts\evaluate_groundtruth.py
python -B .\scratch_qc.py
```

Expected baseline audit terakhir:

- unit test: 42/42 pass
- groundtruth: 62/62 pass
- QC: 62/62 pass

Jalankan validasi dataset canonical:

```powershell
python -B .\Scripts\validate_curated_dataset.py
```

Expected baseline:

- data validation gate: `PASS_WITH_WARNINGS`
- blocking errors: `0`
- active candidates: `212`

Jalankan queue targeted completion:

```powershell
python -B .\Scripts\generate_targeted_completion_queue.py
```

Output utama:

- `Dataset/3_Curated/targeted_data_completion_queue.csv`
- `Dataset/3_Curated/targeted_data_completion_top50.csv`
- `Dokumentasi_Sistem/TARGETED_DATA_COMPLETION_PLAN_2026-05-25.md`

## 5. Dataset Canonical

Dataset rekomendasi aktif:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Groundtruth aktif:

```text
Dataset/3_Curated/groundtruth_queries.csv
```

## 6. Catatan P0 Berikutnya

Setup ini menyelesaikan dasar reproducibility dan API contract test baseline.

Pekerjaan berikutnya:

1. Jalankan LLM provider benchmark harness sebelum memilih provider final.
2. Restart server Flask setelah perubahan kode agar port aktif memakai versi terbaru.
3. Selesaikan warning data prioritas sebelum integrasi LLM yang lebih percaya diri.

Catatan verifikasi bersih:

- `.venv_clean_verify` sudah pernah dibuat untuk membuktikan `requirements.txt` dapat diinstall dari environment kosong.
- Hasilnya terdokumentasi di `Dokumentasi_Sistem/CLEAN_VENV_AND_API_SCHEMA_SNAPSHOT_2026-05-25.md`.
- LLM evidence caveat policy terbaru terdokumentasi di `Dokumentasi_Sistem/LLM_EVIDENCE_CAVEAT_POLICY_2026-05-25.md`.
- Sentiment adjustment policy terbaru terdokumentasi di `Dokumentasi_Sistem/SENTIMENT_ADJUSTMENT_POLICY_2026-05-26.md`.
