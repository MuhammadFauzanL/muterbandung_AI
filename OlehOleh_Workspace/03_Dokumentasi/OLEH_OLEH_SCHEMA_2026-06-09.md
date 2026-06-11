# Schema Dataset Oleh-Oleh MuterBandung

Dokumen ini menjadi aturan awal sebelum scraping oleh-oleh dilakukan. Tujuannya sederhana: data oleh-oleh jangan bercampur dengan wisata atau penginapan, dan setiap klaim tetap punya sumber.

## Posisi Entity

Oleh-oleh dipakai sebagai entity pendukung. Alur utama tetap wisata, lalu sistem bisa menawarkan toko oleh-oleh yang dekat, relevan dengan rute, atau cocok dengan kebutuhan user.

## Kolom Inti

| Kolom | Wajib | Isi |
|---|---:|---|
| `oleh_oleh_id` | Ya | ID unik, contoh `OO-001` |
| `name` | Ya | Nama toko/tempat |
| `entity_level` | Ya | `brand`, `branch`, `store`, `market`, atau `listing_unclear` |
| `subtype` | Ya | Mengacu ke taxonomy, contoh `brownies`, `snack_kering`, `souvenir_merch` |
| `parent_group` | Ya | Kelompok besar dari taxonomy |
| `main_products` | Ya | Produk utama, dipisah dengan titik koma |
| `latitude` | Ya | Koordinat latitude |
| `longitude` | Ya | Koordinat longitude |
| `rating` | Ya | Rating Google/Maps, 0 sampai 5 |
| `reviews` | Ya | Jumlah review numeric |
| `source_url` | Ya | URL sumber utama |
| `place_url` | Penting | URL Google Maps jika tersedia |
| `address` | Penting | Alamat lengkap atau ringkas |
| `region` | Penting | Kota/Kabupaten/area |
| `opening_hours` | Penting | Jam buka dalam teks atau struktur |
| `price_level` | Penting | `low`, `medium`, `high`, atau `unknown` |
| `primary_image_url` | Penting | URL gambar utama |

## Kolom AI Awal

Kolom ini boleh diisi dari rule/keyword dulu. Jangan dibuat seolah-olah hasil model berat.

| Kolom | Isi |
|---|---|
| `product_tags` | Tag produk dari nama, kategori, dan review |
| `travel_friendly` | `high`, `medium`, `low`, `unknown` |
| `gift_fit_family` | Cocok untuk keluarga |
| `gift_fit_office` | Cocok untuk kantor/teman kerja |
| `gift_fit_children` | Cocok untuk anak |
| `food_related` | `true/false` |
| `shelf_life_estimate` | `short`, `medium`, `long`, `unknown` |
| `queue_risk` | `low`, `medium`, `high`, `unknown` |
| `parking_risk` | `low`, `medium`, `high`, `unknown` |
| `data_confidence` | `low`, `medium`, `high` |

## Quality Flags

| Flag | Maksud |
|---|---|
| `is_oleh_oleh_candidate` | Tempat layak masuk kandidat oleh-oleh |
| `is_verified_oleh_oleh` | Sudah disetujui manual sebagai toko/tempat oleh-oleh |
| `has_valid_coordinate` | Koordinat ada dan masuk area Bandung Raya |
| `has_rating_reviews` | Rating dan jumlah review tersedia |
| `has_product_signal` | Nama/kategori/review menunjukkan produk oleh-oleh |
| `needs_manual_review` | Perlu dicek manusia |

## Aturan Awal

1. Rating, jumlah review, alamat, koordinat, dan URL tidak boleh diisi dari perkiraan.
2. Taxonomy boleh berbasis rule, tapi keputusan final subtype tetap bisa dikoreksi manual.
3. Mall umum jangan langsung dianggap oleh-oleh. Harus ada sinyal produk atau toko yang jelas.
4. Restoran biasa jangan masuk, kecuali punya produk yang memang bisa dibawa pulang.
5. Review comment dipakai setelah daftar tempat disetujui, bukan sebelum entitasnya jelas.

## Output Tahap Awal

| File | Fungsi |
|---|---|
| `OLEH_OLEH_TAXONOMY_2026-06-09.csv` | Daftar subtype dan aturan awal |
| `OLEH_OLEH_CANONICAL_CANDIDATE_YYYY-MM-DD.csv` | Dataset kandidat setelah scraping kecil dan cleaning |
| `OLEH_OLEH_REVIEW_TARGETS_READY_YYYY-MM-DD.csv` | Target review comment setelah kandidat disetujui |

## Keputusan Saat Ini

Tahap sekarang baru menyiapkan taxonomy dan schema. Belum ada scraping, belum ada model, dan belum ada klaim final tentang toko oleh-oleh mana yang paling baik.
