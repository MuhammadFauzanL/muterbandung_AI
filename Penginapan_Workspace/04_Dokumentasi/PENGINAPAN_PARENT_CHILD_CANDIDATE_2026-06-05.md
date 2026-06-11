# Penginapan Parent-Child Candidate Mapping - 2026-06-05

Dokumen ini mencatat tahap awal entity resolution penginapan.

Status output: **candidate mapping**, belum relasi final.

## Output

- Possible duplicate review: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_POSSIBLE_DUPLICATE_REVIEW_2026-06-05.csv`
- Room-level listings: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_ROOM_LEVEL_LISTINGS_2026-06-05.csv`
- Parent-child mapping candidate: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_2026-06-05.csv`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Candidate input rows | 1656 |
| Possible duplicate rows | 247 |
| Possible duplicate groups | 111 |
| Room-level listing rows | 54 |
| Parent-child mapping rows | 54 |
| Child with parent candidate | 13 |
| Child without parent candidate | 41 |

## Confidence Label

| Confidence label | Jumlah |
|---|---:|
| no_candidate | 41 |
| high | 8 |
| medium | 5 |

## Catatan Keputusan

- Mapping ini tidak mengubah canonical candidate.
- Relasi dengan confidence tinggi tetap belum dianggap final.
- Child listing tidak dihapus otomatis.
- Review scraping sebaiknya menunggu parent utama dipilih.
