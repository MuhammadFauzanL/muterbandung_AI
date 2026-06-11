from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
PENGINAPAN_WORKSPACE = ROOT / "Penginapan_Workspace"
NOTEBOOK_PATH = ROOT / "Notebooks" / "wisata_training.ipynb"
SUMMARY_PATH = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_canonical_summary_2026-05-29.json"
VALIDATION_PATH = PENGINAPAN_WORKSPACE / "02_Curated" / "hotel_canonical_validation_results_2026-05-29.json"

TAG = "hotel_canonical_pipeline_2026_05_29"


def source_lines(text: str) -> list[str]:
    return [f"{line}\n" for line in text.strip("\n").split("\n")]


def new_cell(cell_type: str, source: str) -> dict:
    cell = {
        "cell_type": cell_type,
        "id": uuid4().hex[:8],
        "metadata": {"tags": [TAG]},
        "source": source_lines(source),
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
    return cell


def main() -> None:
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

    cells = notebook.get("cells", [])
    notebook["cells"] = [
        cell
        for cell in cells
        if TAG not in cell.get("metadata", {}).get("tags", [])
    ]

    validation_summary = validation["summary"]
    property_segments = ", ".join(
        f"{name}: {count}"
        for name, count in summary["property_segment_counts"].items()
    )
    quality_flags = ", ".join(
        f"{name}: {count}"
        for name, count in summary["quality_flags"].items()
    )
    confidence = ", ".join(
        f"{name}: {count}"
        for name, count in summary["review_confidence_counts"].items()
    )

    notebook["cells"].extend(
        [
            new_cell(
                "markdown",
                f"""
# Hotel canonical dataset foundation (2026-05-29)

Bagian ini menyimpan pekerjaan pondasi hotel sebelum masuk ke LLM atau model rekomendasi. Dataset hotel tidak dibuang walaupun berisi hotel, guest house, villa, apartment, vacation rental, dan listing level kamar. Semua dipertahankan, tetapi diberi `property_segment` agar recommender bisa memfilter sesuai kebutuhan user.

Output utama:
- `Penginapan_Workspace/02_Curated/HOTEL_CANONICAL_CIMAHI_2026-05-29.csv`
- `Penginapan_Workspace/02_Curated/hotel_canonical_summary_2026-05-29.json`
- `Penginapan_Workspace/02_Curated/hotel_canonical_validation_results_2026-05-29.json`
- `Penginapan_Workspace/04_Dokumentasi/HOTEL_CANONICAL_PIPELINE_2026-05-29.md`
- `Penginapan_Workspace/04_Dokumentasi/HOTEL_VALIDATION_REPORT_2026-05-29.md`

Status terakhir:
- Baris: {summary["row_count"]}
- Kolom: {summary["column_count"]}
- Validation gate: {validation_summary["gate_status"]}
- Error: {validation_summary["error_count"]}
- Warning: {validation_summary["warning_count"]}
- Segment properti: {property_segments}
- Quality flags terisi: {quality_flags}
- Review confidence: {confidence}

Catatan penting: `rating_sentiment_score` dan `adjusted_rating_sentiment_score` adalah rating-based sentiment, bukan NLP komentar. Ini dipakai karena dataset hotel saat ini belum punya raw review comment yang cukup untuk pipeline NLP seperti wisata.
""",
            ),
            new_cell(
                "code",
                """
# Rebuild canonical hotel dataset dan jalankan validation pipeline.
# Jalankan sel ini dari root project PIJAK atau dari folder Notebooks.
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "build_hotel_canonical_dataset.py")],
    check=True,
)
subprocess.run(
    [sys.executable, str(PROJECT_ROOT / "Penginapan_Workspace" / "06_Scripts" / "validate_hotel_canonical_dataset.py")],
    check=True,
)
""",
            ),
            new_cell(
                "code",
                """
# Ringkasan cepat output hotel canonical.
import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path.cwd().resolve()
while PROJECT_ROOT.name != "PIJAK" and PROJECT_ROOT.parent != PROJECT_ROOT:
    PROJECT_ROOT = PROJECT_ROOT.parent

canonical_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "HOTEL_CANONICAL_CIMAHI_2026-05-29.csv"
summary_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "hotel_canonical_summary_2026-05-29.json"
validation_path = PROJECT_ROOT / "Penginapan_Workspace" / "02_Curated" / "hotel_canonical_validation_results_2026-05-29.json"

hotel_df = pd.read_csv(canonical_path)
summary = json.loads(summary_path.read_text(encoding="utf-8"))
validation = json.loads(validation_path.read_text(encoding="utf-8"))

display(
    {
        "rows": summary["row_count"],
        "columns": summary["column_count"],
        "gate_status": validation["summary"]["gate_status"],
        "errors": validation["summary"]["error_count"],
        "warnings": validation["summary"]["warning_count"],
        "property_segment_counts": summary["property_segment_counts"],
        "review_confidence_counts": summary["review_confidence_counts"],
        "sentiment_source_counts": summary["sentiment_source_counts"],
    }
)

hotel_df[
    [
        "hotel_id",
        "name",
        "property_segment",
        "overall_rating",
        "reviews",
        "price_lowest",
        "rating_sentiment_score",
        "adjusted_rating_sentiment_score",
        "rating_sentiment_label",
        "review_confidence_label",
        "data_quality_score",
    ]
].head(10)
""",
            ),
            new_cell(
                "markdown",
                """
## Aturan penggunaan untuk recommender dan LLM

- Untuk user yang minta hotel formal, prioritaskan `property_segment == "hotel"` lalu fallback ke `guest_house` jika perlu.
- Untuk user yang minta keluarga, ramai-ramai, murah, atau staycation fleksibel, `villa`, `apartment`, dan `vacation_rental` boleh ikut.
- Baris dengan `missing_review_confidence` atau `low_review_confidence` tidak boleh dijelaskan terlalu percaya diri.
- Baris tanpa `price_available` tidak boleh dipakai untuk klaim murah/mahal secara tegas.
- Baris tanpa `amenities_available` tidak boleh membuat klaim fasilitas spesifik.
- Baris tanpa `image_available` jangan dipakai untuk kartu visual utama.
""",
            ),
        ]
    )

    NOTEBOOK_PATH.write_text(
        json.dumps(notebook, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )

    print(f"Updated {NOTEBOOK_PATH}")
    print(f"Removed old tagged cells and appended 4 cells tagged {TAG}")


if __name__ == "__main__":
    main()
