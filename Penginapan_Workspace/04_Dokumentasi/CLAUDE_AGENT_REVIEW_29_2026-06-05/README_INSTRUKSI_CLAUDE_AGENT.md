# Instruksi Claude Agent - Review 29 Parent/Child Penginapan

Folder ini berisi paket kecil untuk mengecek 29 data penginapan yang masih perlu keputusan parent/child.

## File Utama

| File | Isi |
|---|---|
| `PENGINAPAN_CLAUDE_REVIEW_29_PARENT_CHILD_DECISION_2026-06-05.csv` | Gabungan 29 data yang perlu dicek |
| `PENGINAPAN_REVIEW_20_ACCEPTED_BY_RULE_CANDIDATE_2026-06-05.csv` | 20 kandidat child-parent dari aturan sistem |
| `PENGINAPAN_REVIEW_9_MANUAL_CHECK_2026-06-05.csv` | 9 data yang perlu cek manual lebih hati-hati |
| `PROMPT_UNTUK_CLAUDE_AGENT.md` | Instruksi siap pakai untuk Claude |

## Tujuan

Tentukan apakah setiap `name` adalah child/detail dari `parent_candidate_name`, atau sebenarnya properti mandiri.

## Pilihan Keputusan

| Keputusan | Pakai Jika |
|---|---|
| `accept_as_child` | Nama adalah kamar/unit/detail dari parent kandidat |
| `accept_as_parent` | Nama adalah properti mandiri dan layak jadi target scraping |
| `hold_low_priority` | Masih ragu atau tidak penting untuk jalur utama |
| `needs_more_check` | Bukti belum cukup, perlu cek lanjutan |

## Cara Cek

1. Buka CSV gabungan 29 data.
2. Cek kolom `name`, `parent_candidate_name`, `parent_candidate_distance_km`, dan `parent_candidate_score`.
3. Search Google Maps/Web dengan nama child dan parent.
4. Catat keputusan di `claude_decision`.
5. Isi `claude_evidence_url` dengan URL bukti yang dipakai.
6. Isi `claude_reason` singkat, maksimal 1-2 kalimat.

## Ringkasan Data

| Kelompok | Jumlah |
|---|---:|
| 20 kandidat child-parent | 20 |
| 9 manual check | 9 |
| Total | 29 |

## Catatan

Jangan menghapus data. Kalau tidak yakin, gunakan `hold_low_priority` atau `needs_more_check`.
