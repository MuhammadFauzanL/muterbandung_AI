# Catatan Keputusan Place Discovery Oleh-Oleh

Dokumen ini mencatat alasan kenapa tahap oleh-oleh dimulai dari pencarian tempat dulu, bukan langsung mengambil review komentar.

## Keputusan

Tahap awal menggunakan **Google Maps Search Scraper** untuk mencari daftar toko/tempat oleh-oleh.

Review komentar belum diambil pada tahap ini. Review baru diambil setelah tempatnya lolos sebagai kandidat oleh-oleh yang benar.

## Alasan

Kalau langsung scrape review dari kata kunci umum, hasilnya bisa tercampur dengan restoran, mall, cafe, atau tempat belanja umum. Untuk rekomendasi, yang paling penting dulu adalah memastikan entitas tempatnya benar.

## Data Yang Dicari Di Tahap Ini

| Data | Alasan |
|---|---|
| Nama tempat | Menentukan entity utama |
| Alamat | Membantu cek lokasi dan region |
| Koordinat | Dipakai untuk rekomendasi dekat wisata |
| Rating | Sinyal kualitas awal |
| Jumlah review | Mengukur confidence data |
| Kategori Google | Membantu label taxonomy |
| Google Maps URL / place URL | Dipakai untuk target review scraping berikutnya |
| Jam buka | Dipakai untuk filter buka sekarang |
| Website / phone | Sumber tambahan jika tersedia |

## Scope Awal

Untuk batch awal, fokus pada kategori yang paling jelas sebagai oleh-oleh:

| Prioritas | Kategori |
|---:|---|
| 1 | Brownies, kue, bolu |
| 2 | Snack kering dan makanan kemasan |
| 3 | Batagor, siomay, tahu susu |
| 4 | Pusat oleh-oleh multi produk |

Fashion, mall umum, dan pasar lokal belum menjadi fokus awal. Data jenis ini bisa masuk nanti kalau taxonomy dan aturan filternya sudah lebih kuat.

## Output Yang Diharapkan

Hasil tahap ini bukan dataset final, tetapi raw candidate. Setelah itu perlu dedupe, label taxonomy, dan review manual ringan sebelum masuk tahap review scraping.

Alur kerja:

`search scraper -> raw places -> dedupe -> taxonomy label -> manual approve -> review scraping`

## Status

Status saat ini: taxonomy dan schema sudah tersedia. Tahap berikutnya adalah membuat batch query kecil untuk place discovery.
