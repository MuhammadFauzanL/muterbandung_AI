# Format Notebook Audit Bertahap

Dokumen ini menjadi standar penulisan notebook untuk proses data engineering di project MuterBandung.ai, terutama pada dataset penginapan.

Nama singkat format ini:

**Notebook Audit Bertahap**

Kalimat instruksi pendek yang bisa dipakai:

> Kerjakan dengan Format Notebook Audit Bertahap: setiap code cell harus punya output yang jelas, lalu langsung diikuti markdown keputusan berdasarkan output itu.

## Prinsip Utama

Notebook tidak hanya dipakai untuk menjalankan script. Notebook harus menunjukkan proses berpikir data engineer:

1. Kenapa pengecekan dilakukan.
2. Data apa yang keluar dari code.
3. Keputusan apa yang diambil dari output tersebut.
4. Langkah berikutnya apa.

Markdown keputusan tidak boleh mengarang di luar hasil code. Kalau angka atau tabel tidak keluar dari cell sebelumnya, jangan dijadikan dasar keputusan.

## Pola Cell

| Urutan | Jenis Cell | Isi |
|---:|---|---|
| 1 | Markdown | Tujuan kecil tahap ini |
| 2 | Code | Jalankan pengecekan atau proses kecil |
| 3 | Output | Angka, tabel, atau ringkasan yang mudah dibaca |
| 4 | Markdown | Keputusan pendek berdasarkan output |
| 5 | Code berikutnya | Lanjut berdasarkan keputusan sebelumnya |

## Aturan Penulisan Markdown

| Bagian | Aturan |
|---|---|
| Tujuan | Tulis singkat, cukup 1-3 kalimat |
| Keputusan | Harus berdasarkan output cell sebelumnya |
| Bahasa | Natural, jelas, tidak terlalu panjang |
| Nada | Seperti catatan kerja data engineer, bukan laporan AI |
| Klaim | Jangan membuat klaim yang tidak muncul dari output |

## Aturan Penulisan Code Cell

| Bagian | Aturan |
|---|---|
| Scope | Satu code cell hanya mengerjakan satu tujuan kecil |
| Output | Wajib menampilkan hasil yang bisa dibaca |
| Tabel | Tampilkan sample secukupnya, tidak perlu semua baris |
| Variabel | Gunakan nama yang jelas |
| File output | Kalau membuat file, tampilkan path dan jumlah row |

## Format Keputusan

Gunakan format pendek seperti ini:

```markdown
**Keputusan**

Output menunjukkan ada 300 target yang terlihat sebagai kamar/unit. Data ini tidak masuk target scraping review utama dan ditahan sebagai child/detail listing.
```

Atau:

```markdown
**Keputusan**

87 data masih abu-abu. Data ini belum diputuskan sebagai parent atau child, sehingga masuk antrian review ringan.
```

## Contoh Struktur Tahap

| Cell | Jenis | Isi |
|---:|---|---|
| 1 | Markdown | Tujuan: cek target review yang masih terlihat seperti detail kamar/unit |
| 2 | Code | Hitung jumlah target berdasarkan `flag_group` |
| 3 | Markdown | Keputusan dari jumlah tiap kelompok |
| 4 | Code | Pisahkan target menjadi `ready`, `held_child`, dan `needs_review` |
| 5 | Markdown | Keputusan hasil split awal |
| 6 | Code | Audit `needs_review` dengan nama, koordinat, dan kandidat parent |
| 7 | Markdown | Keputusan sementara untuk data abu-abu |

## Contoh Untuk Penginapan

| Kelompok | Keputusan Awal |
|---|---|
| `hold_room_label` | Tahan sebagai child/detail kamar |
| `hold_unit_or_bedroom_listing` | Tahan sebagai child/unit listing |
| `review_villa_or_house_unit` | Audit lagi, karena bisa parent atau child |
| `review_other_detail_name` | Review ringan, jangan langsung parent |

## Output Yang Diharapkan

Jika tahap memisahkan target review dijalankan, output minimal yang perlu dibuat:

| File | Isi |
|---|---|
| `PENGINAPAN_REVIEW_TARGETS_READY_YYYY-MM-DD.csv` | Target parent yang aman untuk scraping review |
| `PENGINAPAN_REVIEW_TARGETS_HELD_CHILD_YYYY-MM-DD.csv` | Kamar/unit/detail listing yang ditahan |
| `PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_YYYY-MM-DD.csv` | Data abu-abu yang perlu review ringan |

## Checklist Sebelum Tahap Selesai

| Cek | Status |
|---|---|
| Setiap code cell punya output | Wajib |
| Setiap output penting punya markdown keputusan | Wajib |
| Keputusan tidak keluar dari data output | Wajib |
| File output mencantumkan jumlah row | Wajib |
| Data abu-abu tidak dipaksa masuk parent | Wajib |
| Child/detail tidak dihapus dari dataset | Wajib |

## Catatan

Format ini dipakai agar notebook mudah diaudit ulang. Kalau nanti ada keputusan yang salah, sumber masalahnya bisa dilacak dari cell mana output dan keputusan itu muncul.
