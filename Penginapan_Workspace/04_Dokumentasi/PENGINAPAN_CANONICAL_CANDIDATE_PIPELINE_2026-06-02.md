# Penginapan Canonical Candidate Pipeline - 2026-06-02

Tahap ini melakukan dedupe konservatif dan region validation awal untuk data penginapan.

## Output

- Deduped master: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_DEDUPED_MASTER_BANDUNG_RAYA_2026-06-02.csv`
- Canonical candidate: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv`
- Validation JSON: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\penginapan_canonical_candidate_validation_2026-06-02.json`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Raw master rows | 2840 |
| Existing canonical rows included | 181 |
| Pool rows | 3021 |
| Candidate rows after dedupe | 1656 |
| Dedupe removed rows | 1365 |
| Validation gate | PASS_WITH_WARNINGS |

## Property Type

| Property type | Jumlah |
|---|---:|
| apartment | 352 |
| guest_house | 152 |
| hotel | 487 |
| room_level_listing | 54 |
| vacation_rental | 269 |
| villa | 342 |

## Region Validation

| Region validation | Jumlah |
|---|---:|
| bandung_raya_valid | 1656 |

## Region Bucket

| Region bucket | Jumlah |
|---|---:|
| bandung_raya_other | 27 |
| cimahi_baros_pasteur | 443 |
| kabupaten_bandung | 2 |
| kbb_selatan_baratdaya | 28 |
| kbb_tengah_barat | 317 |
| kbb_utara_lembang_parongpong_cisarua | 34 |
| kota_bandung | 805 |

## Catatan Kejujuran

- Dedupe dibuat konservatif agar tidak salah menggabungkan villa/apartment/unit yang mirip namanya.
- Dataset ini bernama `PENGINAPAN`, bukan `HOTEL`, karena isinya mencakup hotel, villa, apartment, guest house, homestay, dan vacation rental.
- Region validation ini masih rough coordinate validation, bukan batas administratif presisi.
- Output ini masih `canonical candidate`, belum final production canonical.
