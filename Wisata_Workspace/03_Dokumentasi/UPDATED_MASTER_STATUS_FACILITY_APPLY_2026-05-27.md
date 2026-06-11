# Updated Master Status + Facility Apply - 2026-05-27

Generated at: `2026-05-27T00:22:03.523992Z`
Dataset: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
Source master: `updated_master_wisata_bandung.csv`
Backup: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_updated_master_status_facility_20260527_072203`

## Summary

- Status rows applied: `42`
- Status rows skipped: `1`
- Facility rows applied: `54`
- Missing/invalid rows skipped: `0`

## Applied Status Decisions

| Decision | Count |
| --- | ---: |
| `include_active` | 39 |
| `exclude_closed` | 1 |
| `exclude_unclear` | 1 |
| `include_renamed` | 1 |

## Applied Facility Flags

| Flag | Count |
| --- | ---: |
| `parking_verified` | 54 |
| `toilet_verified` | 53 |
| `mushola_verified` | 50 |
| `wheelchair_accessible_verified` | 12 |
| `pet_friendly_verified` | 11 |

## Skipped Status Rows

| ID | Name | Decision | Reason |
| --- | --- | --- | --- |
| `LOC-196` | Curug Walanda Citatah | `needs_manual_check` | Status decision is not safe for automatic apply. |

## Applied Status Rows

| ID | Name | Decision |
| --- | --- | --- |
| `LOC-008` | Bandung Science Center | `exclude_closed` |
| `LOC-017` | Cihampelas Walk | `include_active` |
| `LOC-023` | Curug Malela | `include_active` |
| `LOC-029` | Dusun Bambu | `include_active` |
| `LOC-044` | Jans Park (Jatinangor National Park) | `include_active` |
| `LOC-068` | Pasar Cimindi | `include_active` |
| `LOC-069` | Pemandian Cipanas Cileungsing | `include_active` |
| `LOC-116` | Wisata Kampoeng Ciherang | `include_active` |
| `LOC-121` | NuArt Sculpture Park | `include_active` |
| `LOC-133` | Punclut Bandung (Puncak Ciumbuleuit) | `include_active` |
| `LOC-135` | Taman Main Mili-Mili & Hutan Mycelia | `include_active` |
| `LOC-137` | Rumah Belanda | `exclude_unclear` |
| `LOC-138` | Kebun Teh Sukawana | `include_active` |
| `LOC-139` | Kawah Rengganis Ciwidey | `include_active` |
| `LOC-149` | Taman Wisata Alam Cimanggu | `include_active` |
| `LOC-152` | Kebun Teh Rancabali | `include_active` |
| `LOC-163` | Kampung Adat Cikondang | `include_active` |
| `LOC-164` | Java Preanger Gunung Tilu | `include_active` |
| `LOC-166` | Muara Rahong Hills | `include_active` |
| `LOC-173` | Cakrawala Nature Sparkling Restaurant | `include_active` |
| `LOC-176` | Padepokan Dayang Sumbi | `include_active` |
| `LOC-178` | De Ranch Lembang | `include_renamed` |
| `LOC-180` | Cimory Dairyland Lembang | `include_active` |
| `LOC-181` | Noah's Park Lembang | `include_active` |
| `LOC-182` | Pine Forest Camp Lembang | `include_active` |
| `LOC-186` | Indiana Camp Lembang | `include_active` |
| `LOC-187` | Curug Layung | `include_active` |
| `LOC-190` | Curug Anom | `include_active` |
| `LOC-192` | Curug Ngebul Gununghalu | `include_active` |
| `LOC-193` | Sanghyang Poek | `include_active` |
| `LOC-195` | Sungai Cikahuripan Green Canyon Saguling | `include_active` |
| `LOC-198` | Tebing Gunung Hawu | `include_active` |
| `LOC-201` | Curug Batu Templek | `include_active` |
| `LOC-213` | Taman Cibeunying | `include_active` |
| `LOC-215` | Taman Pramuka Bandung | `include_active` |
| `LOC-217` | Karang Setra Waterland | `include_active` |
| `LOC-219` | Museum Inggit Garnasih | `include_active` |
| `LOC-222` | Nuansa Riung Gunung | `include_active` |
| `LOC-224` | Sungai Palayangan Rafting | `include_active` |
| `LOC-225` | Curug Ceret Pangalengan | `include_active` |
| `LOC-226` | Gunung Nini Pangalengan | `include_active` |
| `LOC-234` | Perkebunan Teh Rancabali | `include_active` |

## Applied Facility Rows

| ID | Name | Updated Flags |
| --- | --- | --- |
| `LOC-001` | 23 Paskal Shopping Center | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True`, `pet_friendly_verified=False` |
| `LOC-002` | Alam Wisata Cimahi | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-005` | Amazing Artgames | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-006` | Bandung Carnival Land | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-007` | Bandung Indah Plaza | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True`, `pet_friendly_verified=False` |
| `LOC-010` | Braga Citywalk | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-017` | Cihampelas Walk | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True` |
| `LOC-018` | Cimahi Mall | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `pet_friendly_verified=False` |
| `LOC-027` | Dago Dreampark | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-029` | Dusun Bambu | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True` |
| `LOC-030` | Farm House Susu Lembang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-031` | Floating Market Lembang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True` |
| `LOC-038` | Gn. Tangkuban Parahu | `parking_verified=True`, `toilet_verified=True`, `wheelchair_accessible_verified=False` |
| `LOC-044` | Jans Park (Jatinangor National Park) | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-054` | Lembang Wonderland | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-064` | Nimo Highland | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-066` | Pandiga Educreation Sports | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-067` | Paris Van Java | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-068` | Pasar Cimindi | `parking_verified=True`, `wheelchair_accessible_verified=False`, `pet_friendly_verified=False` |
| `LOC-074` | RM Sangu Liwet Ibu Ika | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-097` | Taman Lembah Dewata | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-102` | Terminal Wisata Grafika Cikole | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-104` | The Kings Shopping Centre | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `pet_friendly_verified=False` |
| `LOC-105` | The Lodge Maribaya | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=False` |
| `LOC-106` | The Nice Park Bandung | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-108` | Trans Studio Bandung | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True`, `pet_friendly_verified=False` |
| `LOC-109` | Trans Studio Mall Bandung | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True`, `pet_friendly_verified=False` |
| `LOC-110` | Upside Down World Bandung | `parking_verified=True`, `toilet_verified=True` |
| `LOC-111` | Venus Cimahi | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-116` | Wisata Kampoeng Ciherang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-117` | Kiara Artha Park | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True` |
| `LOC-122` | Peta Park | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-127` | Sarae Hills | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-130` | Fairy Garden by The Lodge | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-135` | Taman Main Mili-Mili & Hutan Mycelia | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-141` | Taman Wisata Bougenville | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-144` | Barusen Hills Ciwidey | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-145` | Palalangon Park | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-146` | Taman Love Soreang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-147` | Victory Waterpark Soreang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `pet_friendly_verified=False` |
| `LOC-148` | Pesona Nirwana Waterpark | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `pet_friendly_verified=False` |
| `LOC-162` | Rumah Putih Cukul | `parking_verified=True`, `toilet_verified=True` |
| `LOC-165` | Malabar Mountain Coffee Shop | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-167` | Cicalengka Dreamland | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-169` | Dago Bakery Punclut | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-171` | D'Dieuland | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-172` | Sudut Pandang Bandung | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-173` | Cakrawala Nature Sparkling Restaurant | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-174` | Lereng Anteng Panoramic Coffee | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-177` | Wahoo Waterworld | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `wheelchair_accessible_verified=True`, `pet_friendly_verified=False` |
| `LOC-179` | Mini Mania Lembang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-181` | Noah's Park Lembang | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-216` | Panama Park 825 | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True` |
| `LOC-217` | Karang Setra Waterland | `parking_verified=True`, `toilet_verified=True`, `mushola_verified=True`, `pet_friendly_verified=False` |
