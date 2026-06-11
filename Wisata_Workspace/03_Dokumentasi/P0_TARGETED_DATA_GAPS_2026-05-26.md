# P0 Targeted Data Gaps - 2026-05-26

Sumber: `Dataset/3_Curated/targeted_data_completion_queue.csv`.

## Kesimpulan

- P0 tersisa: `43` task, semuanya `active_status_verification`.
- Jam buka sudah tidak muncul sebagai task completion setelah batch manual terakhir.
- Koordinat, media, fasilitas, dan rating/sentiment masih ada kekurangan, tetapi prioritasnya P1/P2 menurut scoring saat ini.

## Ringkasan Kekurangan

| Jenis kekurangan | Total | Prioritas |
| --- | ---: | --- |
| `active_status_verification` | 189 | P0:43, P1:146 |
| `coordinate_verification` | 9 | P1:9 |
| `facility_verification` | 202 | P1:54, P2:148 |
| `media_completion` | 40 | P1:20, P2:20 |
| `rating_sentiment_completion` | 17 | P1:17 |

## Batch Review yang Saya Rekomendasikan Dulu

File isian: `Dataset/3_Curated/manual_review_batch2_recommended_first_2026-05-26.csv`

| Task | Jumlah dalam batch |
| --- | ---: |
| `facility_verification` | 54 |
| `active_status_verification` | 43 |
| `media_completion` | 20 |
| `rating_sentiment_completion` | 17 |
| `coordinate_verification` | 9 |

## P0 Status Aktif yang Harus Dicek Manual

| ID | Destinasi | Kategori | Score |
| --- | --- | --- | ---: |
| `LOC-192` | Curug Ngebul Gununghalu | Wisata Alam | 111 |
| `LOC-196` | Curug Walanda Citatah | Wisata Alam | 111 |
| `LOC-226` | Gunung Nini Pangalengan | Wisata Alam | 111 |
| `LOC-176` | Padepokan Dayang Sumbi | Tempat Belajar | 111 |
| `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) | Wisata Alam | 111 |
| `LOC-195` | Sungai Cikahuripan Green Canyon Saguling | Wisata Alam | 111 |
| `LOC-213` | Taman Cibeunying | Taman Kota | 111 |
| `LOC-023` | Curug Malela | Wisata Alam | 105 |
| `LOC-044` | Jans Park (Jatinangor National Park) | Rekreasi Keluarga | 105 |
| `LOC-138` | Kebun Teh Sukawana | Wisata Alam | 105 |
| `LOC-166` | Muara Rahong Hills | Wisata Alam | 105 |
| `LOC-069` | Pemandian Cipanas Cileungsing | Wisata Alam | 105 |
| `LOC-116` | Wisata Kampoeng Ciherang | Rekreasi Keluarga | 105 |
| `LOC-008` | Bandung Science Center | Tempat Belajar | 103 |
| `LOC-173` | Cakrawala Nature Sparkling Restaurant | Tempat Kuliner | 103 |
| `LOC-017` | Cihampelas Walk | Tempat Belanja | 103 |
| `LOC-180` | Cimory Dairyland Lembang | Wisata Satwa | 103 |
| `LOC-190` | Curug Anom | Wisata Alam | 103 |
| `LOC-201` | Curug Batu Templek | Wisata Alam | 103 |
| `LOC-225` | Curug Ceret Pangalengan | Wisata Alam | 103 |
| `LOC-187` | Curug Layung | Wisata Alam | 103 |
| `LOC-178` | De'Ranch Lembang | Wisata Satwa | 103 |
| `LOC-029` | Dusun Bambu | Rekreasi Keluarga | 103 |
| `LOC-186` | Indiana Camp Lembang | Tempat Camping | 103 |
| `LOC-164` | Java Preanger Gunung Tilu | Wisata Alam | 103 |
| `LOC-163` | Kampung Adat Cikondang | Desa Wisata | 103 |
| `LOC-217` | Karang Setra Waterland | Wahana Air | 103 |
| `LOC-139` | Kawah Rengganis Ciwidey | Wisata Alam | 103 |
| `LOC-152` | Kebun Teh Rancabali | Wisata Alam | 103 |
| `LOC-219` | Museum Inggit Garnasih | Tempat Belajar | 103 |
| `LOC-181` | Noah's Park Lembang | Rekreasi Keluarga | 103 |
| `LOC-121` | NuArt Sculpture Park | Tempat Seni | 103 |
| `LOC-222` | Nuansa Riung Gunung | Wisata Alam | 103 |
| `LOC-068` | Pasar Cimindi | Tempat Belanja | 103 |
| `LOC-234` | Perkebunan Teh Rancabali | Rekreasi Alam | 103 |
| `LOC-182` | Pine Forest Camp Lembang | Tempat Camping | 103 |
| `LOC-137` | Rumah Belanda | Tempat Budaya | 103 |
| `LOC-193` | Sanghyang Poek | Wisata Alam | 103 |
| `LOC-224` | Sungai Palayangan Rafting | Wisata Petualangan | 103 |
| `LOC-135` | Taman Main Mili-Mili & Hutan Mycelia | Rekreasi Keluarga | 103 |
| `LOC-215` | Taman Pramuka Bandung | Taman Kota | 103 |
| `LOC-149` | Taman Wisata Alam Cimanggu | Wisata Alam | 103 |
| `LOC-198` | Tebing Gunung Hawu | Wisata Alam | 103 |

## Koordinat Perlu Verifikasi

| ID | Destinasi | Kategori | Priority |
| --- | --- | --- | --- |
| `LOC-023` | Curug Malela | Wisata Alam | P1 |
| `LOC-155` | Curug Panganten | Wisata Alam | P1 |
| `LOC-044` | Jans Park (Jatinangor National Park) | Rekreasi Keluarga | P1 |
| `LOC-138` | Kebun Teh Sukawana | Wisata Alam | P1 |
| `LOC-166` | Muara Rahong Hills | Wisata Alam | P1 |
| `LOC-069` | Pemandian Cipanas Cileungsing | Wisata Alam | P1 |
| `LOC-162` | Rumah Putih Cukul | Rekreasi Keluarga | P1 |
| `LOC-158` | Situ Ninah (Situ Datar) | Wisata Alam | P1 |
| `LOC-116` | Wisata Kampoeng Ciherang | Rekreasi Keluarga | P1 |

## Rating/Sentiment Kosong

| ID | Destinasi | Kategori | Priority |
| --- | --- | --- | --- |
| `LOC-155` | Curug Panganten | Wisata Alam | P1 |
| `LOC-196` | Curug Walanda Citatah | Wisata Alam | P1 |
| `LOC-226` | Gunung Nini Pangalengan | Wisata Alam | P1 |
| `LOC-068` | Pasar Cimindi | Tempat Belanja | P1 |
| `LOC-234` | Perkebunan Teh Rancabali | Rekreasi Alam | P1 |
| `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) | Wisata Alam | P1 |
| `LOC-137` | Rumah Belanda | Tempat Budaya | P1 |
| `LOC-195` | Sungai Cikahuripan Green Canyon Saguling | Wisata Alam | P1 |
| `LOC-134` | Bukit Bintang Bandung (Patahan Lembang) | Wisata Alam | P1 |
| `LOC-192` | Curug Ngebul Gununghalu | Wisata Alam | P1 |
| `LOC-029` | Dusun Bambu | Rekreasi Keluarga | P1 |
| `LOC-152` | Kebun Teh Rancabali | Wisata Alam | P1 |
| `LOC-174` | Lereng Anteng Panoramic Coffee | Tempat Kuliner | P1 |
| `LOC-220` | Nimo Jungle Hot Spring | Wisata Alam | P1 |
| `LOC-176` | Padepokan Dayang Sumbi | Tempat Belajar | P1 |
| `LOC-162` | Rumah Putih Cukul | Rekreasi Keluarga | P1 |
| `LOC-213` | Taman Cibeunying | Taman Kota | P1 |

## Media/Gambar P1

| ID | Destinasi | Kategori |
| --- | --- | --- |
| `LOC-201` | Curug Batu Templek | Wisata Alam |
| `LOC-225` | Curug Ceret Pangalengan | Wisata Alam |
| `LOC-187` | Curug Layung | Wisata Alam |
| `LOC-196` | Curug Walanda Citatah | Wisata Alam |
| `LOC-178` | De'Ranch Lembang | Wisata Satwa |
| `LOC-226` | Gunung Nini Pangalengan | Wisata Alam |
| `LOC-183` | Imah Seniman Lembang | Penginapan Wisata |
| `LOC-186` | Indiana Camp Lembang | Tempat Camping |
| `LOC-219` | Museum Inggit Garnasih | Tempat Belajar |
| `LOC-181` | Noah's Park Lembang | Rekreasi Keluarga |
| `LOC-222` | Nuansa Riung Gunung | Wisata Alam |
| `LOC-148` | Pesona Nirwana Waterpark | Wahana Air |
| `LOC-182` | Pine Forest Camp Lembang | Tempat Camping |
| `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) | Wisata Alam |
| `LOC-120` | Rumah Guguk | Wisata Satwa |
| `LOC-193` | Sanghyang Poek | Wisata Alam |
| `LOC-195` | Sungai Cikahuripan Green Canyon Saguling | Wisata Alam |
| `LOC-215` | Taman Pramuka Bandung | Taman Kota |
| `LOC-198` | Tebing Gunung Hawu | Wisata Alam |
| `LOC-177` | Wahoo Waterworld | Wahana Air |
