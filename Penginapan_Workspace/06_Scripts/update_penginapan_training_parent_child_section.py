from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT / "Penginapan_Workspace"
NOTEBOOK_PATH = WORKSPACE / "03_Notebooks" / "penginapan_training.ipynb"

TAG = "penginapan_parent_child_candidate_2026_06_05"


def md(source: str):
    cell = new_markdown_cell(source.strip())
    cell.metadata["tags"] = [TAG, "decision-documentation"]
    return cell


def code(source: str):
    cell = new_code_cell(source.strip())
    cell.metadata["tags"] = [TAG, "audit-code"]
    return cell


def replace_old_priority_language(cells: list) -> list:
    updated = []
    for cell in cells:
        source = "".join(cell.get("source", []))
        if source.startswith("## Tahap 9 - Prioritas Penyesuaian P0/P1/P2"):
            cell["source"] = [
                line + "\n"
                for line in """
## Tahap 9 - Ringkasan Temuan Actionable

**Tujuan kecil:** membedakan temuan yang memblokir penggunaan data dari temuan yang masih bisa dilanjutkan dengan review atau caveat.

Istilah yang dipakai pada notebook ini:

- **ERROR aktif:** harus diperbaiki sebelum dataset dipakai.
- **Review utama:** penting untuk struktur ranking, duplicate review, dan parent-child.
- **Caveat:** data boleh dipakai, tetapi sistem tidak boleh mengklaim field yang kosong.
""".strip().split("\n")
            ]
        elif source.startswith("adjustment_df = pd.read_csv(paths[\"adjustment_queue\"]"):
            cell["source"] = [
                line + "\n"
                for line in """
adjustment_df = pd.read_csv(paths["adjustment_queue"], dtype=str, keep_default_na=False)
manual_queue_df = pd.read_csv(paths["manual_queue"], dtype=str, keep_default_na=False)

actionable_summary = pd.DataFrame(
    {
        "metric": [
            "Manual review queue rows",
            "Actionable queue rows",
            "Rows terkait possible duplicate",
            "Rows terkait room-level listing",
        ],
        "value": [
            len(manual_queue_df),
            len(adjustment_df),
            int(adjustment_df["finding_codes"].str.contains("POSSIBLE_DUPLICATE_NAME_COORD", na=False).sum()),
            int(adjustment_df["finding_codes"].str.contains("ROOM_LEVEL_LISTING", na=False).sum()),
        ],
    }
)

display(actionable_summary)
display(adjustment_df[["penginapan_id", "name", "finding_codes", "recommended_next_step"]].head(40))
""".strip().split("\n")
            ]
            cell["outputs"] = []
            cell["execution_count"] = None
        elif source.startswith("### Keputusan: Fokus berikutnya adalah P1 duplicate review"):
            cell["source"] = [
                line + "\n"
                for line in """
### Keputusan: Fokus berikutnya adalah duplicate review dan parent-child

**Bukti dari output sebelumnya**

- Tidak ada ERROR aktif yang memblokir dataset.
- Temuan actionable masih didominasi possible duplicate dan room-level listing.

**Keputusan snapshot 2026-06-05**

Dataset boleh dilanjutkan ke entity resolution candidate. Temuan duplicate dan room-level tidak diselesaikan dengan penghapusan massal.

**Langkah berikutnya**

Buat file candidate mapping: possible duplicate review, room-level listing, dan parent-child mapping candidate.

> Jika output cell sebelumnya berubah saat notebook dijalankan ulang, keputusan ini wajib ditinjau ulang sebelum proses dilanjutkan.
""".strip().split("\n")
            ]
        else:
            replacements = {
                "9. Menentukan prioritas P0/P1/P2.": "9. Menentukan temuan actionable tanpa memakai label prioritas angka sebagai struktur keputusan.",
                "Kasus ini harus masuk P1/P2 review dan parent-child preparation.": "Kasus ini harus masuk review lanjutan dan parent-child preparation.",
                "Pisahkan tindakan P0/P1/P2 agar pekerjaan berikutnya terarah.": "Pisahkan temuan actionable agar pekerjaan berikutnya terarah.",
                "| Automated audit | `PASS_WITH_WARNINGS`; tidak ada P0/error aktif |": "| Automated audit | `PASS_WITH_WARNINGS`; tidak ada ERROR aktif |",
            }
            new_source = source
            for old, new in replacements.items():
                new_source = new_source.replace(old, new)
            if new_source != source:
                cell["source"] = [line + "\n" for line in new_source.rstrip("\n").split("\n")]
        updated.append(cell)
    return updated


def build_section() -> list:
    return [
        md(
            """
## Fase B - Entity Resolution Candidate Penginapan

Fase ini menyiapkan struktur awal parent-child untuk penginapan.

Output fase ini **belum final**. Semua relasi masih berstatus candidate mapping agar bisa direview sebelum dipakai untuk ranking atau target scraping review.
"""
        ),
        md(
            """
## Tahap A - Kunci Snapshot Data Saat Ini

**Tujuan kecil:** memastikan candidate saat ini menjadi basis kerja dan tidak dibangun ulang dari JSON.
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

candidate_path = CURATED_DIR / "PENGINAPAN_CANONICAL_CANDIDATE_BANDUNG_RAYA_2026-06-02.csv"
candidate_df = pd.read_csv(candidate_path, dtype=str, keep_default_na=False)

snapshot_table = pd.DataFrame(
    {
        "metric": [
            "Candidate rows",
            "Property types",
            "Room-level listing rows",
            "Region valid rows",
        ],
        "value": [
            len(candidate_df),
            candidate_df["property_type"].nunique(),
            int(candidate_df["property_type"].eq("room_level_listing").sum()),
            int(candidate_df["region_validation_label"].eq("bandung_raya_valid").sum()),
        ],
    }
)

display(snapshot_table)
display(candidate_df["property_type"].value_counts().rename_axis("property_type").reset_index(name="rows"))
"""
        ),
        md(
            """
### Keputusan Tahap A

Candidate saat ini dipakai sebagai snapshot kerja. Data tidak di-rebuild dari JSON pada tahap ini karena kita sedang menyiapkan struktur entity resolution, bukan mengulang ingest data.
"""
        ),
        md(
            """
## Tahap B - Audit Possible Duplicate

**Tujuan kecil:** melihat penginapan yang masih berpotensi dobel berdasarkan nama ternormalisasi dan koordinat rounded.
"""
        ),
        code(
            """
parent_child_run = subprocess.run(
    [
        sys.executable,
        str(SCRIPT_DIR / "build_penginapan_parent_child_candidates.py"),
    ],
    check=True,
    capture_output=True,
    text=True,
)
print(parent_child_run.stdout.strip())

summary_path = CURATED_DIR / "penginapan_parent_child_candidate_summary_2026-06-05.json"
duplicate_review_path = CURATED_DIR / "PENGINAPAN_POSSIBLE_DUPLICATE_REVIEW_2026-06-05.csv"

parent_child_summary = json.loads(summary_path.read_text(encoding="utf-8"))
duplicate_review_df = pd.read_csv(duplicate_review_path, dtype=str, keep_default_na=False)

display(
    pd.DataFrame(
        {
            "metric": ["Possible duplicate rows", "Possible duplicate groups"],
            "value": [
                parent_child_summary["possible_duplicate_rows"],
                parent_child_summary["possible_duplicate_groups"],
            ],
        }
    )
)
display(duplicate_review_df["group_review_type"].value_counts().rename_axis("group_review_type").reset_index(name="rows"))
display(duplicate_review_df.head(30))
"""
        ),
        md(
            """
### Keputusan Tahap B

Possible duplicate tidak digabung otomatis. File ini dipakai sebagai daftar review karena nama dan koordinat mirip belum selalu berarti properti yang sama.
"""
        ),
        md(
            """
## Tahap C - Audit Room-Level Listing

**Tujuan kecil:** memisahkan listing kamar/unit agar tidak ikut ranking sebagai properti utama.
"""
        ),
        code(
            """
room_level_path = CURATED_DIR / "PENGINAPAN_ROOM_LEVEL_LISTINGS_2026-06-05.csv"
room_level_df = pd.read_csv(room_level_path, dtype=str, keep_default_na=False)

display(
    pd.DataFrame(
        {
            "metric": [
                "Room-level listing rows",
                "Rows with duplicate group",
                "Rows name looks room/unit",
            ],
            "value": [
                len(room_level_df),
                int(room_level_df["possible_duplicate_group_id"].ne("").sum()),
                int(room_level_df["name_looks_room_or_unit"].eq("True").sum()),
            ],
        }
    )
)
display(room_level_df.head(40))
"""
        ),
        md(
            """
### Keputusan Tahap C

Room-level listing tetap disimpan, tetapi disiapkan sebagai child candidate. Data ini tidak boleh dipakai sebagai daftar properti utama untuk ranking.
"""
        ),
        md(
            """
## Tahap D - Parent-Child Mapping Candidate

**Tujuan kecil:** mencari kandidat parent untuk room-level listing dengan aturan konservatif.

Catatan: confidence tinggi tetap belum final. Ini baru kandidat untuk direview.
"""
        ),
        code(
            """
mapping_path = CURATED_DIR / "PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_2026-06-05.csv"
mapping_df = pd.read_csv(mapping_path, dtype=str, keep_default_na=False)

display(
    pd.DataFrame(
        {
            "metric": [
                "Mapping candidate rows",
                "Child with parent candidate",
                "Child without parent candidate",
            ],
            "value": [
                len(mapping_df),
                mapping_df[mapping_df["parent_candidate_id"].ne("")]["child_penginapan_id"].nunique(),
                mapping_df[mapping_df["parent_candidate_id"].eq("")]["child_penginapan_id"].nunique(),
            ],
        }
    )
)
display(mapping_df["confidence_label"].value_counts().rename_axis("confidence_label").reset_index(name="rows"))
display(
    mapping_df[
        [
            "child_penginapan_id",
            "child_name",
            "parent_candidate_id",
            "parent_candidate_name",
            "confidence_score",
            "confidence_label",
            "match_basis",
            "decision_recommendation",
        ]
    ].head(60)
)
"""
        ),
        md(
            """
### Keputusan Tahap D

Relasi parent-child belum difinalkan. Baris dengan parent candidate dapat direview lebih dulu, sedangkan child tanpa parent tetap ditahan sebagai child candidate tanpa parent.
"""
        ),
        md(
            """
## Tahap E - Verifikasi Output Fase B

**Tujuan kecil:** memastikan semua file hasil entity resolution candidate sudah tersedia.
"""
        ),
        code(
            """
phase_b_outputs = {
    "possible_duplicate_review": CURATED_DIR / "PENGINAPAN_POSSIBLE_DUPLICATE_REVIEW_2026-06-05.csv",
    "room_level_listings": CURATED_DIR / "PENGINAPAN_ROOM_LEVEL_LISTINGS_2026-06-05.csv",
    "parent_child_mapping_candidate": CURATED_DIR / "PENGINAPAN_PARENT_CHILD_MAPPING_CANDIDATE_2026-06-05.csv",
    "summary": CURATED_DIR / "penginapan_parent_child_candidate_summary_2026-06-05.json",
}

artifact_rows = []
for name, path in phase_b_outputs.items():
    rows = None
    columns = None
    if path.exists() and path.suffix == ".csv":
        temp = pd.read_csv(path, dtype=str, keep_default_na=False)
        rows = len(temp)
        columns = len(temp.columns)
    artifact_rows.append({"artifact": name, "exists": path.exists(), "rows": rows, "columns": columns, "path": str(path)})

display(pd.DataFrame(artifact_rows))
"""
        ),
        md(
            """
### Keputusan Tahap E

Fase B selesai sebagai candidate mapping. Langkah berikutnya adalah review relasi parent-child yang sudah ada kandidatnya, lalu baru membuat target scraping review dari properti utama.
"""
        ),
    ]


def update_notebook() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    cells = [cell for cell in nb.cells if TAG not in cell.get("metadata", {}).get("tags", [])]
    cells = replace_old_priority_language(cells)
    cells.extend(build_section())
    nb.cells = cells
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"updated_notebook={NOTEBOOK_PATH}")
    print(f"cells={len(nb.cells)}")


if __name__ == "__main__":
    update_notebook()
