# Hotel Coverage Audit After KBB Weak-Area Batch - 2026-06-02

Audit ini membaca seluruh dataset hotel/penginapan di `Penginapan_Workspace`, terutama JSON Google Hotels Search baru tanggal 2026-06-02 yang sudah berjalan sampai Batujajar.

## Kesimpulan Singkat

Scraping tambahan sudah sangat membantu. Dengan dedupe nama ketat, dataset bertambah sekitar 256 entitas penginapan unik baru dari batch 2026-06-02. Area P0 sudah memiliki raw data, dan P1 sudah berjalan sampai Batujajar. Namun hasil beberapa area masih banyak overlap, terutama sekitar Kota Baru Parahyangan, Padalarang, Baros/Cimahi, dan Ciwidey. Karena itu hasil ini belum boleh langsung dianggap valid per kecamatan tanpa geofilter/region validation.

## Status File Baru

| File | Query area | Unique ketat | Incremental baru | Duplikat ke data sebelumnya | Rating tersedia | Catatan |
|---|---|---:|---:|---:|---:|---|
| `dataset_google-hotels-search-scraper_2026-06-02_04-27-50-180.json` | Cililin, KBB | 102 | 85 | 17 | 20 | Bagus sebagai batch awal, tetapi banyak hasil KBP/Cimahi/Baros. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-35-05-199.json` | Saguling, KBB | 60 | 18 | 42 | 25 | Banyak overlap dengan Cililin/KBP. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-42-37-525.json` | Cipongkor, KBB | 60 | 3 | 57 | 25 | Hampir seluruhnya overlap. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-45-15-161.json` | Gununghalu, KBB | 73 | 59 | 14 | 19 | Banyak mengarah ke Ciwidey/Rancabali, tetap berguna untuk Bandung selatan. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-47-56-242.json` | Rongga, KBB | 141 | 68 | 73 | 33 | Tambahan besar, tetapi ada sebagian yang melebar keluar Bandung Raya. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-53-48-525.json` | Sindangkerta, KBB | 78 | 18 | 60 | 29 | Banyak overlap dengan Ciwidey/Rancabali. |
| `dataset_google-hotels-search-scraper_2026-06-02_04-57-17-734.json` | Padalarang, KBB | 60 | 1 | 59 | 26 | Raw tersedia, tetapi incremental kecil karena overlap dengan KBP sebelumnya. |
| `dataset_google-hotels-search-scraper_2026-06-02_05-03-29-424.json` | Ngamprah, KBB | 9 | 4 | 5 | 4 | Hasil kecil, tapi relevan untuk Padalarang/KBP. |
| `dataset_google-hotels-search-scraper_2026-06-02_05-05-45-170.json` | Batujajar, KBB | 18 | 0 | 18 | 5 | Sudah discrape, tetapi semua hasil overlap dengan run sebelumnya. |

## Agregat Saat Ini

| Metrik | Nilai |
|---|---:|
| Unique baseline sebelum batch baru | 1003 |
| Unique setelah batch baru | 1259 |
| Net unique baru dari batch 2026-06-02 | 256 |
| File baru yang diaudit | 9 |
| Area P0 selesai raw scrape | 6/6 |
| Area P1 sampai Batujajar selesai raw scrape | 3/6 |

## Status Area Lemah

| Area | Status saat ini | Rekomendasi |
|---|---|---|
| Cililin | Raw tersedia, tambahan besar | Masuk proses dedupe + geofilter. |
| Saguling | Raw tersedia, overlap tinggi | Tetap simpan, tapi validasi koordinat. |
| Cipongkor | Raw tersedia, incremental sangat kecil | Jangan ulang dulu; lanjut area lain. |
| Gununghalu | Raw tersedia, tambahan cukup besar | Perlu cek karena banyak hasil Ciwidey/Rancabali. |
| Rongga | Raw tersedia, tambahan besar | Perlu geofilter karena ada hasil luar Bandung Raya. |
| Sindangkerta | Raw tersedia, overlap tinggi | Tetap simpan untuk Bandung selatan/KBB selatan. |
| Padalarang | Raw tersedia, incremental sangat kecil | Jangan ulang dulu. |
| Ngamprah | Raw tersedia, jumlah kecil | Aman, tapi tidak perlu ulang segera. |
| Batujajar | Raw tersedia, incremental 0 | Jangan ulang dulu. |
| Cipatat | Belum discrape | Lanjut berikutnya. |
| Cipeundeuy | Belum discrape | Lanjut berikutnya. |
| Cikalongwetan | Belum discrape | Lanjut berikutnya. |
| Pangalengan | Belum discrape batch baru | Lanjut setelah KBB P1 selesai. |
| Kertasari | Belum discrape | Lanjut setelah Pangalengan. |
| Pacet | Belum discrape | Lanjut setelah Kertasari. |
| Rancabali | Belum discrape batch baru | Lanjut bila ingin memperkuat Ciwidey-Rancabali. |
| Pasirjambu | Belum discrape batch baru | Lanjut bila ingin memperkuat Ciwidey-Gambung. |

## Catatan Kualitas

- Semua unique record baru memiliki koordinat.
- Tidak semua record punya rating dan review count; dari batch baru, rating/reviews hanya tersedia pada sebagian data.
- `vacation_rentals: true` berhasil menangkap villa, homestay, dan rumah sewa, tetapi juga membuat hasil lebih banyak room-level listing.
- Area kecil di KBB sering menghasilkan overlap ke Kota Baru Parahyangan, Padalarang, Cimahi/Baros, dan Ciwidey.
- Sebelum masuk canonical hotel dataset, perlu proses:
  1. flatten JSON ke CSV,
  2. dedupe property token/nama/koordinat,
  3. region validation berbasis koordinat,
  4. flag room-level listing,
  5. hitung quality score.

## Rekomendasi Langkah Berikutnya

Jangan ulang query sampai Batujajar dulu. Lanjutkan area P1 yang belum berjalan:

1. Cipatat
2. Cipeundeuy
3. Cikalongwetan

Setelah itu lanjut P2 untuk area wisata Bandung selatan:

1. Pangalengan
2. Kertasari
3. Pacet
4. Rancabali
5. Pasirjambu

Setelah semua output masuk, baru jalankan build dataset training/canonical hotel dari seluruh JSON baru.
