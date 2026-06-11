import json
import subprocess
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_output


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
PHASE_TITLE = "## Fase J - Apartment Sebagai Secondary Option"


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
            + "\n\nTujuan: apartment tetap disimpan, tapi tidak menjadi pilihan utama untuk query umum."
        ),
        code_cell(
            r"""
import pandas as pd

path = "Penginapan_Workspace/02_Curated/PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10_DRIVE_FULL_REVIEW.csv"
df = pd.read_csv(path)
counts = df["property_type"].value_counts()
print("total_rows:", len(df))
print(counts.to_string())
print("apartment_share:", round(counts.get("apartment", 0) / len(df) * 100, 2), "%")
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: apartment cukup besar, jadi tidak dihapus. Apartment diturunkan sebagai opsi kedua supaya rekomendasi umum tetap terasa seperti penginapan utama."
        ),
        code_cell(
            r"""
from Scripts.penginapan_recommender import PenginapanRecommender

engine = PenginapanRecommender()
tests = [
    ("query_umum", "murah dekat alun alun bandung"),
    ("query_apartment", "apartemen studio murah dekat alun alun bandung"),
]

for label, query in tests:
    result = engine.recommend(query=query, user_lat=-6.9219, user_lon=107.6069, top_k=5)
    print("\n" + label + ":", query)
    for item in result["recommendations"]:
        print(
            item["rank"],
            item["property_type"],
            item["name"],
            item["final_score"],
            item["score_breakdown"]["property_type_priority_score"],
        )
""".strip()
        ),
        new_markdown_cell(
            "Keputusan: query umum tidak didominasi apartment. Kalau user memang mencari apartment/studio, penalti dilepas dan apartment tampil normal."
        ),
    ]

    nb.cells.extend(new_cells)
    nbformat.write(nb, NOTEBOOK_PATH)
    print(json.dumps({"notebook": str(NOTEBOOK_PATH), "added_phase": PHASE_TITLE, "cell_count": len(nb.cells)}, indent=2))


if __name__ == "__main__":
    main()
