# Penginapan Parent Master Final - 2026-06-05

Tahap ini memisahkan parent dan child listing berdasarkan 13 relasi yang sudah direview manual.

## Output

- Relations final: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv`
- Parent master: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_PARENT_MASTER_2026-06-05.csv`
- Child listings final: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_CHILD_LISTINGS_FINAL_2026-06-05.csv`
- Review scrape targets: `D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace\02_Curated\PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv`

## Ringkasan

| Metrik | Nilai |
|---|---:|
| Candidate rows | 1656 |
| Final accepted relations | 13 |
| Parent master rows | 1602 |
| Child listing rows | 54 |
| Review target rows | 1518 |
| Validation gate | PASS_WITH_WARNINGS |

## Catatan Singkat

- Child tidak dihapus, hanya tidak masuk ranking utama.
- Parent master dipakai untuk ranking dan target scraping review.
- Child tanpa parent final tetap ditahan sebagai child, bukan dipromosikan ke parent.
