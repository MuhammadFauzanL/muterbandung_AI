# Media Enrichment Audit - 2026-05-25

## Verdict

```text
PASSED WITH REVIEW QUEUE
```

Media URL dan link destinasi sudah diperkaya secara konservatif. Hanya match yang exact, fuzzy sangat tinggi, atau override eksplisit yang diaktifkan.

## Source Audit

- Curated rows: 234
- Raw media candidates after dedupe: 235
- Output dataset: `Dataset\3_Curated\DATABASE_WISATA_LABELED_V2_REVIEWED.csv`
- Groundtruth audit CSV: `Dataset\3_Curated\media_groundtruth_audit.csv`
- Review queue CSV: `Dataset\3_Curated\media_match_review_queue.csv`

## Match Summary

- Accepted media rows: 181/234
- Active candidate rows with media: 169/213
- Needs review/missing rows: 53

Status counts:

```json
{
  "accepted": 181,
  "missing": 53
}
```

Method counts:

```json
{
  "exact_normalized_title": 161,
  "fuzzy_high_confidence": 4,
  "manual_override": 16,
  "manual_reject": 2,
  "missing": 51
}
```

## Safety Policy

- URL gambar/link hanya aktif jika `media_available=true`.
- Match borderline tidak dimasukkan ke evidence pack; masuk `media_match_review_queue.csv`.
- Road-level result seperti `Jl. Curug Panganten` dan `Jl. Gn. Tampomas` ditolak manual.
- LLM validator tetap menolak URL yang tidak ada di `candidate.media`.

## Review Queue Sample

| location_id | location_name | suggested_title | score | note |
|---|---|---|---:|---|
| LOC-155 | Curug Panganten | Jl. Curug Panganten | 0.909 | Road/route result, not destination-level media. |
| LOC-037 | Gn. Tampomas | Jl. Gn. Tampomas | 0.880 | Road result, not destination-level media. |
| LOC-176 | Padepokan Dayang Sumbi | Penginapan Dayang Sumbi | 0.800 | No reliable media match. |
| LOC-177 | Wahoo Waterworld | Wahoo Waterworld Bandung | 0.800 | No reliable media match. |
| LOC-182 | Pine Forest Camp Lembang | Pine Forest Camp | 0.800 | No reliable media match. |
| LOC-187 | Curug Layung | Curug Pelangi | 0.800 | No reliable media match. |
| LOC-190 | Curug Anom | Curug Dago | 0.800 | No reliable media match. |
| LOC-228 | Tanjung Duriat | Wisata Tanjung Duriat | 0.800 | No reliable media match. |
| LOC-159 | Penangkaran Rusa Kertamanah | Penangkaran Rusa Ranca Upas | 0.778 | No reliable media match. |
| LOC-196 | Curug Walanda Citatah | Curug Walanda | 0.765 | No reliable media match. |
| LOC-215 | Taman Pramuka Bandung | Taman Pramuka | 0.765 | No reliable media match. |
| LOC-163 | Kampung Adat Cikondang | Rumah Adat Cikondang | 0.762 | No reliable media match. |
| LOC-222 | Nuansa Riung Gunung | Nuansa Riung gunung Pangalengan | 0.760 | No reliable media match. |
| LOC-193 | Sanghyang Poek | Sanghyang Kenit | 0.759 | No reliable media match. |
| LOC-198 | Tebing Gunung Hawu | Gunung Hawu | 0.759 | No reliable media match. |
| LOC-183 | Imah Seniman Lembang | MiniMania Lembang | 0.757 | No reliable media match. |
| LOC-186 | Indiana Camp Lembang | Indiana Camp | 0.750 | No reliable media match. |
| LOC-201 | Curug Batu Templek | CURUG BATU TEMPLEK CISANGGARUNG | 0.735 | No reliable media match. |
| LOC-120 | Rumah Guguk | Rumah Guguk Petshop | 0.733 | No reliable media match. |
| LOC-225 | Curug Ceret Pangalengan | Curug Ceret (Naringgul) | 0.727 | No reliable media match. |
| LOC-226 | Gunung Nini Pangalengan | Wayang Windu Pangalengan | 0.723 | No reliable media match. |
| LOC-181 | Noah's Park Lembang | Noah's Park / Wisata Lembang Bandung | 0.717 | No reliable media match. |
| LOC-199 | Taman Buru Gunung Masigit Kareumbi | Kawasan Konservasi Taman Buru G. Masigit Kareumbi | 0.707 | No reliable media match. |
| LOC-148 | Pesona Nirwana Waterpark | Pesona Nirwana Waterpark & Cottages / Resort | 0.706 | No reliable media match. |
| LOC-149 | Taman Wisata Alam Cimanggu | Taman EcoWisata Cimenteng | 0.706 | No reliable media match. |

## Next Checks

## Verification

Syntax check:

```text
ast_ok 6
node --check Scripts/static/script.js: OK
```

Unit test:

```text
python -B -m unittest Scripts.test_recommender Scripts.test_llm_evidence_pack Scripts.test_llm_guard
Ran 26 tests
OK
```

Live API smoke test:

```text
top: Glamping Legok Kondang
recommendations[0].media.available: True
llm_evidence_pack.candidates[0].media.available: True
llm_prompt_guard: present
```

Live LLM validator:

```text
valid media URL from evidence: 200 True
fake URL outside evidence: 422 False
```

Groundtruth live:

```text
Passed: 62
Failed: 0
Errors: 0
```

QC live:

```text
Passed: 62
Failed: 0
Errors: 0
```

Frontend Playwright:

```text
desktop: media image rendered for top result
mobile: top card image width 294.5 px, naturalWidth 426
screenshots: media-enrichment-results-desktop.png, media-enrichment-results-mobile.png
```

Operational:

```text
Port 5000 LISTENING PID: 9936
Backup created: Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv.bak_media_20260525_130324
```
