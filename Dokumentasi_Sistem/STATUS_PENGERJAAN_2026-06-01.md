# Status Pengerjaan Sistem - 2026-06-01

## Ringkasan

Status saat ini: pondasi data wisata dan hotel sudah masuk fase siap dipakai untuk pengembangan recommender/LLM, tetapi data hotel masih perlu completion untuk meningkatkan kualitas jawaban. Per 2026-06-02, proses wisata sudah dipisahkan ke `Wisata_Workspace` dan proses penginapan/hotel sudah dipisahkan ke `Penginapan_Workspace`.

## Wisata

- Workspace wisata: `Wisata_Workspace`
- Dataset utama: `Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
- Status: sudah menjadi dataset curated utama wisata.
- Batch manual lanjutan: `Wisata_Workspace/01_Dataset/3_Curated/manual_review_batch3_remaining_46_after_status_facility_2026-05-27.csv`
- Fokus sisa: koordinat, media, rating/sentiment, dan data yang masih perlu review manual.

## Hotel

- Workspace penginapan: `Penginapan_Workspace`
- Dataset canonical: `Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv`
- Total data: `181` baris.
- Total kolom: `76` kolom.
- Validation gate: `PASS_WITH_WARNINGS`.
- Error validasi: `0`.
- Warning validasi: `469`.

## Segment Hotel

| Segment | Jumlah |
| --- | ---: |
| `apartment` | 65 |
| `hotel` | 64 |
| `guest_house` | 36 |
| `villa` | 10 |
| `room_level_listing` | 5 |
| `vacation_rental` | 1 |

## Kesiapan Hotel

| Level | Jumlah |
| --- | ---: |
| `strong_core_ready` | 41 |
| `usable_without_price_required` | 83 |
| `minimal_usable` | 166 |

## Quality Flags Hotel

| Flag | Terisi |
| --- | ---: |
| `rating_available` | 128 |
| `price_available` | 89 |
| `amenities_available` | 121 |
| `image_available` | 180 |
| `description_available` | 24 |
| `source_link_available` | 94 |
| `reviews_breakdown_available` | 18 |

## Masalah Yang Masih Perlu Diperhatikan

| Kode | Jumlah | Dampak |
| --- | ---: | --- |
| `W_RATING_MISSING` | 53 | Tidak bisa diranking kuat berdasarkan rating. |
| `W_PRICE_MISSING` | 92 | Tidak boleh dipakai untuk klaim murah/mahal secara tegas. |
| `W_AMENITIES_MISSING` | 60 | LLM harus hati-hati saat menyebut fasilitas. |
| `W_DESCRIPTION_MISSING` | 157 | Penjelasan kaya masih lemah tanpa deskripsi. |
| `W_IMAGE_MISSING` | 1 | Tidak cocok untuk kartu visual utama. |
| `W_LOW_REVIEW_CONFIDENCE` | 106 | Perlu shrinkage dan wording yang konservatif. |

## Notebook

- Notebook utama: `Wisata_Workspace/02_Notebooks/wisata_training.ipynb`
- Status: sudah berisi bagian hotel canonical pipeline.
- Jumlah cell notebook: `37`.
- Jumlah cell khusus hotel: `4`.
- Notebook khusus penginapan: `Penginapan_Workspace/03_Notebooks/penginapan_training.ipynb`

## Kesimpulan

Pondasi data sudah cukup untuk mulai masuk ke layer rekomendasi awal, tetapi belum ideal untuk jawaban LLM yang sangat kaya. Untuk menjaga output LLM tetap aman, sistem harus membaca quality flags dan confidence label sebelum membuat klaim.

## Prioritas Berikutnya

1. Buat `hotel_recommendation_ready.csv` dari canonical hotel dengan filter confidence dan quality flags.
2. Buat data dictionary final agar setiap kolom punya fungsi yang jelas untuk LLM dan recommender.
3. Tambahkan guardrail retrieval: data tanpa harga tidak boleh menjawab klaim harga, data tanpa amenities tidak boleh menjawab klaim fasilitas.
4. Buat batch completion hotel untuk `price`, `description`, `amenities`, dan `rating/review`.
5. Setelah itu baru integrasikan hotel ke API/recommender bersama wisata.
