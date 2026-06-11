from __future__ import annotations

import copy
import io
import json
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"

SECTION_MARKER = "## Fase D - Split Target Review Sebelum Scraping"


def source_lines(text: str) -> list[str]:
    return text.strip("\n").splitlines(keepends=True)


def markdown_cell(text: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source_lines(text),
    }


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
import pandas as pd

CURATED_DIR = Path("../02_Curated")
if not CURATED_DIR.exists():
    CURATED_DIR = Path("Penginapan_Workspace/02_Curated")

targets = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_SCRAPE_TARGETS_PARENT_MASTER_2026-06-05.csv")
flagged = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_FLAGGED_DETAIL_NAME_2026-06-05.csv")

summary_a = pd.DataFrame(
    [
        {"metric": "total_review_targets", "jumlah": len(targets)},
        {"metric": "flagged_detail_name_rows", "jumlah": len(flagged)},
    ]
)
flag_group_counts = (
    flagged["flag_group"]
    .value_counts(dropna=False)
    .rename_axis("flag_group")
    .reset_index(name="jumlah")
)

print("Ringkasan target review")
print(summary_a.to_string(index=False))
print("\nJumlah per flag_group")
print(flag_group_counts.to_string(index=False))
'''
    output_a = run_code(code_a, namespace)

    code_b = r'''
import json

summary_path = CURATED_DIR / "penginapan_review_targets_split_summary_2026-06-05.json"
with summary_path.open(encoding="utf-8") as handle:
    split_summary = json.load(handle)

summary_b = pd.DataFrame(
    [
        {"kelompok": "ready", "jumlah": split_summary["ready_rows"]},
        {"kelompok": "held_child", "jumlah": split_summary["held_child_rows"]},
        {"kelompok": "needs_review", "jumlah": split_summary["needs_review_rows"]},
    ]
)

output_files = pd.DataFrame(
    [
        {
            "file": Path(path).name,
            "rows": pd.read_csv(path).shape[0],
        }
        for path in split_summary["outputs"].values()
    ]
)

print("Hasil split target review")
print(summary_b.to_string(index=False))
print("\nFile output")
print(output_files.to_string(index=False))
'''
    output_b = run_code(code_b, namespace)

    code_c = r'''
needs_review_audit = pd.read_csv(
    CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_AUDIT_2026-06-05.csv"
)

audit_counts = (
    needs_review_audit["audit_recommendation"]
    .value_counts(dropna=False)
    .rename_axis("audit_recommendation")
    .reset_index(name="jumlah")
)
sample_cols = [
    "review_target_id",
    "name",
    "property_type",
    "flag_group",
    "audit_recommendation",
    "parent_candidate_name",
    "parent_candidate_score",
]

print("Ringkasan audit 87 data")
print(audit_counts.to_string(index=False))
print("\nContoh kandidat dari audit")
print(needs_review_audit[sample_cols].head(10).to_string(index=False))
'''
    output_c = run_code(code_c, namespace)
    audit_count_map = dict(
        zip(
            namespace["audit_counts"]["audit_recommendation"],
            namespace["audit_counts"]["jumlah"],
        )
    )
    candidate_child_count = int(audit_count_map.get("candidate_child_to_parent", 0))
    manual_check_count = int(audit_count_map.get("needs_manual_check", 0))
    unclear_count = int(audit_count_map.get("candidate_standalone_or_unclear", 0))

    new_cells = [
        markdown_cell(
            """
## Fase D - Split Target Review Sebelum Scraping

Bagian ini memakai **Format Notebook Audit Bertahap**. Tujuannya sederhana: target scraping review dipisahkan dulu agar kamar/unit tidak ikut discrape sebagai parent.
"""
        ),
        markdown_cell(
            """
### Proses A - Audit Kelompok Flagged

Tujuan kecil: cek ulang berapa target review yang namanya masih terlihat seperti kamar, unit, atau detail listing.
"""
        ),
        code_cell(code_a, next_count, output_a),
        markdown_cell(
            """
### Keputusan Proses A

Output menunjukkan ada 1.518 target review dan 387 nama yang terkena flag detail. Dua kelompok sudah jelas ditahan sebagai child: `hold_room_label` 35 data dan `hold_unit_or_bedroom_listing` 265 data. Dua kelompok lain masih perlu dicek ringan: 66 data villa/house dan 21 data detail lain.
"""
        ),
        markdown_cell(
            """
### Proses B - Split Target Review Awal

Tujuan kecil: memisahkan target menjadi `ready`, `held_child`, dan `needs_review` berdasarkan kelompok flagged.
"""
        ),
        code_cell(code_b, next_count + 1, output_b),
        markdown_cell(
            """
### Keputusan Proses B

Split awal diterima. Ada 1.131 target yang aman untuk scraping review, 300 data ditahan sebagai child/detail, dan 87 data tidak dipaksa masuk parent karena masih abu-abu.
"""
        ),
        markdown_cell(
            """
### Proses C - Audit 87 Data Abu-Abu

Tujuan kecil: melihat apakah 87 data abu-abu punya kandidat parent dari dataset saat ini, memakai nama dan kandidat koordinat yang tersedia.
"""
        ),
        code_cell(code_c, next_count + 2, output_c),
        markdown_cell(
            f"""
### Keputusan Proses C

Dari 87 data abu-abu, {candidate_child_count} terlihat punya kandidat parent yang cukup kuat, {manual_check_count} masih perlu cek manual, dan {unclear_count} belum punya kandidat parent yang kuat. Untuk saat ini 87 data ini tetap tidak masuk target scraping massal sampai diputuskan lebih lanjut.
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
