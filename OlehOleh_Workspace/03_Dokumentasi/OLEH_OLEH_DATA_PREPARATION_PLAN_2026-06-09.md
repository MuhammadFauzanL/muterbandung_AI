# Oleh-Oleh Data Preparation Plan 2026-06-09

## Keputusan Awal

Oleh-oleh diperlakukan sebagai entity pendukung MuterBandung, bukan bagian utama ranking wisata.

Perannya:

- Wisata: tujuan utama user.
- Penginapan: pendukung untuk menginap.
- Oleh-oleh: pendukung akhir perjalanan atau kebutuhan belanja khas.

Dengan pola ini, toko oleh-oleh tidak muncul saat user mencari wisata alam, tetapi bisa muncul saat user mencari oleh-oleh atau setelah itinerary wisata terbentuk.

## Prinsip Data

Mulai kecil dulu. Jangan langsung scrape banyak cabang.

Batch awal cukup 10-20 tempat yang jelas relevan, lalu diuji apakah hasil query masuk akal.

## Tahap A - Scope

Tentukan batas data oleh-oleh:

- Bakery/kue khas Bandung.
- Brownies/bolen/snack khas.
- Souvenir/kerajinan khas.
- Pusat oleh-oleh.

Yang belum perlu dimasukkan di batch awal:

- Restoran umum.
- Mall umum.
- Warung kecil tanpa identitas oleh-oleh kuat.

## Tahap B - Raw Search

Gunakan Google Maps Search Scraper untuk mencari daftar tempat.

Query awal:

- `oleh-oleh khas Bandung`
- `pusat oleh-oleh Bandung`
- `brownies Bandung`
- `toko kue khas Bandung`
- `souvenir khas Bandung`
- `oleh-oleh Lembang`

Output raw disimpan terpisah di workspace oleh-oleh.

## Tahap C - Cleaning dan Dedupe

Cek duplikasi cabang dan brand.

Aturan awal:

- Rekomendasi app memakai lokasi cabang.
- Analisis boleh punya `brand_name`.
- Cabang yang berbeda tetap boleh ada jika koordinatnya berbeda dan berguna untuk user.

## Tahap D - Canonical Candidate

Buat dataset kandidat dengan kolom minimal:

| Kolom | Isi |
|---|---|
| `entity_type` | `oleh_oleh` |
| `oleh_oleh_id` | ID unik |
| `name` | Nama cabang/tempat |
| `brand_name` | Nama brand jika ada |
| `subtype` | bakery, brownies, snack, souvenir, pusat_oleh_oleh |
| `latitude` | Koordinat |
| `longitude` | Koordinat |
| `rating` | Rating Google |
| `reviews` | Jumlah review |
| `opening_hours` | Jam buka |
| `product_tags` | Produk utama |
| `media_url` | Gambar |
| `source_url` | URL sumber |
| `data_quality_status` | ready, needs_review, hold |

## Tahap E - Review Scraping

Jangan scrape review semua dulu.

Ambil batch test kecil 10-20 tempat. Setelah hasilnya tepat, baru batch berikutnya.

Review nanti dipakai untuk sentiment/aspect:

- rasa
- harga
- pelayanan
- antrean
- kemasan
- cocok untuk oleh-oleh

## Tahap F - Integrasi Sistem

Oleh-oleh tidak masuk ranking wisata utama.

Muncul pada:

- query langsung: `oleh-oleh Bandung`
- query dekat lokasi: `oleh-oleh dekat Braga`
- itinerary akhir: rekomendasi belanja sebelum pulang

## Status

Plan dibuat. Belum ada scraping, cleaning, atau integrasi runtime.

Tahap berikutnya jika ingin lanjut: buat raw search query JSON untuk scraper batch kecil.
