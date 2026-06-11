import json
import subprocess
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_output


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
PHASE_TITLE = "## Fase I - Review Drive dan Sentiment Hotel"


def run_code(code):
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    text = completed.stdout
    if completed.stderr:
        text += ("\n" if text else "") + completed.stderr
    if completed.returncode != 0:
        text += f"\n[exit_code={completed.returncode}]"
    return text.strip()


def code_cell(source):
    cell = new_code_cell(source)
    output_text = run_code(source)
    cell["execution_count"] = None
    cell["outputs"] = [new_output("stream", name="stdout", text=output_text + "\n")]
    return cell


def remove_existing_phase(cells):
    clean = []
    skip = False
    for cell in cells:
        source = cell.get("source", "")
        if cell.get("cell_type") == "markdown" and source.startswith(PHASE_TITLE):
            skip = True
            continue
        if skip and cell.get("cell_type") == "markdown" and source.startswith("## Fase "):
            skip = False
        if not skip:
            clean.append(cell)
    return clean


def main():
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb.cells = remove_existing_phase(nb.cells)

    new_cells = [
        new_markdown_cell(
            PHASE_TITLE
            + "\n\nTujuan: memasukkan batch review dari zip Drive, lalu cek apakah cukup kuat untuk sentiment hotel."
        ),
        code_cell(
            r"""
from pathlib import Path
import pandas as pd

zip_path = Path("drive-download-20260610T103243Z-3-001.zip")
raw_dir = Path("Penginapan_Workspace/01_Raw_Data/google_maps_reviews_json/drive_download_20260610T103243Z_3_001")
files = sorted(raw_dir.glob("*.csv"))

rows = 0
text_rows = 0
for path in files:
    df = pd.read_csv(path, usecols=lambda c: c in {"text", "textTranslated", "searchString", "title"})
    rows += len(df)
    text_rows += (
        df.get("text", pd.Series("", index=df.index)).fillna("").astype(str).str.strip().ne("")
        | df.get("textTranslated", pd.Series("", index=df.index)).fillna("").astype(str).str.strip().ne("")
    ).sum()

print("zip_exists:", zip_path.exists())
print("raw_dir:", raw_dir)
print("csv_file_count:", len(files))
print("raw_review_rows:", rows)
print("raw_rows_with_text:", int(text_rows))
print("first_files:", [p.name for p in files[:3]])
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: batch Drive diterima sebagai sumber review hotel. Isinya CSV Apify, bukan JSON, jadi normalizer dibuat membaca CSV juga."
        ),
        code_cell(
            r"""
import json
from pathlib import Path

summary_path = Path("Penginapan_Workspace/02_Curated/penginapan_review_2026-06-10_drive_full_review_normalize_summary.json")
summary = json.loads(summary_path.read_text(encoding="utf-8"))
for key in [
    "raw_file_count",
    "raw_rows_read",
    "matched_rows_after_dedupe",
    "unique_review_targets_matched",
    "unique_penginapan_matched",
    "rows_with_text",
    "target_total_final_ready",
]:
    print(f"{key}: {summary.get(key)}")
print("normalized_output:", Path(summary["outputs"]["normalized"]).name)
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: normalisasi valid. Semua row berhasil match ke target, tapi coverage belum penuh karena target yang kena review baru sebagian."
        ),
        code_cell(
            r"""
import json
from pathlib import Path

coverage_path = Path("Penginapan_Workspace/02_Curated/penginapan_review_2026-06-10_drive_full_review_coverage_summary.json")
coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
for key in [
    "target_total",
    "review_rows",
    "target_with_any_scrape",
    "target_with_text_review",
    "target_missing_from_batch",
]:
    print(f"{key}: {coverage.get(key)}")
print("status_counts:", coverage.get("review_batch_status_counts"))
print("missing_file:", Path(coverage["outputs"]["missing_targets"]).name)
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: target yang sudah punya teks dipakai untuk sentiment. Target yang belum ada disimpan sebagai queue scraping berikutnya."
        ),
        code_cell(
            r"""
import json
import pandas as pd
from pathlib import Path

summary_path = Path("Penginapan_Workspace/02_Curated/penginapan_sentiment_baseline_summary_2026-06-10_DRIVE_FULL_REVIEW.json")
summary = json.loads(summary_path.read_text(encoding="utf-8"))
for key in [
    "review_rows_input",
    "review_rows_with_text_inference",
    "parent_hotels_with_sentiment",
    "parent_master_rows",
    "parent_master_with_sentiment_rows",
    "sentiment_global_average",
    "model_warning_count",
]:
    print(f"{key}: {summary.get(key)}")

agg = pd.read_csv("Penginapan_Workspace/02_Curated/PENGINAPAN_SENTIMENT_AGGREGATED_2026-06-10_DRIVE_FULL_REVIEW.csv")
cols = [
    "parent_penginapan_id",
    "hotel_review_count_analyzed",
    "hotel_adjusted_sentiment_score",
    "hotel_review_confidence_label",
]
print(agg.sort_values("hotel_review_count_analyzed", ascending=False)[cols].head(8).to_string(index=False))
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: sentiment hotel naik jauh. Model dipakai sebagai baseline produksi awal, dengan catatan warning versi scikit-learn perlu dibereskan saat deployment."
        ),
        code_cell(
            r"""
from Scripts.penginapan_recommender import PenginapanRecommender

dataset = "Penginapan_Workspace/02_Curated/PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10_DRIVE_FULL_REVIEW.csv"
engine = PenginapanRecommender(dataset)
result = engine.recommend(
    query="hotel dekat alun alun bandung murah",
    user_lat=-6.9219,
    user_lon=107.6069,
    top_k=5,
)
print("total_results:", result["total_results"])
print("dataset:", result["metadata"]["dataset_path"].split("/")[-1].split("\\")[-1])
for item in result["recommendations"]:
    print(item["rank"], item["name"], item["distance_km"], item["final_score"], item["hotel_adjusted_sentiment_label"])
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: dataset baru dipakai untuk baseline recommender hotel. Bobot jarak tetap paling besar agar hotel dekat wisata/titik user naik lebih dulu."
        ),
    ]

    nb.cells.extend(new_cells)
    nbformat.write(nb, NOTEBOOK_PATH)
    print(json.dumps({"notebook": str(NOTEBOOK_PATH), "added_phase": PHASE_TITLE, "cell_count": len(nb.cells)}, indent=2))


if __name__ == "__main__":
    main()
