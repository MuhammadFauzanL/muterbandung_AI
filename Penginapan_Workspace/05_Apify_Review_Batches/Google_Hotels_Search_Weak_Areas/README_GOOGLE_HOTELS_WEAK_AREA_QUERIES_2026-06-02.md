# Google Hotels Search - Weak Area Queries

File utama:

`google_hotels_search_weak_area_queries_2026-06-02.json`

Gunakan untuk menutup coverage penginapan Bandung Raya yang masih lemah.

## Urutan Eksekusi

| Prioritas | Area | Alasan |
|---|---|---|
| P0 | Cililin, Saguling, Cipongkor, Gununghalu, Rongga, Sindangkerta | KBB selatan/barat masih kosong atau sangat lemah. |
| P1 | Padalarang, Ngamprah, Batujajar, Cipatat, Cipeundeuy, Cikalongwetan | KBB tengah/barat masih lemah. |
| P2 | Pangalengan, Kertasari, Pacet, Rancabali, Pasirjambu | Kabupaten Bandung selatan perlu diperkuat untuk itinerary wisata alam. |

## Cara Pakai

1. Buka actor Apify `johnvc/google-hotels-search-scraper`.
2. Masuk ke tab input JSON.
3. Ambil salah satu object `input` dari file query.
4. Jalankan satu per satu, mulai dari `P0`.
5. Setelah selesai, simpan output JSON ke:

`Penginapan_Workspace/01_Raw_Data/google_hotels_search_json/`

## Contoh Query Pertama

```json
{
  "adults": 2,
  "check_in_date": "2026-07-02",
  "check_out_date": "2026-07-03",
  "children": 0,
  "currency": "IDR",
  "gl": "id",
  "hl": "id",
  "max_pages": 15,
  "q": "penginapan in Cililin, Kabupaten Bandung Barat, Jawa Barat",
  "vacation_rentals": true
}
```

## Catatan Aman

- Jangan mulai dari query luas seperti `hotels in West Bandung Regency` lagi, karena hasilnya cenderung didominasi Lembang, Pasteur, dan Kota Bandung.
- Untuk area kecil, `max_pages` 15 cukup aman sebagai batch awal.
- Untuk area wisata besar seperti Pangalengan, pakai `max_pages` 25.
- Setelah output masuk, jalankan proses konversi/dedupe sebelum masuk canonical hotel dataset.
