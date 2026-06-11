# Hotel Safe Phase Coverage Audit - 2026-06-02

Audit ini mengecek ulang seluruh CSV dan JSON hotel/penginapan di `Penginapan_Workspace` untuk menjawab apakah data sudah masuk fase aman walaupun belum menutup seluruh wilayah Bandung secara sempurna.

## Keputusan Audit

**Status: AMAN UNTUK RAW COVERAGE DAN LANJUT KE BUILD DATASET HOTEL.**

Data belum menutup semua wilayah secara sempurna, tetapi sudah cukup aman untuk kebutuhan MuterBandung sebagai fitur pendukung wisata, dengan syarat data JSON baru diproses dulu menjadi dataset training/canonical melalui flatten, dedupe, region validation, dan quality scoring.

## Skor Fase Aman

| Check | Status | Bukti |
|---|---|---|
| Raw data hotel total minimal 1000 unique | Lolos | 1385 unique ketat |
| Koordinat tersedia minimal 95% | Lolos | 1384/1385 unique punya koordinat |
| Kota Bandung kuat | Lolos | 715 unique rough area |
| KBB utara/Lembang-Parongpong-Cisarua aman | Lolos | 81 unique rough area |
| KBB tengah-barat/Padalarang-Ngamprah-Batujajar aman | Lolos | 142 unique rough area |
| KBB selatan/barat daya punya raw coverage | Lolos | 51 unique rough area |
| Rating/review tersedia cukup | Lolos | 902 rating, 871 review count |
| Curated/canonical sudah sinkron dengan raw baru | Belum | canonical lama 174 unique ketat, training lama 381 unique ketat |

Skor: **7/8**.

Artinya raw data sudah aman, tetapi dataset final/canonical belum aman karena belum memasukkan JSON baru.

## Inventaris Saat Ini

| Komponen | Jumlah |
|---|---:|
| Total JSON Google Hotels Search | 18 |
| JSON baru tanggal 2026-06-02 | 15 |
| Total record JSON | 2946 |
| Unique dari JSON | 1262 |
| Total record CSV entity hotel | 1500 |
| Unique gabungan CSV + JSON | 1385 |
| Net unique baru dari JSON 2026-06-02 | 386 |

## Coverage Rough Area

| Area rough | Unique | Status |
|---|---:|---|
| Kota Bandung / pusat-utara | 715 | Aman/kuat |
| Cimahi-Baros-Pasteur border | 316 | Aman/kuat |
| KBB tengah-barat | 142 | Aman/kuat |
| KBB utara Lembang-Parongpong-Cisarua | 81 | Aman/kuat |
| KBB selatan / barat daya | 51 | Cukup aman |
| Bandung Raya lain | 67 | Cadangan |
| Luar Bandung Raya rough | 10 | Perlu filter |
| Tanpa koordinat | 1 | Perlu cek |

## Status Query Baru

| Query area | Unique ketat dari batch baru | Status |
|---|---:|---|
| Cililin, Kabupaten Bandung Barat | 102 | Aman raw |
| Saguling, Kabupaten Bandung Barat | 21 | Minimum aman, banyak overlap |
| Cipongkor, Kabupaten Bandung Barat | 3 | Lemah, tapi sudah dicoba |
| Gununghalu, Kabupaten Bandung Barat | 71 | Aman raw |
| Rongga, Kabupaten Bandung Barat | 67 | Aman raw, perlu geofilter |
| Sindangkerta, Kabupaten Bandung Barat | 29 | Cukup aman |
| Padalarang, Kabupaten Bandung Barat | 4 | Lemah karena overlap |
| Ngamprah, Kabupaten Bandung Barat | 4 | Lemah karena overlap |
| Cipatat, Kabupaten Bandung Barat | 3 | Lemah karena overlap |
| Cipeundeuy, Kabupaten Bandung Barat | 53 | Aman raw |
| Cikalongwetan, Kabupaten Bandung Barat | 33 | Cukup aman |
| Pangalengan, Kabupaten Bandung | 65 | Aman raw |
| Pasirjambu, Kabupaten Bandung | 2 | Lemah, tapi ada data |

## Catatan Duplikasi

File berikut adalah duplikat penuh berdasarkan SHA256:

- `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200.json`
- `dataset_google-hotels-search-scraper_2026-06-02_06-11-36-200 (1).json`

Keduanya berisi query Pangalengan yang sama. Saat build dataset, salah satu harus diabaikan atau dedupe berdasarkan hash/property token.

## Area Yang Belum Perlu Dikejar Secara Agresif

Area berikut sudah cukup untuk fase raw coverage awal:

- Kota Bandung
- Cimahi/Baros/Pasteur
- Lembang/Parongpong/Cisarua
- Padalarang/Ngamprah/Batujajar secara koridor
- KBB selatan/barat daya secara raw coverage
- Pangalengan

## Area Yang Masih Kurang Jika Ingin Lebih Lengkap

Area berikut belum harus dikejar untuk fase aman, tetapi bagus jika ingin memperkuat coverage:

| Area | Alasan |
|---|---|
| Kertasari | Belum terlihat ada query/file khusus. |
| Pacet | Belum terlihat ada query/file khusus. |
| Rancabali | Belum terlihat ada query/file khusus, walaupun kemungkinan tertangkap dari Ciwidey/Pasirjambu/Pangalengan. |
| Pasirjambu | Ada, tapi hasil unik sangat kecil. |
| Cipongkor | Sudah dicoba, tetapi hasil baru kecil. |
| Cipatat | Sudah dicoba, tetapi hasil baru kecil. |

## Rekomendasi Langkah Berikutnya

Jangan scraping ulang dulu kecuali ingin mengejar kelengkapan maksimal. Untuk kondisi sekarang, langkah terbaik adalah:

1. Flatten seluruh JSON Google Hotels Search ke CSV raw gabungan.
2. Abaikan file JSON duplikat Pangalengan.
3. Dedupe berdasarkan property token, nama normalized, dan koordinat.
4. Tambahkan `region_validation_label`.
5. Tandai `outside_bandung_raya_rough` agar tidak masuk rekomendasi utama.
6. Tandai room-level listing agar tidak mengalahkan hotel/properti utama.
7. Build ulang dataset penginapan training/canonical candidate versi baru.

## Kesimpulan Final

Data hotel/penginapan saat ini **sudah masuk fase aman untuk pondasi raw dataset**. Tidak semua area harus disempurnakan sekarang. Yang lebih penting berikutnya adalah engineering data pipeline agar raw JSON baru masuk ke dataset final dengan dedupe, validasi wilayah, dan quality flag yang rapi.
