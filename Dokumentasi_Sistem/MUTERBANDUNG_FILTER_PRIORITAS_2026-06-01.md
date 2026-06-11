# Muter Bandung - Prioritas Filter Website

Dokumen ini merangkum filter yang paling penting untuk user website Muter Bandung. Prinsip utamanya: user tidak boleh dipaksa membaca semua data teknis. Filter utama harus membantu user mengambil keputusan liburan dengan cepat, sedangkan filter teknis tetap tersedia di bagian lanjutan.

## Tujuan Website

Muter Bandung adalah website rekomendasi wisata Bandung Raya. Fokus utamanya adalah membantu user memilih tempat wisata berdasarkan gaya perjalanan, budget, waktu, lokasi, dan kebutuhan praktis. Hotel/penginapan berfungsi sebagai fitur pendukung setelah user memilih destinasi atau membuat itinerary.

## Prinsip UI Filter

| Prinsip | Keputusan UI | Alasan |
| --- | --- | --- |
| Jangan tampilkan semua filter sekaligus | Gunakan filter cepat + filter lanjutan | Terlalu banyak filter membuat user bingung. |
| Utamakan bahasa user | Gunakan istilah seperti `Keluarga`, `Healing`, `Gratis`, `Dekat Saya` | User tidak berpikir dalam nama kolom dataset. |
| Data confidence tetap dipakai, tapi tidak ditonjolkan | Confidence dipakai sistem untuk ranking, bukan filter utama user | User butuh hasil yang aman, bukan melihat semua audit flag. |
| Hotel menjadi fitur pendukung | Tampilkan hotel setelah user memilih wisata | Website tidak berubah menjadi marketplace hotel. |
| Filter yang rawan data kosong disembunyikan | Crowd level, confidence, dan detail verifikasi masuk advanced | Banyak data masih `unknown` atau belum lengkap. |

## Filter Yang Wajib Muncul Di Halaman Utama

| Prioritas | Filter | Bentuk UI | Data/Field | Fungsi Untuk User | Catatan |
| ---: | --- | --- | --- | --- | --- |
| 1 | Cari / Ceritakan Rencana | Search bar natural language | `query`, semantic recommender | User bisa mengetik bebas seperti "wisata alam murah buat keluarga" | Ini harus menjadi pintu utama AI recommender. |
| 2 | Gaya Liburan | Chip multi-select | `final_primary_intent`, `category`, `multi_labels` | Memilih tipe pengalaman wisata | Pilihan awal cukup 6 chip. |
| 3 | Budget | Segmented control | `price_min`, `price_max`, `price_type` | Menyaring gratis atau batas harga | Jangan pakai input angka sebagai default. |
| 4 | Buka Sekarang | Toggle | `jam_buka`, `jam_tutup`, weekday/weekend | Menampilkan tempat yang relevan dengan waktu user | Bisa dipadukan dengan waktu rencana. |
| 5 | Dekat Saya | Button + radius chip | `latitude`, `longitude`, distance calculation | Rekomendasi berdasarkan posisi user | Radius cukup 5, 10, 25 km. |
| 6 | Ramah Anak | Toggle/chip | `child_friendly_verified`, labels | Penting untuk keluarga | Sangat bernilai untuk decision making. |
| 7 | Butuh Penginapan | Toggle | Hotel canonical dataset + distance | Memunculkan hotel terdekat setelah wisata dipilih | Jangan langsung buka semua filter hotel. |

## Chip Gaya Liburan Yang Disarankan

| Chip | Mapping Data | Kenapa Penting |
| --- | --- | --- |
| Alam | `Alam`, `Wisata Alam` | Kategori terbesar dan paling sering dicari. |
| Keluarga | `Keluarga`, `Ramah Anak`, `Rekreasi Keluarga` | Cocok untuk mayoritas user. |
| Edukasi | `Edukasi`, `Tempat Belajar` | Penting untuk anak/sekolah/keluarga. |
| Kuliner | `Kuliner`, `Tempat Kuliner` | User sering mencari makan/nongkrong. |
| Healing | `Santai/Healing`, alam santai | Bahasa yang natural bagi user. |
| Malam | `night_verified`, `open_24h_verified`, intent malam | Membantu user yang pergi sore/malam. |

## Budget Filter Yang Disarankan

| Label UI | Logika Data | Kenapa Lebih Baik |
| --- | --- | --- |
| Gratis | `price_type == Gratis` atau `price_max == 0` | Mudah dipahami. |
| < Rp50.000 | `price_max <= 50000` | Cocok untuk wisata murah. |
| < Rp100.000 | `price_max <= 100000` | Batas umum untuk keluarga. |
| Bebas | Tidak membatasi harga | Default yang tidak terlalu agresif. |
| Custom | Advanced filter | Untuk user yang ingin angka spesifik. |

## Filter Kebutuhan Praktis

| Filter | Status UI | Field | Alasan |
| --- | --- | --- | --- |
| Ada Parkir | Utama atau chip cepat | `parking_verified` | Penting untuk user bawa kendaraan. |
| Ada Mushola | Utama atau chip cepat | `mushola_verified` | Penting untuk wisata keluarga lokal. |
| Ada Toilet | Advanced | `toilet_verified` | Penting, tapi jangan penuhi layar utama. |
| Akses Kursi Roda | Advanced | `wheelchair_accessible_verified` | Sangat penting untuk user tertentu. |
| Indoor | Advanced | `indoor_verified`, labels | Relevan saat hujan/panas. |
| Outdoor | Tidak perlu filter khusus di awal | kategori/labels | Sudah tercakup oleh Alam/Petualangan. |
| Aman/Terverifikasi | Dipakai sistem, bukan chip utama | `safety_verified`, `is_active_verified` | Sebaiknya memengaruhi ranking dan warning. |

## Filter Hotel Sebagai Pendukung

| Prioritas | Filter Hotel | Bentuk UI | Field | Kapan Ditampilkan |
| ---: | --- | --- | --- | --- |
| 1 | Dekat Destinasi | Auto result | hotel lat/lon + wisata lat/lon | Setelah user klik destinasi. |
| 2 | Tipe Penginapan | Chip | `property_segment` | Saat user membuka panel penginapan. |
| 3 | Budget Menginap | Segmented/custom | `price_lowest` | Saat user memilih "Butuh Penginapan". |
| 4 | Rating Hotel | Slider sederhana | `overall_rating`, `reviews` | Advanced hotel panel. |
| 5 | Review Confidence | Dipakai sistem | `review_confidence_label` | Jangan ditampilkan ke user awam. |
| 6 | Fasilitas Utama | Checkbox | `has_wifi`, `has_parking`, `has_pool`, `has_air_conditioning` | Advanced hotel panel. |
| 7 | Cocok Keluarga | Toggle | `kid_friendly`, `kitchen_available` | Untuk villa/apartment/family trip. |
| 8 | Ada Gambar | Dipakai sistem | `image_available` | Untuk menentukan kartu visual. |
| 9 | Data Quality | Dipakai sistem | `data_quality_score` | Untuk ranking dan guardrail. |

## Filter Yang Tidak Disarankan Muncul Di Awal

| Filter | Masalah Jika Ditampilkan Di Awal | Rekomendasi |
| --- | --- | --- |
| Minimal rating | User awam belum tentu butuh, bisa membuang destinasi menarik | Masuk advanced. |
| Mode ranking | Terlalu teknis | Simpan default `Seimbang`, advanced jika perlu. |
| Jam rencana detail | Berguna, tapi tidak untuk first screen | Tampilkan setelah `Buka Sekarang`. |
| Crowd level | Data masih banyak `unknown` | Jangan dijadikan filter utama. |
| Sentiment confidence | Terlalu teknis | Pakai untuk ranking internal. |
| Status verifikasi | Penting untuk safety, tapi istilahnya teknis | Ubah jadi badge "Data terverifikasi" di detail. |
| Semua fasilitas hotel | Terlalu banyak | Tampilkan setelah user memilih hotel/penginapan. |

## Rekomendasi Layout Final

| Area | Isi | Catatan |
| --- | --- | --- |
| Header | Logo + mungkin tombol status/server | Jangan terlalu ramai. |
| Search panel | Search bar besar + tombol cari | Ini pusat pengalaman AI. |
| Quick chips | Alam, Keluarga, Gratis, Buka Sekarang, Dekat Saya, Butuh Penginapan | Maksimal 6 chip terlihat. |
| Sidebar ringkas | Budget, radius, kebutuhan utama | Jangan tampilkan semua checkbox kategori. |
| Advanced drawer | Rating, jam detail, fasilitas lengkap, aksesibilitas, crowd, verifikasi | Bisa collapsible. |
| Result cards | Foto, nama, kategori, harga, rating, jam, durasi, jarak, alasan AI | Sudah cocok dengan arah UI sekarang. |
| Destination detail | Detail wisata + hotel terdekat | Tempat hotel mulai muncul. |

## MVP Filter Set

Jika harus dibuat sangat sederhana, cukup gunakan:

| Nomor | Filter | Wajib |
| ---: | --- | --- |
| 1 | Search / query bebas | Ya |
| 2 | Gaya liburan | Ya |
| 3 | Budget | Ya |
| 4 | Buka sekarang | Ya |
| 5 | Dekat saya / radius | Ya |
| 6 | Ramah anak | Ya |
| 7 | Butuh penginapan | Ya |
| 8 | Filter lanjutan | Ya |

## Kesimpulan

Filter Muter Bandung sebaiknya tidak meniru marketplace hotel atau dashboard admin. Fokusnya adalah membantu user menjawab: "Saya mau liburan seperti apa, dengan budget berapa, kapan, dan butuh penginapan atau tidak?" Filter teknis tetap penting, tetapi digunakan sistem untuk ranking, guardrail, dan detail page.
