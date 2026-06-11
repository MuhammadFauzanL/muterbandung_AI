# Sentiment Lineage Audit MuterBandung

Tanggal audit: 2026-05-24

## Executive Verdict

Status: **NEEDS CORRECTION BEFORE LLM / ACADEMIC CLAIM**

Skor sentiment yang aktif dipakai recommender saat ini **bukan terbukti berasal dari IndoBERT pada runtime maupun dari output IndoBERT yang tersambung ke database aktif**.

Berdasarkan code path yang ditemukan, sumber aktif `avg_sentimen_skor` adalah:

```text
Dataset/MASTER_REVIEWS_ENRICHED.csv
-> Scripts/run_nlp_pipeline_v2.py
-> TF-IDF + LinearSVC
-> Dataset/MASTER_REVIEWS_LABELED.csv
-> Dataset/SENTIMENT_SCORES_PER_LOKASI.csv
-> Scripts/run_fase7_multilabel.py
-> DATABASE_WISATA_FINAL_PARIPURNA.csv
-> Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
-> Scripts/recommender.py
```

Model IndoBERT memang ada sebagai artefak di `Models/MuterBandung-IndoBERT-Sentiment/`, tetapi audit kode belum menemukan bukti bahwa output model IndoBERT tersebut menulis kolom sentiment aktif yang dipakai recommender.

## Scope

Audit ini menelusuri:

- code path sentiment di runtime recommender
- dataset aktif yang dibaca recommender
- pipeline pembentuk `MASTER_REVIEWS_LABELED.csv`
- pipeline pembentuk `SENTIMENT_SCORES_PER_LOKASI.csv`
- keberadaan artefak model IndoBERT
- inkonsistensi label API/UI/dokumentasi

## Runtime Evidence

### 1. Dataset Aktif

`MuterBandungRecommender` menerima default `DATABASE_WISATA_FINAL_PARIPURNA.csv`, tetapi jika file reviewed tersedia, code mengarahkannya ke:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Evidence:

```text
Scripts/recommender.py
- membaca REVIEWED_DB_PATH
- load dataframe dari CSV
- tidak menjalankan model sentiment
```

### 2. Kolom Sentiment Yang Dipakai Ranking

Ranking mengambil langsung:

```python
sent_score = float(row['avg_sentimen_skor']) if pd.notna(row['avg_sentimen_skor']) else 0.0
```

Bobot sentiment:

```text
Query mode: 35%
No-query mode: 55%
```

Artinya lineage sentiment sangat penting karena memengaruhi ranking secara besar.

### 3. Nama Field API Saat Ini Misleading

Di `score_breakdown`, code mengirim:

```python
'sentimen_indobert': round(sent_score, 4)
```

Frontend membaca field yang sama untuk badge:

```javascript
bd.sentimen_indobert
```

Masalah: field ini bernama `sentimen_indobert`, tetapi nilai yang dikirim adalah `avg_sentimen_skor` dari CSV aktif, bukan hasil inference IndoBERT runtime.

## Data Evidence

### Dataset Sentiment

| File | Rows | Kolom Kunci |
|---|---:|---|
| `Dataset/MASTER_REVIEWS_ENRICHED.csv` | 34.150 | review bersih tanpa label sentiment |
| `Dataset/MASTER_REVIEWS_LABELED.csv` | 34.003 | `sentimen`, `sentimen_prediksi`, `sentimen_skor` |
| `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv` | 212 | `avg_sentimen_skor`, `sentimen_label_lokasi` |
| `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv` | 234 | database aktif reviewed |

Distribusi `MASTER_REVIEWS_LABELED.csv`:

```text
positif: 29.326
netral: 2.360
negatif: 2.317
```

Range skor:

```text
SENTIMENT_SCORES_PER_LOKASI avg_sentimen_skor: -0.3077 to 1.0
DATABASE_WISATA_LABELED_V2_REVIEWED avg_sentimen_skor: -0.3077 to 1.0
```

Konsistensi merge:

```text
Overlap DB reviewed vs SENTIMENT_SCORES_PER_LOKASI: 212 lokasi
Mismatch avg_sentimen_skor pada overlap: 0
DB rows tanpa match sentiment source: 22
Active rows: 213
Active rows dengan avg_sentimen_skor = 0: 17
Rows tanpa sentimen_label_lokasi: 22
```

## Pipeline Evidence

### Pipeline Aktif Yang Terbukti Menulis File Sentiment

`Scripts/run_nlp_pipeline_v2.py`:

- membaca `Dataset/MASTER_REVIEWS_ENRICHED.csv`
- membuat label ground truth dari rating
- memakai `TfidfVectorizer`
- melatih `LinearSVC`
- menulis:
  - `Dataset/MASTER_REVIEWS_LABELED.csv`
  - `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv`

`Scripts/run_fase7_multilabel.py`:

- membaca `Dataset/MASTER_REVIEWS_LABELED.csv`
- membaca `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv`
- merge ke database wisata
- menulis `DATABASE_WISATA_FINAL_PARIPURNA.csv`

### IndoBERT Artifact

Artefak ditemukan:

```text
Models/MuterBandung-IndoBERT-Sentiment/config.json
Models/MuterBandung-IndoBERT-Sentiment/model.safetensors
Models/MuterBandung-IndoBERT-Sentiment/tokenizer.json
Models/MuterBandung-IndoBERT-Sentiment/training_args.bin
```

Notebook/script terkait IndoBERT ditemukan:

```text
MuterBandung_Colab_Package/Train_IndoBERT_MuterBandung.ipynb
MuterBandung_Colab_Package/IndoBERT_Colab.ipynb
Notebooks/IndoBERT_Colab.ipynb
Scripts/create_colab_notebook.py
Scripts/benchmark_indobert.py
```

Namun audit belum menemukan file output IndoBERT yang tersambung ke database aktif, misalnya:

```text
INDOBERT_LABELED_RESULTS.csv
MASTER_REVIEWS_LABELED_INDOBERT.csv
SENTIMENT_SCORES_PER_LOKASI_INDOBERT.csv
```

## Findings

### Finding 1 - Active Sentiment Source Is TF-IDF + LinearSVC, Not Proven IndoBERT

Severity: **High**

Runtime recommender tidak memanggil IndoBERT. Dataset aktif mengambil `avg_sentimen_skor` dari CSV. CSV tersebut terbukti dibentuk oleh `run_nlp_pipeline_v2.py` memakai TF-IDF + LinearSVC.

Impact:

- Klaim "sentimen IndoBERT" pada API/UI/dokumentasi belum valid.
- Paper/laporan akademik bisa dianggap tidak konsisten.
- LLM evidence pack nanti akan membawa metadata sentiment yang salah jika tidak diperbaiki.

### Finding 2 - API Field `sentimen_indobert` Misleading

Severity: **High**

Field `score_breakdown.sentimen_indobert` sebenarnya berisi skor dari `avg_sentimen_skor`, bukan skor IndoBERT.

Recommended fix:

- Tambahkan field netral:
  - `sentiment_score`
  - `sentiment_model_source`
  - `sentiment_model_version`
- Jangan pakai `sentimen_indobert` sebagai field output aktif selama source aktif bukan IndoBERT.

### Finding 3 - Final Dataset Lacks Sentiment Provenance Columns

Severity: **High**

Dataset aktif tidak memiliki kolom:

```text
sentiment_model_source
sentiment_model_version
sentiment_confidence
sentiment_generated_at
sentiment_pipeline_file
```

Impact:

- Tidak bisa membuktikan asal skor per row.
- Sulit membandingkan SVM vs IndoBERT.
- Sulit membuat audit LLM evidence pack yang jujur.

### Finding 4 - Missing Sentiment Rows Are Penalized But Not Explicitly Marked

Severity: **Medium**

Ada 22 row database tanpa match sentiment source dan 17 active rows dengan `avg_sentimen_skor = 0`.

Status 2026-05-24: sudah dimitigasi dengan `sentiment_available`. Row tanpa data sentiment sekarang ditandai `False`, sedangkan score tetap 0 agar ranking lama tidak berubah.

Impact:

- Tempat tanpa data review bisa turun ranking tanpa penjelasan eksplisit.
- User/LLM tidak tahu apakah skor 0 berarti netral asli atau data kosong.

Recommended fix:

- Tambahkan `sentiment_available`
- Tambahkan `sentiment_missing_reason`
- Tampilkan warning internal untuk LLM/evaluator.

### Finding 5 - IndoBERT Config Artifact Needs Verification Before Use

Severity: **Medium**

`config.json` model IndoBERT menunjukkan arsitektur `BertForSequenceClassification`, tetapi metadata label masih generik `LABEL_0`, `LABEL_1`, `LABEL_2`. Ada juga `_num_labels: 5` sementara `id2label` berisi 3 label.

Impact:

- Sebelum IndoBERT dipakai ulang, mapping label harus divalidasi.
- Jangan langsung mengaktifkan model tanpa test inference dan label mapping.

## Recommended Remediation Plan

### Phase 1 - Honest Metadata Fix

Tanpa mengubah ranking dulu:

1. Tambahkan metadata sentiment ke response backend:
   - `sentiment_score`
   - `sentiment_model_source: "tfidf_linearsvc"`
   - `sentiment_model_version: "run_nlp_pipeline_v2"`
   - `sentiment_available`
2. Rename tampilan UI dari internal `sentimen_indobert` menjadi label netral `Sentimen`.
3. Dokumentasi harus menyebut: "sentiment aktif saat ini adalah SVM baseline, IndoBERT tersedia sebagai artefak training tetapi belum menjadi source aktif."

### Phase 2 - Dataset Provenance Columns

Tambahkan kolom ke dataset curated:

```text
sentiment_model_source
sentiment_model_version
sentiment_confidence
sentiment_generated_at
sentiment_available
sentiment_review_count
```

Untuk kondisi sekarang, isi awal:

```text
sentiment_model_source = tfidf_linearsvc
sentiment_model_version = run_nlp_pipeline_v2
sentiment_confidence = null atau berbasis review count
sentiment_available = total_ulasan > 0
```

### Phase 3 - IndoBERT Activation Only If Evidence Complete

Jika ingin benar-benar memakai IndoBERT:

1. Buat inference script yang memuat `Models/MuterBandung-IndoBERT-Sentiment`.
2. Validasi label mapping positif/netral/negatif.
3. Jalankan inference ke `MASTER_REVIEWS_ENRICHED.csv`.
4. Simpan output baru:
   - `MASTER_REVIEWS_LABELED_INDOBERT.csv`
   - `SENTIMENT_SCORES_PER_LOKASI_INDOBERT.csv`
5. Bandingkan dengan SVM memakai evaluator.
6. Baru putuskan apakah ranking memakai SVM, IndoBERT, atau ensemble.

## Code-Level Recommendation

Perubahan aman berikutnya:

```text
Scripts/recommender.py
- Tambahkan sentiment metadata ke score_breakdown
- Jangan lagi menyebut field baru sebagai indobert jika source aktif bukan IndoBERT
- Field lama `sentimen_indobert` tidak dipakai sebagai output aktif
```

```text
Scripts/static/script.js
- Gunakan bd.sentiment_score jika ada
- Label UI tetap "Sentimen", bukan "IndoBERT"
```

## Phase 1 Implementation Status - 2026-05-24

Status:

```text
IMPLEMENTED
```

Perubahan yang sudah diterapkan:

- `Scripts/recommender.py` mengirim field netral `sentiment_score`, `sentiment_model_source`, `sentiment_model_version`, dan `sentiment_available` pada `score_breakdown` dan item rekomendasi.
- `Scripts/static/script.js` membaca `bd.sentiment_score` dan tidak lagi membaca `bd.sentimen_indobert`.
- `Scripts/test_recommender.py` sekarang memastikan `sentimen_indobert` tidak muncul pada `score_breakdown`.
- Dataset berikut sudah memiliki metadata sentiment:
  - `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
  - `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2.csv`
  - `DATABASE_WISATA_FINAL_PARIPURNA.csv`
  - `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv`
- Pipeline pembentuk data sentiment (`run_nlp_pipeline_v2.py`, `run_fase5_sentiment.py`, dan `run_fase7_multilabel.py`) ikut disiapkan agar metadata tidak hilang saat regenerasi.

Catatan kontrol:

```text
Ranking tidak diubah.
sentiment_score tetap berasal dari avg_sentimen_skor.
Klaim IndoBERT belum diaktifkan sampai pipeline IndoBERT tersambung dan tervalidasi.
```

## Audit Conclusion

Code saat ini **berjalan dan baseline evaluator PASS**, dan metadata sentiment aktif sudah diluruskan. Klaim "IndoBERT aktif" tetap belum valid sampai pipeline IndoBERT benar-benar tersambung.

Verdict:

```text
Active sentiment source: TF-IDF + LinearSVC baseline
IndoBERT status: artifact/training asset, not proven as active scoring source
Runtime scoring impact: high, because sentiment weight is 35%
Action required before LLM: add provenance metadata and correct misleading API/UI naming
```
