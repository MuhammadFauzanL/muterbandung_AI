# Local Scrape Candidates Audit

Tanggal: 2026-05-25

Audit ini membuat kandidat isian dari raw file lokal:

`Dataset\dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv`

Tidak ada dataset utama yang diubah.

## Ringkasan

- Raw Google Maps rows: 230
- Media queue rows: 53
- Data queue rows: 60
- Media candidates: 25
- Media approved candidates: 25
- Media review required: 0
- Data candidates: 10
- Data approved candidates: 9
- Data review required: 1
- Unresolved rows: 78
- Unresolved by queue: `{"data": 50, "media": 28}`

## Output

- `Dataset\3_Curated\local_scrape_media_candidates.csv`
- `Dataset\3_Curated\local_scrape_data_candidates.csv`
- `Dataset\3_Curated\local_scrape_unresolved_queue.csv`

## Catatan

- Kandidat dengan `approved_candidate` tetap harus ditinjau sebelum apply final.
- Kandidat dengan `review_required` tidak boleh langsung masuk dataset utama.
- Field yang tidak ada di raw extractor, seperti jam operasional, koordinat presisi, fasilitas, dan sentiment pipeline, tetap butuh verifikasi manual atau scraping sumber lain.
