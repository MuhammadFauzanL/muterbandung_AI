from __future__ import annotations

import json
from math import ceil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
CURATED_DIR = ROOT / "Penginapan_Workspace" / "02_Curated"
BATCH_ROOT = (
    ROOT
    / "Penginapan_Workspace"
    / "05_Apify_Review_Batches"
    / "Hotel_Review_Batches_Final_Ready"
    / "Compass_Full_Ready_Batches_2026-06-06"
)

FINAL_READY = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_READY_2026-06-05.csv"
TEST_BATCH = CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_TEST_BATCH_30_2026-06-05.csv"

BATCH_SIZE = 100
MAX_REVIEWS = 30


def build_payload(urls: list[str]) -> dict:
    return {
        "language": "id",
        "maxReviews": MAX_REVIEWS,
        "personalData": True,
        "startUrls": [{"url": url} for url in urls],
    }


def write_batches(df: pd.DataFrame, out_dir: Path, prefix: str) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    total_batches = ceil(len(df) / BATCH_SIZE)

    for batch_number in range(1, total_batches + 1):
        start = (batch_number - 1) * BATCH_SIZE
        end = start + BATCH_SIZE
        batch = df.iloc[start:end].copy()
        batch_name = f"{prefix}_batch_{batch_number:03d}"
        json_path = out_dir / f"{batch_name}.json"
        index_path = out_dir / f"{batch_name}_index.csv"

        payload = build_payload(batch["google_maps_search_url"].tolist())
        json_path.write_text(json.dumps(payload, indent=4, ensure_ascii=False), encoding="utf-8")

        index_cols = [
            "review_target_id",
            "penginapan_id",
            "name",
            "property_type",
            "review_scrape_priority",
            "review_confidence_label",
            "google_maps_search_query",
            "google_maps_search_url",
        ]
        index_cols = [col for col in index_cols if col in batch.columns]
        batch[index_cols].to_csv(index_path, index=False)

        rows.append(
            {
                "batch_name": batch_name,
                "batch_number": batch_number,
                "target_rows": len(batch),
                "max_reviews_per_target": MAX_REVIEWS,
                "estimated_max_review_rows": len(batch) * MAX_REVIEWS,
                "json_file": str(json_path),
                "index_file": str(index_path),
            }
        )

    assignment = pd.DataFrame(rows)
    assignment.to_csv(out_dir / f"{prefix}_assignment.csv", index=False)
    return assignment


def write_readme(
    all_assignment: pd.DataFrame,
    remaining_assignment: pd.DataFrame,
    all_rows: int,
    remaining_rows: int,
    skipped_test_rows: int,
) -> None:
    readme = f"""# Compass Review Batches Penginapan - 2026-06-06

Folder ini berisi batch JSON untuk actor Compass Google Maps Reviews Scraper.

## Rekomendasi Pakai

Gunakan folder `remaining_1110_after_test30` terlebih dahulu, karena 30 target pertama sudah pernah discrape sebagai batch test.

Kalau ingin re-run semuanya dari awal, gunakan folder `all_1140`.

## Ringkasan

| Set | Target | Batch | Catatan |
|---|---:|---:|---|
| `remaining_1110_after_test30` | {remaining_rows} | {len(remaining_assignment)} | Recommended, tidak mengulang batch test 30 |
| `all_1140` | {all_rows} | {len(all_assignment)} | Re-run semua target final |
| skipped test batch | {skipped_test_rows} | - | Sudah ada hasil scrape test |

## Setting JSON

```json
{{
  "language": "id",
  "maxReviews": {MAX_REVIEWS},
  "personalData": true,
  "startUrls": [
    {{"url": "https://www.google.com/maps/search/?api=1&query=..."}}
  ]
}}
```

## Cara Bagi ke Teman

1. Bagikan satu file JSON batch ke satu orang.
2. Bagikan juga file `_index.csv` pasangannya.
3. Setelah scraping selesai, simpan output JSON dengan nama batch yang sama.
4. Audit wajib dilakukan per batch: jumlah target yang muncul, match title, review text, dan target missing.

## Catatan

Jangan langsung menggabungkan hasil scrape ke sentiment sebelum audit match selesai.
"""
    (BATCH_ROOT / "README_COMPASS_BATCHES_2026-06-06.md").write_text(readme, encoding="utf-8")


def main() -> None:
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)

    final_ready = pd.read_csv(FINAL_READY, dtype=str, keep_default_na=False)
    test_batch = pd.read_csv(TEST_BATCH, dtype=str, keep_default_na=False)
    test_ids = set(test_batch["review_target_id"])

    final_ready = final_ready[final_ready["google_maps_search_url"].astype(str).str.strip().ne("")].copy()
    all_ready = final_ready.sort_values(["property_type", "name", "review_target_id"]).reset_index(drop=True)
    remaining = all_ready[~all_ready["review_target_id"].isin(test_ids)].reset_index(drop=True)

    all_assignment = write_batches(
        all_ready,
        BATCH_ROOT / "all_1140",
        "compass_penginapan_reviews_all_1140",
    )
    remaining_assignment = write_batches(
        remaining,
        BATCH_ROOT / "remaining_1110_after_test30",
        "compass_penginapan_reviews_remaining_1110",
    )

    all_assignment.to_csv(BATCH_ROOT / "ALL_1140_ASSIGNMENT.csv", index=False)
    remaining_assignment.to_csv(BATCH_ROOT / "REMAINING_1110_AFTER_TEST30_ASSIGNMENT.csv", index=False)

    summary = {
        "batch_size": BATCH_SIZE,
        "max_reviews_per_target": MAX_REVIEWS,
        "all_1140_rows": int(len(all_ready)),
        "all_1140_batches": int(len(all_assignment)),
        "remaining_1110_rows": int(len(remaining)),
        "remaining_1110_batches": int(len(remaining_assignment)),
        "skipped_test_batch_rows": int(len(test_ids)),
        "recommended_folder": str(BATCH_ROOT / "remaining_1110_after_test30"),
        "rerun_all_folder": str(BATCH_ROOT / "all_1140"),
    }
    (BATCH_ROOT / "compass_penginapan_review_batches_summary_2026-06-06.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    write_readme(
        all_assignment=all_assignment,
        remaining_assignment=remaining_assignment,
        all_rows=len(all_ready),
        remaining_rows=len(remaining),
        skipped_test_rows=len(test_ids),
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
