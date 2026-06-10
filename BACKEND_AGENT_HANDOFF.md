# MuterBandung AI Backend Handoff

Tanggal: 2026-06-10

Dokumen ini untuk agent/backend developer yang akan melanjutkan integrasi AI recommender MuterBandung.

## Tujuan Repo

Repo ini berisi runtime AI recommender untuk:

| Entitas | Status | Catatan |
|---|---|---|
| Wisata | Siap dikembangkan | Dataset runtime sudah dipakai oleh recommender |
| Oleh-oleh | Baseline siap | Sudah punya scoring, harga manual, produk utama, dan query audit |
| Penginapan | Candidate | Data parent/child sudah rapi, sentiment masih dikerjakan terpisah |

Fokus backend saat ini: expose API, jaga ranking tetap di backend, dan jangan membuat klaim di luar data.

## File Utama

| File | Fungsi |
|---|---|
| `Scripts/app.py` | Flask API utama |
| `Scripts/recommender.py` | Ranking dan rekomendasi wisata |
| `Scripts/oleh_oleh_recommender.py` | Ranking dan rekomendasi oleh-oleh |
| `Scripts/llm_evidence_pack.py` | Evidence pack untuk penjelasan LLM |
| `Scripts/llm_guard.py` | Guard agar LLM tidak mengarang |
| `Scripts/templates/index.html` | UI dev sementara |
| `Scripts/static/script.js` | Frontend logic sementara |
| `Scripts/static/style.css` | Style UI sementara |

## Dataset Runtime

| Entitas | File |
|---|---|
| Wisata | `Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv` |
| Wisata validation | `Wisata_Workspace/01_Dataset/3_Curated/data_validation_runtime_candidate_2026-06-09.json` |
| Alias lokasi | `Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv` |
| Oleh-oleh | `OlehOleh_Workspace/03_Curated/OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_2026-06-10.csv` |
| Oleh-oleh summary | `OlehOleh_Workspace/03_Curated/OLEH_OLEH_BASELINE_UI_ENRICHED_WITH_MANUAL_PRODUCT_PRICE_SUMMARY_2026-06-10.json` |
| Penginapan parent | `Penginapan_Workspace/02_Curated/PENGINAPAN_PARENT_MASTER_2026-06-05.csv` |
| Penginapan child | `Penginapan_Workspace/02_Curated/PENGINAPAN_CHILD_LISTINGS_FINAL_2026-06-05.csv` |
| Relasi penginapan | `Penginapan_Workspace/02_Curated/PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv` |

## Endpoint Saat Ini

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/recommend` | POST | Rekomendasi wisata |
| `/api/oleh-oleh/recommend` | POST | Rekomendasi oleh-oleh |
| `/api/llm/validate` | POST | Validasi output LLM |

Contoh payload wisata:

```json
{
  "query": "wisata alam murah ramah anak",
  "top_n": 5
}
```

Contoh payload oleh-oleh:

```json
{
  "query": "snack murah tahan perjalanan",
  "top_n": 5
}
```

## Cara Jalan Lokal

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:HOST="127.0.0.1"
$env:PORT="5000"
python .\Scripts\app.py
```

Lalu buka:

```text
http://127.0.0.1:5000
```

## Validasi Cepat

```powershell
python -m py_compile .\Scripts\app.py .\Scripts\recommender.py .\Scripts\oleh_oleh_recommender.py .\Scripts\llm_evidence_pack.py .\Scripts\llm_guard.py
python .\Scripts\run_recommender_runtime_audit.py
python .\Scripts\audit_oleh_oleh_recommender_queries.py
```

## Aturan Penting

- Ranking jangan dihitung di frontend.
- Frontend hanya mengirim query dan menampilkan hasil dari API.
- LLM belum menjadi penentu ranking.
- Jika LLM dipasang, gunakan evidence pack dari backend.
- Jangan klaim fasilitas, harga, sentiment, atau status aktif kalau field datanya kosong.
- Penginapan belum final untuk ranking user-facing sampai sentiment hotel selesai.
- Raw scraper, log, venv, dan file besar tidak perlu masuk repo.

## Catatan Untuk Pengembangan Berikutnya

| Prioritas | Pekerjaan |
|---|---|
| 1 | Stabilkan API backend untuk wisata dan oleh-oleh |
| 2 | Buat endpoint penginapan sebagai candidate/stub dulu |
| 3 | Tambahkan penginapan ke ranking setelah sentiment selesai |
| 4 | Pasang LLM hanya sebagai layer penjelasan, bukan ranking utama |
| 5 | Tambahkan test kontrak API sebelum ubah response schema |

## Status Singkat

Wisata sudah paling matang. Oleh-oleh sudah baseline dan bisa dikembangkan. Penginapan sudah punya struktur data, tapi belum final untuk rekomendasi karena sentiment review masih menunggu hasil.
