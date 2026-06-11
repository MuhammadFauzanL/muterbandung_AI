# Cleanup Unused Files - 2026-05-28

## Ringkasan

Pembersihan dilakukan untuk merapikan root workspace setelah folder pengumpulan `KUMPULAN_PENTING_MUTERBANDUNG_2026-05-28` dibuat.

File asli penting untuk pengumpulan sudah disalin ke folder pengumpulan sebelum cleanup. Dataset utama, scripts inti, notebooks, dokumentasi sistem, model, dan folder data utama tidak dihapus.

## Dihapus

- Root log/runtime files: `server_*.log`, `muterbandung_*.log`, `test_start.*`.
- Folder runtime/cache lokal: `.playwright-mcp`, `logs`, `__pycache__`, `Scripts/__pycache__`.
- Root output sementara: `groundtruth_eval_*`, `qc_report.md`, screenshot evaluasi/media enrichment.
- Root dokumen/CSV duplikat yang sudah tersimpan di folder pengumpulan.
- Scratch/temporary files: `scratch_qc.py`, `skill.md`, `skill(1).md`.
- Backup dataset lama di `Dataset/3_Curated/*.bak_*`.
- Preview dataset sementara: `DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_PREVIEW.csv`.

Total item yang dihapus: `52`.

## Tetap Dipertahankan

- `Dataset/`
- `Scripts/`
- `Notebooks/`
- `Dokumentasi_Sistem/`
- `Models/`
- `KUMPULAN_PENTING_MUTERBANDUNG_2026-05-28/`
- `.venv_clean_verify/`
- `Codex_Backups/`
- `Apify_Workspace/`
- `Scraping/`
- `Wisata-Extracted/`
- `MuterBandung_Colab_Package/`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `readme.md`
- `ARCHITECTURE.md`

## Validasi Setelah Cleanup

Dataset validation tetap berhasil:

```text
Gate: PASS_WITH_WARNINGS
Rows: 234
Active candidates: 209
Errors: 0
Warnings: 375
```

Cleanup ini tidak mengubah dataset utama atau logic aplikasi.
