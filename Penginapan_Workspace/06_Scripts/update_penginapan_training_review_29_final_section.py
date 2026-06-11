from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
SECTION_MARKER = "## Fase F - Keputusan Final 29 Data"


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

    code = r'''
from pathlib import Path
import json
import pandas as pd

CURATED_DIR = Path("../02_Curated")
if not CURATED_DIR.exists():
    CURATED_DIR = Path("Penginapan_Workspace/02_Curated")

summary_path = CURATED_DIR / "penginapan_review_29_final_decision_summary_2026-06-05.json"
with summary_path.open(encoding="utf-8") as handle:
    final_29_summary = json.load(handle)

final_29 = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_29_FINAL_DECISION_2026-06-05.csv")

summary_table = pd.DataFrame(
    [
        {"kelompok": "child_parent_relation", "jumlah": final_29_summary["child_parent_rows"]},
        {"kelompok": "parent_ready", "jumlah": final_29_summary["parent_ready_rows"]},
        {"kelompok": "held_drop", "jumlah": final_29_summary["held_drop_rows"]},
        {"kelompok": "needs_more_check", "jumlah": final_29_summary["needs_more_check_rows"]},
    ]
)

sample_cols = ["review_target_id", "name", "parent_candidate_name", "final_decision", "final_group"]
print("Ringkasan keputusan final 29 data")
print(summary_table.to_string(index=False))
print("\nContoh data final")
print(final_29[sample_cols].head(8).to_string(index=False))
print(f"\nfile_final={Path(final_29_summary['final_decision_path']).name}")
'''
    output = run_code(code, {})

    new_cells = [
        markdown_cell(
            """
## Fase F - Keputusan Final 29 Data

Hasil review 29 data sudah ditutup. Bagian ini hanya mencatat keputusan finalnya agar alur parent/child tetap jelas.
"""
        ),
        markdown_cell(
            """
### Proses A - Catat Keputusan Final

Tujuan kecil: baca hasil final 29 data dan cek jumlah tiap keputusan.
"""
        ),
        code_cell(code, next_count, output),
        markdown_cell(
            """
### Keputusan Proses A

Keputusan final diterima. 19 data menjadi child-parent, 9 data tetap parent-ready, dan 1 data dikeluarkan dari jalur utama. Tidak ada data yang masih `needs_more_check`.
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
