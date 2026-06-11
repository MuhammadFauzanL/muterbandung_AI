from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"

SECTION_MARKER = "## Fase E - Keputusan Lanjutan untuk 87 Data"


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

audit_87 = pd.read_csv(CURATED_DIR / "PENGINAPAN_REVIEW_TARGETS_NEEDS_REVIEW_AUDIT_2026-06-05.csv")
audit_counts = (
    audit_87["audit_recommendation"]
    .value_counts(dropna=False)
    .rename_axis("audit_recommendation")
    .reset_index(name="jumlah")
)

print("Jumlah keputusan awal dari 87 data")
print(audit_counts.to_string(index=False))
'''
    output_a = run_code(code_a, namespace)

    code_b = r'''
summary_path = CURATED_DIR / "penginapan_needs_review_decision_split_summary_2026-06-05.json"
with summary_path.open(encoding="utf-8") as handle:
    decision_summary = json.load(handle)

split_table = pd.DataFrame(
    [
        {"kelompok": "child_parent_candidate", "jumlah": decision_summary["child_parent_candidate_rows"]},
        {"kelompok": "manual_check", "jumlah": decision_summary["manual_check_rows"]},
        {"kelompok": "held_low_priority", "jumlah": decision_summary["held_low_priority_rows"]},
    ]
)

output_table = pd.DataFrame(
    [
        {"file": Path(path).name, "rows": pd.read_csv(path).shape[0]}
        for path in decision_summary["outputs"].values()
    ]
)

print("Hasil split 87 data")
print(split_table.to_string(index=False))
print("\nFile output")
print(output_table.to_string(index=False))
'''
    output_b = run_code(code_b, namespace)

    code_c = r'''
files = {
    "child_parent_candidate": CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_20_CHILD_PARENT_CANDIDATE_2026-06-05.csv",
    "manual_check": CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_9_MANUAL_CHECK_2026-06-05.csv",
    "held_low_priority": CURATED_DIR / "PENGINAPAN_NEEDS_REVIEW_58_HELD_LOW_PRIORITY_2026-06-05.csv",
}

ids = {}
for key, path in files.items():
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    ids[key] = set(df["review_target_id"])
    print(f"{key}: rows={len(df)}, unique_ids={df['review_target_id'].nunique()}")

overlap = 0
keys = list(ids)
for index, left in enumerate(keys):
    for right in keys[index + 1:]:
        overlap += len(ids[left] & ids[right])

print(f"total_rows={sum(len(value) for value in ids.values())}")
print(f"overlap_review_target_id={overlap}")
'''
    output_c = run_code(code_c, namespace)

    new_cells = [
        markdown_cell(
            """
## Fase E - Keputusan Lanjutan untuk 87 Data

Bagian ini mencatat keputusan setelah 87 data abu-abu dipisahkan. Tujuannya agar 58 data tidak hilang, tapi juga tidak menahan proses scraping utama.
"""
        ),
        markdown_cell(
            """
### Proses A - Baca Hasil Audit 87 Data

Tujuan kecil: lihat ulang jumlah data berdasarkan rekomendasi audit.
"""
        ),
        code_cell(code_a, next_count, output_a),
        markdown_cell(
            """
### Keputusan Proses A

Output membagi 87 data menjadi tiga arah: kandidat child-parent, cek manual, dan held low priority. Data ini tidak masuk scraping massal dulu.
"""
        ),
        markdown_cell(
            """
### Proses B - Pisahkan Keputusan 20 / 9 / 58

Tujuan kecil: buat file kerja terpisah agar tindak lanjutnya tidak tercampur.
"""
        ),
        code_cell(code_b, next_count + 1, output_b),
        markdown_cell(
            """
### Keputusan Proses B

20 data masuk kandidat relasi child-parent. 9 data menunggu cek manual. 58 data ditahan sebagai low priority, bukan dihapus.
"""
        ),
        markdown_cell(
            """
### Proses C - Validasi Split

Tujuan kecil: pastikan total tetap 87 dan tidak ada `review_target_id` yang masuk dua file.
"""
        ),
        code_cell(code_c, next_count + 2, output_c),
        markdown_cell(
            """
### Keputusan Proses C

Validasi diterima. Total kembali ke 87 dan tidak ada overlap, jadi keputusan 20 / 9 / 58 bisa dilacak dengan aman.
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
