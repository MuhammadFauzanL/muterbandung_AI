from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
TAG = "penginapan_parent_master_final_2026_06_05"


def md(source: str):
    cell = new_markdown_cell(source.strip())
    cell.metadata["tags"] = [TAG, "decision-documentation"]
    return cell


def code(source: str):
    cell = new_code_cell(source.strip())
    cell.metadata["tags"] = [TAG, "audit-code"]
    return cell


def build_section() -> list:
    return [
        md(
            """
## Fase C - Parent Master dan Target Review

Fase ini memakai 13 relasi yang sudah direview manual sebagai relasi final.

| Catatan |
|---|
| Child tidak dibuang. Child hanya dipisahkan dari daftar parent utama. |
| Parent master dipakai untuk ranking dan target scraping review. |
"""
        ),
        md(
            """
## Tahap A - Buat Relasi Final

| Catatan |
|---|
| 13 pasangan yang sudah accept dicatat sebagai relasi final. |
"""
        ),
        code(
            """
from pathlib import Path
import json
import subprocess
import sys

import pandas as pd
from IPython.display import display

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

WORKSPACE = PROJECT_ROOT / "Penginapan_Workspace"
CURATED_DIR = WORKSPACE / "02_Curated"
SCRIPT_DIR = WORKSPACE / "06_Scripts"

run_final = subprocess.run(
    [sys.executable, str(SCRIPT_DIR / "build_penginapan_parent_master_final.py")],
    check=True,
    capture_output=True,
    text=True,
)
print(run_final.stdout.strip())

relations_path = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv"
relations_df = pd.read_csv(relations_path, dtype=str, keep_default_na=False)

display(pd.DataFrame({"metric": ["Final relations"], "value": [len(relations_df)]}))
display(relations_df[["child_penginapan_id", "child_name", "parent_penginapan_id", "parent_name", "manual_decision"]])
"""
        ),
        md(
            """
### Keputusan Tahap A

| Catatan |
|---|
| 13 relasi diterima sebagai final karena sudah direview manual. |
| Ini bukan auto-merge; sumber keputusannya tetap dicatat. |
"""
        ),
        md(
            """
## Tahap B - Pisahkan Parent dan Child

| Catatan |
|---|
| Parent untuk ranking. Child untuk detail kamar/unit. |
"""
        ),
        code(
            """
summary_path = CURATED_DIR / "penginapan_parent_master_final_summary_2026-06-05.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))

parent_master_path = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_2026-06-05.csv"
child_final_path = CURATED_DIR / "PENGINAPAN_CHILD_LISTINGS_FINAL_2026-06-05.csv"

parent_master_df = pd.read_csv(parent_master_path, dtype=str, keep_default_na=False)
child_final_df = pd.read_csv(child_final_path, dtype=str, keep_default_na=False)

display(
    pd.DataFrame(
        {
            "metric": [
                "Parent master rows",
                "Child listing rows",
                "Accepted child",
                "Child tanpa parent final",
                "Parent dengan child final",
            ],
            "value": [
                summary["parent_master_rows"],
                summary["child_listings_rows"],
                summary["child_listing_status_counts"].get("accepted_parent", 0),
                summary["child_listing_status_counts"].get("child_without_final_parent", 0),
                summary["parent_with_child_count"],
            ],
        }
    )
)
display(child_final_df[["child_penginapan_id", "child_name", "parent_penginapan_id", "parent_name", "relation_status"]].head(30))
"""
        ),
        md(
            """
### Keputusan Tahap B

| Catatan |
|---|
| Parent master sudah terpisah dari child listing. |
| 41 child tanpa parent final tetap ditahan sebagai child, bukan dipromosikan ke parent. |
"""
        ),
        md(
            """
## Tahap C - Validasi Pemisahan

| Catatan |
|---|
| Yang dicek: accepted child tidak boleh muncul di parent master dan target review. |
"""
        ),
        code(
            """
validation_path = CURATED_DIR / "penginapan_parent_master_final_validation_2026-06-05.json"
validation = json.loads(validation_path.read_text(encoding="utf-8"))

display(
    pd.DataFrame(
        {
            "metric": [
                "Validation gate",
                "Accepted child in parent master",
                "Any child in parent master",
                "Child in review targets",
                "Child without final parent",
            ],
            "value": [
                validation["gate"],
                validation["accepted_child_in_parent_master"],
                validation["any_child_in_parent_master"],
                validation["child_in_review_targets"],
                validation["child_without_final_parent"],
            ],
        }
    )
)
display(pd.DataFrame(validation["warnings"]))
"""
        ),
        md(
            """
### Keputusan Tahap C

| Catatan |
|---|
| Validasi lolos dengan warning. Warning-nya wajar karena 41 child belum punya parent final. |
| Tidak ada child yang masuk parent master atau target review. |
"""
        ),
        md(
            """
## Tahap D - Target Scraping Review dari Parent Master

| Catatan |
|---|
| Target review dibuat dari parent master, bukan dari child listing. |
| Nama yang masih terlihat seperti unit diberi flag agar dicek saat batch test. |
"""
        ),
        code(
            """
review_targets_path = CURATED_DIR / "PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv"
review_targets_df = pd.read_csv(review_targets_path, dtype=str, keep_default_na=False)

display(
    pd.DataFrame(
        {
            "metric": [
                "Review target rows",
                "Target flagged detail-name",
                "Missing rating/review",
                "Low review confidence",
                "Medium review confidence",
                "High review confidence",
            ],
            "value": [
                len(review_targets_df),
                summary["review_target_detail_listing_flag_count"],
                summary["review_target_priority_counts"].get("missing_rating_or_review", 0),
                summary["review_target_priority_counts"].get("low_review_confidence", 0),
                summary["review_target_priority_counts"].get("medium_review_confidence", 0),
                summary["review_target_priority_counts"].get("high_review_confidence", 0),
            ],
        }
    )
)
display(review_targets_df[["review_target_id", "penginapan_id", "name", "property_type", "review_scrape_priority", "name_looks_detail_listing", "target_review_note"]].head(40))
"""
        ),
        md(
            """
### Keputusan Tahap D

| Catatan |
|---|
| Target review sudah bisa dipakai untuk batch test kecil dulu. |
| Target dengan flag detail-name jangan langsung dipercaya; cek hasil match Google Maps saat test. |
"""
        ),
    ]


def update_notebook() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb.cells = [cell for cell in nb.cells if TAG not in cell.get("metadata", {}).get("tags", [])]
    nb.cells.extend(build_section())
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"updated_notebook={NOTEBOOK_PATH}")
    print(f"cells={len(nb.cells)}")


if __name__ == "__main__":
    update_notebook()
