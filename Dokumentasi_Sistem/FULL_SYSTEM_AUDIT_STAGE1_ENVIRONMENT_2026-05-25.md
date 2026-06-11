# Full System Audit Stage 1 - Environment and Project Inventory

## Scope

Tahap 1 mengaudit struktur project, environment lokal, dependency, runtime server, ukuran artefak, dan risiko operasional awal. Tahap ini sengaja belum masuk detail dataset/recommender agar konteks tetap ringan.

## Inventory Summary

File yang dihitung mengecualikan `Scraping/venv`, `Codex_Backups`, `__pycache__`, dan `.playwright-mcp`.

```text
total_files: 349
```

Distribusi folder utama:

```text
Scripts: 107
Dataset: 71
Apify_Workspace: 45
Scraping: 38
root files: 31
Dokumentasi_Sistem: 17
Wisata-Extracted: 12
Notebooks: 9
Models: 7
logs: 4
MuterBandung_Colab_Package: 4
Tugas_Kuliah: 4
```

Distribusi ekstensi utama:

```text
.py: 122
.csv: 79
.md: 31
.json: 29
.sample: 14
.ipynb: 11
.txt: 11
.log: 9
.zip: 5
.xlsx: 5
```

## Runtime Environment

Environment aktif saat audit:

```text
Python: 3.13.2
Flask: 3.1.1
pandas: 2.3.3
numpy: 2.3.1
sentence-transformers: 5.2.0
torch: 2.9.1
transformers: 4.57.3
requests: 2.32.5
scikit-learn: 1.8.0
tensorflow: 2.20.0
tf-keras: 2.20.1
```

Tidak ditemukan file environment resmi di root project:

```text
requirements.txt
pyproject.toml
environment.yml
Pipfile
poetry.lock
uv.lock
```

## Runtime Server

Port aktif:

```text
0.0.0.0:5000 LISTENING PID 9936
```

Log `muterbandung_live_new.out.log` menunjukkan server berhasil memuat engine:

```text
MuterBandung Recommender loaded: 213 destinasi aktif dari 234 baris.
Database source: Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv
Landmark aliases loaded: 8
Mengisi 17 nilai avg_rating kosong dengan median: 4.53
Debug mode: off
```

Log error live lebih banyak berisi request sukses `POST /api/recommend 200`, bukan error fatal.

## Git and Versioning

Root project `PIJAK` bukan Git repository:

```text
fatal: not a git repository
```

Ada repository terpisah di `Scraping/.git`, tetapi itu bukan root project utama.

Risiko:

- perubahan sistem utama tidak terlacak rapi;
- sulit rollback saat eksperimen LLM;
- sulit membedakan file final, backup, dan artefak sementara;
- audit akademik/profesional lebih sulit dipertanggungjawabkan.

## Large Artifacts

Artefak terbesar:

```text
474.74 MB Models/MuterBandung-IndoBERT-Sentiment/model.safetensors
440.51 MB Models/MuterBandung-IndoBERT-Sentiment.zip
53.23 MB Dataset/Archives/MASTER_REVIEWS_ENRICHED_backup_preclean_20260521_105325.csv
32.87 MB Scraping/.git/objects/pack/...
30.02 MB Dataset/Archives/MASTER_REVIEWS_ENRICHED_backup_20260520_224122.csv
18.37 MB Dataset/MASTER_REVIEWS_LABELED.csv
16.09 MB Dataset/Archives/dataset_Google-Maps-Reviews-Scraper_2026-05-20_09-53-52-559 (1).csv
14.37 MB Dataset/1_Raw_Data/apify_reviews_tambahan_batch1.csv
14.18 MB Dataset/MASTER_REVIEWS_ENRICHED.csv
14.18 MB MuterBandung_Colab_Package/MASTER_REVIEWS_ENRICHED.csv
```

Risiko:

- jika project dijadikan Git repo langsung, file model dan archive besar akan membuat repo berat;
- perlu strategi `.gitignore`, Git LFS, atau folder artefak eksternal;
- backup dan dataset besar perlu dipisahkan dari source code.

## Backup State

Folder `Codex_Backups/` sudah ada dan `.gitignore` saat ini berisi:

```text
Codex_Backups/
```

Ini baik untuk mencegah backup Codex masuk repo. Namun backup masih berada di workspace project, sehingga sebaiknya nanti dipindahkan ke folder backup pribadi di luar project atau drive backup terpisah.

## Stage 1 Verdict

```text
PROJECT STRUCTURE: workable but crowded
RUNTIME SERVER: alive and usable
ENVIRONMENT REPRODUCIBILITY: weak
VERSION CONTROL: weak at root project
ARTIFACT MANAGEMENT: high risk if Git/deploy is introduced without cleanup
```

## Stage 1 Risks

### High

- Tidak ada `requirements.txt` atau lockfile environment.
- Root project belum menjadi Git repository.
- Model dan dataset besar bercampur dengan source code.

### Medium

- Server masih dijalankan sebagai Flask development server.
- Log runtime berada di root dan beberapa log lama masih bercampur.
- Backup Codex masih berada di folder project.

### Low

- `.gitignore` baru hanya melindungi `Codex_Backups/`, belum melindungi artefak umum seperti `__pycache__`, log, model besar, dan archive.

## Recommended Fixes Before LLM Work

1. Buat `requirements.txt` dari environment yang benar-benar dipakai.
2. Tambahkan `.env.example` untuk konfigurasi server, model path, API URL, dan LLM provider.
3. Rapikan `.gitignore` sebelum inisialisasi Git root.
4. Pisahkan artefak besar: model, archive, backup, dan raw dump dari source code.
5. Buat perintah standar:

```powershell
python -B .\Scripts\app.py
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
python -B .\Scripts\evaluate_groundtruth.py
python -B .\scratch_qc.py
```

## Next Stage

Tahap 2 harus fokus ke:

- raw/intermediate/curated dataset;
- field wajib untuk LLM evidence;
- data lineage;
- duplicate/missing/anomaly;
- status media, sentiment, coordinate, price, opening hours.
