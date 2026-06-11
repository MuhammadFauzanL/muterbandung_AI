from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
SECTION_MARKER = "## Fase G - Pre-Scraping Target Review Final"


def source_lines(text: str) -> list[str]:
    return text.strip("\n").splitlines(keepends=True)


def markdown_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source_lines(text)}


def code_cell(text: str, execution_count: int, output_text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": execution_count,
        "metadata": {},
        "outputs": [
            {
                "name": "stdout",
                "output_type": "stream",
                "text": source_lines(output_text if output_text.endswith("\n") else output_text + "\n"),
            }
        ],
        "source": source_lines(text),
    }


def run_code(source: str, namespace: dict) -> str:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        exec(source, namespace)
    return buffer.getvalue()


def remove_existing_section(cells: list[dict]) -> list[dict]:
    for index, cell in enumerate(cells):
        if cell.get("cell_type") == "markdown" and SECTION_MARKER in "".join(cell.get("source", [])):
            return cells[:index]
    return cells


def main() -> None:
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    notebook["cells"] = remove_existing_section(notebook["cells"])

    execution_counts = [
        cell.get("execution_count", 0)
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code" and isinstance(cell.get("execution_count"), int)
    ]
    next_count = (max(execution_counts) if execution_counts else 0) + 1
    namespace: dict = {}

    code_a = r'''
from pathlib import Path
import json
import pandas as pd

CURATED_DIR = Path("../02_Curated")
if not CURATED_DIR.exists():
    CURATED_DIR = Path("Penginapan_Workspace/02_Curated")

summary_path = CURATED_DIR / "penginapan_review_targets_final_summary_2026-06-05.json"
with summary_path.open(encoding="utf-8") as handle:
    final_target_summary = json.load(handle)

apply_table = pd.DataFrame(
    [
        {"metric": "initial_ready", "jumlah": final_target_summary["input_rows"]["initial_ready"]},
        {"metric": "final_29_parent_ready_added", "jumlah": final_target_summary["decision_rows"]["final_29_parent_ready"]},
        {"metric": "final_ready", "jumlah": final_target_summary["final_ready_rows"]},
        {"metric": "final_excluded", "jumlah": final_target_summary["final_excluded_rows"]},
    ]
)

excluded_table = (
    pd.DataFrame(
        final_target_summary["excluded_group_counts"].items(),
        columns=["excluded_group", "jumlah"],
    )
    .sort_values("excluded_group")
)

print("Ringkasan apply keputusan final")
print(apply_table.to_string(index=False))
print("\nExcluded group")
print(excluded_table.to_string(index=False))
'''
    output_a = run_code(code_a, namespace)

    code_b = r'''
final_ready = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_READY_2026-06-05.csv", dtype=str, keep_default_na=False)
final_excluded = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FINAL_EXCLUDED_2026-06-05.csv", dtype=str, keep_default_na=False)

ready_ids = set(final_ready["review_target_id"])
excluded_ids = set(final_excluded["review_target_id"])
overlap = len(ready_ids & excluded_ids)
duplicate_ready = final_ready["review_target_id"].duplicated().sum()
duplicate_excluded = final_excluded["review_target_id"].duplicated().sum()

validation_table = pd.DataFrame(
    [
        {"cek": "ready_rows", "hasil": len(final_ready)},
        {"cek": "excluded_rows", "hasil": len(final_excluded)},
        {"cek": "ready_excluded_overlap", "hasil": overlap},
        {"cek": "duplicate_ready_id", "hasil": int(duplicate_ready)},
        {"cek": "duplicate_excluded_id", "hasil": int(duplicate_excluded)},
    ]
)

print("Validasi target final")
print(validation_table.to_string(index=False))
'''
    output_b = run_code(code_b, namespace)

    code_c = r'''
test_batch = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_TEST_BATCH_30_2026-06-05.csv", dtype=str, keep_default_na=False)
sample_cols = [
    "review_target_id",
    "name",
    "property_type",
    "review_scrape_priority",
    "google_maps_search_query",
]
sample_cols = [col for col in sample_cols if col in test_batch.columns]

print(f"test_batch_rows={len(test_batch)}")
print("\nContoh target batch test")
print(test_batch[sample_cols].head(10).to_string(index=False))
print("\nfile_batch=PENGINAPAN_REVIEW_TARGETS_TEST_BATCH_30_2026-06-05.csv")
'''
    output_c = run_code(code_c, namespace)

    new_cells = [
        markdown_cell(
            """
## Fase G - Pre-Scraping Target Review Final

Bagian ini menyiapkan target scraping review final. Target massal belum dijalankan; kita buat batch test kecil dulu.
"""
        ),
        markdown_cell(
            """
### Proses A - Apply Keputusan Final

Tujuan kecil: terapkan keputusan final 29 data ke target review.
"""
        ),
        code_cell(code_a, next_count, output_a),
        markdown_cell(
            """
### Keputusan Proses A

Target ready final menjadi 1.140 data. Data yang ditahan berjumlah 378, terdiri dari child/detail, low priority, child-parent final, dan satu held/drop.
"""
        ),
        markdown_cell(
            """
### Proses B - Validasi Ready dan Excluded

Tujuan kecil: pastikan target ready final tidak bercampur dengan data excluded.
"""
        ),
        code_cell(code_b, next_count + 1, output_b),
        markdown_cell(
            """
### Keputusan Proses B

Validasi diterima. Tidak ada overlap antara ready dan excluded, dan tidak ada ID ganda di file target final.
"""
        ),
        markdown_cell(
            """
### Proses C - Buat Batch Test 30 Target

Tujuan kecil: ambil batch kecil untuk cek hasil scraping sebelum jalan massal.
"""
        ),
        code_cell(code_c, next_count + 2, output_c),
        markdown_cell(
            """
### Keputusan Proses C

Batch test 30 target sudah dibuat. Scraping sebaiknya dimulai dari file ini dulu, bukan langsung dari semua target ready.
"""
        ),
    ]

    notebook["cells"].extend(new_cells)
    NOTEBOOK.write_text(json.dumps(notebook, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"updated_notebook={NOTEBOOK}")
    print(f"added_cells={len(new_cells)}")
    print(f"new_total_cells={len(notebook['cells'])}")


if __name__ == "__main__":
    main()
