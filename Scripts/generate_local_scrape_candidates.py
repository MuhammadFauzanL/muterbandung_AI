import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import nbformat as nbf
import pandas as pd


RAW_PATH = Path("Wisata_Workspace/01_Dataset/dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv")
MEDIA_QUEUE_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/manual_media_fill_queue.csv")
DATA_QUEUE_PATH = Path("Wisata_Workspace/01_Dataset/3_Curated/manual_data_fill_queue.csv")
OUT_DIR = Path("Wisata_Workspace/01_Dataset/3_Curated")
MEDIA_CANDIDATES_PATH = OUT_DIR / "local_scrape_media_candidates.csv"
DATA_CANDIDATES_PATH = OUT_DIR / "local_scrape_data_candidates.csv"
UNRESOLVED_PATH = OUT_DIR / "local_scrape_unresolved_queue.csv"
AUDIT_PATH = Path("Wisata_Workspace/03_Dokumentasi/LOCAL_SCRAPE_AUDIT_2026-05-25.md")
MASTER_NOTEBOOK_PATH = Path("Wisata_Workspace/02_Notebooks/wisata_training.ipynb")
MASTER_MARKER = "MUTERBANDUNG_LOCAL_SCRAPE_CANDIDATES_2026_05_25"

MATCH_THRESHOLD = 0.82
AUTO_REVIEW_THRESHOLD = 0.93


def normalize_name(value):
    text = str(value or "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\b(bandung|kota|kabupaten|jawa|barat|wisata|the|official)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similarity(left, right):
    left_norm = normalize_name(left)
    right_norm = normalize_name(right)
    if not left_norm or not right_norm:
        return 0.0
    direct = SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = set(left_norm.split())
    right_tokens = set(right_norm.split())
    overlap = len(left_tokens & right_tokens) / max(1, len(left_tokens | right_tokens))
    containment = len(left_tokens & right_tokens) / max(1, min(len(left_tokens), len(right_tokens)))
    return round(max(direct, overlap, containment), 4)


def best_raw_match(raw_df, location_name):
    scored = []
    for _, raw in raw_df.iterrows():
        score = similarity(location_name, raw.get("title", ""))
        if score >= MATCH_THRESHOLD:
            scored.append((score, raw))
    if not scored:
        return None, 0.0
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1], scored[0][0]


def non_empty(value):
    return str(value or "").strip() not in {"", "nan", "None"}


def build_media_candidates(raw_df, queue_df):
    rows = []
    for _, row in queue_df.iterrows():
        location_name = row.get("location_name", "")
        raw, score = best_raw_match(raw_df, location_name)
        if raw is None:
            continue
        has_media = any(non_empty(raw.get(col, "")) for col in ["imageUrl", "url", "website"])
        if not has_media:
            continue
        rows.append(
            {
                "location_id": row.get("location_id", ""),
                "location_name": location_name,
                "category": row.get("category", ""),
                "priority": row.get("priority", ""),
                "matched_raw_title": raw.get("title", ""),
                "match_score": score,
                "new_media_image_url": raw.get("imageUrl", ""),
                "new_media_destination_url": raw.get("url", ""),
                "new_media_website": raw.get("website", ""),
                "new_media_source_note": "local_google_maps_extractor_2026-05-19",
                "reviewer_status": "review_required" if score < AUTO_REVIEW_THRESHOLD else "approved_candidate",
                "reviewer_note": "Auto-candidate from local Google Maps extractor; verify before apply.",
            }
        )
    return pd.DataFrame(rows)


def build_data_candidates(raw_df, queue_df):
    rows = []
    for _, row in queue_df.iterrows():
        field_name = str(row.get("field_name", "")).strip()
        if field_name != "avg_rating":
            continue
        location_name = row.get("location_name", "")
        raw, score = best_raw_match(raw_df, location_name)
        if raw is None or not non_empty(raw.get("totalScore", "")):
            continue
        rows.append(
            {
                "location_id": row.get("location_id", ""),
                "location_name": location_name,
                "category": row.get("category", ""),
                "priority": row.get("priority", ""),
                "issue_type": row.get("issue_type", ""),
                "field_name": field_name,
                "current_value": row.get("current_value", ""),
                "new_value": raw.get("totalScore", ""),
                "source_url": raw.get("url", ""),
                "matched_raw_title": raw.get("title", ""),
                "match_score": score,
                "reviewer_status": "review_required" if score < AUTO_REVIEW_THRESHOLD else "approved_candidate",
                "reviewer_note": "Auto-candidate rating from local Google Maps extractor; verify before apply.",
            }
        )
    return pd.DataFrame(rows)


def build_unresolved(media_queue, data_queue, media_candidates, data_candidates):
    rows = []
    media_done = set(media_candidates.get("location_id", pd.Series(dtype=str)).astype(str))
    for _, row in media_queue.iterrows():
        loc_id = str(row.get("location_id", ""))
        if loc_id not in media_done:
            rows.append(
                {
                    "queue_type": "media",
                    "location_id": loc_id,
                    "location_name": row.get("location_name", ""),
                    "priority": row.get("priority", ""),
                    "field_name": "media",
                    "reason": "no reliable local raw media match",
                }
            )
    data_done = {
        (str(row.get("location_id", "")), str(row.get("field_name", "")))
        for _, row in data_candidates.iterrows()
    }
    for _, row in data_queue.iterrows():
        key = (str(row.get("location_id", "")), str(row.get("field_name", "")))
        if key not in data_done:
            rows.append(
                {
                    "queue_type": "data",
                    "location_id": row.get("location_id", ""),
                    "location_name": row.get("location_name", ""),
                    "priority": row.get("priority", ""),
                    "field_name": row.get("field_name", ""),
                    "reason": "not derivable from local Google Maps extractor",
                }
            )
    return pd.DataFrame(rows)


def write_audit(raw_df, media_queue, data_queue, media_candidates, data_candidates, unresolved):
    approved_media = int((media_candidates.get("reviewer_status", pd.Series(dtype=str)) == "approved_candidate").sum())
    review_media = int((media_candidates.get("reviewer_status", pd.Series(dtype=str)) == "review_required").sum())
    approved_data = int((data_candidates.get("reviewer_status", pd.Series(dtype=str)) == "approved_candidate").sum())
    review_data = int((data_candidates.get("reviewer_status", pd.Series(dtype=str)) == "review_required").sum())
    unresolved_counts = unresolved["queue_type"].value_counts().to_dict() if len(unresolved) else {}

    text = f"""# Local Scrape Candidates Audit

Tanggal: 2026-05-25

Audit ini membuat kandidat isian dari raw file lokal:

`{RAW_PATH}`

Tidak ada dataset utama yang diubah.

## Ringkasan

- Raw Google Maps rows: {len(raw_df)}
- Media queue rows: {len(media_queue)}
- Data queue rows: {len(data_queue)}
- Media candidates: {len(media_candidates)}
- Media approved candidates: {approved_media}
- Media review required: {review_media}
- Data candidates: {len(data_candidates)}
- Data approved candidates: {approved_data}
- Data review required: {review_data}
- Unresolved rows: {len(unresolved)}
- Unresolved by queue: `{json.dumps(unresolved_counts, ensure_ascii=False)}`

## Output

- `{MEDIA_CANDIDATES_PATH}`
- `{DATA_CANDIDATES_PATH}`
- `{UNRESOLVED_PATH}`

## Catatan

- Kandidat dengan `approved_candidate` tetap harus ditinjau sebelum apply final.
- Kandidat dengan `review_required` tidak boleh langsung masuk dataset utama.
- Field yang tidak ada di raw extractor, seperti jam operasional, koordinat presisi, fasilitas, dan sentiment pipeline, tetap butuh verifikasi manual atau scraping sumber lain.
"""
    AUDIT_PATH.write_text(text, encoding="utf-8")


def append_master_notebook(summary):
    if not MASTER_NOTEBOOK_PATH.exists():
        return
    with MASTER_NOTEBOOK_PATH.open("r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MASTER_MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## Local Scrape Candidates

`{MASTER_MARKER}`

Tahap ini membuat kandidat pengisian data dari raw Google Maps extractor lokal, tanpa Colab dan tanpa mengubah dataset utama.

Output:

- `Dataset/3_Curated/local_scrape_media_candidates.csv`
- `Dataset/3_Curated/local_scrape_data_candidates.csv`
- `Dataset/3_Curated/local_scrape_unresolved_queue.csv`
- `Wisata_Workspace/03_Dokumentasi/LOCAL_SCRAPE_AUDIT_2026-05-25.md`

Ringkasan:

```json
{json.dumps(summary, indent=2, ensure_ascii=False)}
```
"""

    code = """import pandas as pd

for path in [
    "Dataset/3_Curated/local_scrape_media_candidates.csv",
    "Dataset/3_Curated/local_scrape_data_candidates.csv",
    "Dataset/3_Curated/local_scrape_unresolved_queue.csv",
]:
    df = pd.read_csv(path)
    print(path, "rows:", len(df))
    display(df.head(5))
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(code))

    with MASTER_NOTEBOOK_PATH.open("w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)


def main():
    raw_df = pd.read_csv(RAW_PATH).fillna("")
    media_queue = pd.read_csv(MEDIA_QUEUE_PATH).fillna("")
    data_queue = pd.read_csv(DATA_QUEUE_PATH).fillna("")

    media_candidates = build_media_candidates(raw_df, media_queue)
    data_candidates = build_data_candidates(raw_df, data_queue)
    unresolved = build_unresolved(media_queue, data_queue, media_candidates, data_candidates)

    media_candidates.to_csv(MEDIA_CANDIDATES_PATH, index=False)
    data_candidates.to_csv(DATA_CANDIDATES_PATH, index=False)
    unresolved.to_csv(UNRESOLVED_PATH, index=False)

    write_audit(raw_df, media_queue, data_queue, media_candidates, data_candidates, unresolved)

    summary = {
        "raw_rows": len(raw_df),
        "media_queue_rows": len(media_queue),
        "data_queue_rows": len(data_queue),
        "media_candidates": len(media_candidates),
        "data_candidates": len(data_candidates),
        "unresolved": len(unresolved),
    }
    append_master_notebook(summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
