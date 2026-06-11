# Full System Audit Master Index - 2026-05-25

Dokumen ini menjadi pintu masuk utama untuk membaca audit sistem MuterBandung/PIJAK sebelum implementasi LLM.

## Executive Verdict

CORE RECOMMENDER READINESS: STRONG PROTOTYPE

DATA READINESS FOR DETERMINISTIC RECOMMENDATION: STRONG

LLM READINESS FOR EXPLANATION/ITINERARY LAYER: CONDITIONAL YES

LLM READINESS FOR AUTONOMOUS CHATBOT/RERANKING: NO

PRODUCTION READINESS: NOT YET

## Audit Documents

| Stage | Focus | File | Main Conclusion |
| --- | --- | --- | --- |
| Foundation | Kesiapan pondasi sebelum LLM | `FOUNDATION_AUDIT_BEFORE_LLM_2026-05-25.md` | LLM boleh masuk hanya sebagai lapisan narasi berbasis evidence, bukan pengambil keputusan utama. |
| Stage 1 | Environment, struktur repo, runtime | `FULL_SYSTEM_AUDIT_STAGE1_ENVIRONMENT_2026-05-25.md` | Sistem hidup dan cukup rapi untuk riset, tetapi belum reproducible karena tidak ada environment spec dan root Git belum jelas. |
| Stage 2 | Data, curated dataset, media, verification | `FULL_SYSTEM_AUDIT_STAGE2_DATA_2026-05-25.md` | Dataset rekomendasi kuat, tetapi real-world verification dan media masih perlu dilengkapi untuk klaim yang aman. |
| Stage 3 | Backend/API/frontend surface | `FULL_SYSTEM_AUDIT_STAGE3_BACKEND_API_2026-05-25.md` | Arsitektur hybrid tepat, tetapi API contract perlu validasi formal sebelum dipakai LLM. |
| Stage 4 | Testing, LLM guard, notebook lineage | `FULL_SYSTEM_AUDIT_STAGE4_TESTING_LLM_GUARD_2026-05-25.md` | Guard dan evaluasi dasar kuat, tetapi belum ada real provider benchmark dan API edge tests. |
| Stage 5 | Final readiness, risk register, roadmap | `FULL_SYSTEM_AUDIT_STAGE5_FINAL_READINESS_2026-05-25.md` | Prioritas berikutnya adalah environment lock, API hardening, lalu LLM benchmark harness. |
| Stage 6 | Consolidation and execution readiness | `FULL_SYSTEM_AUDIT_STAGE6_CONSOLIDATION_2026-05-25.md` | Tidak ada kontradiksi kritis baru; keputusan teknis sudah cukup jelas untuk masuk fase hardening. |

## Canonical System State

1. Dataset aktif untuk rekomendasi:
   `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`

2. Backend utama:
   `Scripts/app.py`
   `Scripts/recommender.py`
   `Scripts/llm_evidence_pack.py`
   `Scripts/llm_guard.py`

3. Frontend utama:
   `Scripts/templates/index.html`
   `Scripts/static/script.js`
   `Scripts/static/style.css`

4. Evaluasi utama:
   `Scripts/evaluate_groundtruth.py`
   `scratch_qc.py`
   `Scripts/test_recommender.py`
   `Scripts/test_llm_evidence_pack.py`
   `Scripts/test_llm_guard.py`

5. Notebook paling canonical saat audit:
   `Notebooks/wisata_training.ipynb`

## Decision Rules For LLM

LLM boleh:

- Menulis ringkasan rekomendasi dari evidence pack.
- Membuat itinerary dari kandidat yang sudah dipilih backend.
- Menjelaskan trade-off antar destinasi.
- Menyebut caveat jika data sentiment, media, fasilitas, atau verifikasi belum tersedia.

LLM tidak boleh:

- Membuat destinasi baru.
- Mengubah ranking backend secara default.
- Mengarang harga, jarak, jam buka, fasilitas, rating, atau media.
- Menggabungkan data web baru ke ranking tanpa pipeline verifikasi.
- Mengklaim tempat sudah verified jika field verifikasi belum mendukung.

## Immediate Execution Order

1. Jalankan P0 backlog dari `FULL_SYSTEM_ACTION_BACKLOG_2026-05-25.md`.
2. Setelah P0 selesai, buat harness benchmark provider LLM.
3. Baru sesudah benchmark, pilih mode integrasi LLM pertama: itinerary/explanation endpoint.

