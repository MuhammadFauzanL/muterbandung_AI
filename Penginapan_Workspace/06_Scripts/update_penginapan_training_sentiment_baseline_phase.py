from pathlib import Path
from textwrap import dedent

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
SECTION_TITLE = "## Fase H - Sentiment Penginapan dan Ranking Jarak"


def md(text):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())


def build_cells():
    return [
        md(f"""
        {SECTION_TITLE}

        Fase ini memakai model sentiment penginapan untuk membaca review hotel, lalu membuat baseline ranking dengan bobot jarak lebih besar.
        """),
        md("""
        ### H1 - Cek Input

        Tujuan: pastikan parent master, review normalized, dan model sentiment sudah tersedia.
        """),
        code("""
        from pathlib import Path
        import json
        import pandas as pd

        ROOT = Path.cwd()
        WORKSPACE = ROOT / "Penginapan_Workspace"
        CURATED_DIR = WORKSPACE / "02_Curated"
        MODEL_PATH = WORKSPACE / "07_Models" / "model_sentimen_muterbandung.pkl"

        input_files = [
            CURATED_DIR / "PENGINAPAN_PARENT_MASTER_2026-06-05.csv",
            CURATED_DIR / "PENGINAPAN_COMPASS_REVIEW_TEST_BATCH_30_RAW_NORMALIZED_2026-06-06.csv",
            CURATED_DIR / "PENGINAPAN_PARENT_CHILD_RELATIONS_FINAL_2026-06-05.csv",
            MODEL_PATH,
        ]

        rows = []
        for path in input_files:
            rows.append({
                "file": str(path.relative_to(ROOT)),
                "exists": path.exists(),
                "size_mb": round(path.stat().st_size / 1024 / 1024, 2) if path.exists() else None,
            })
        pd.DataFrame(rows)
        """),
        md("""
        Keputusan: input cukup untuk batch awal. Review yang dipakai masih batch test, jadi hasil sentiment belum mewakili semua penginapan.
        """),
        md("""
        ### H2 - Jalankan Inference dan Agregasi

        Tujuan: prediksi sentiment per review, lalu agregasi ke parent hotel.
        """),
        code("""
        import subprocess
        import sys

        script_path = WORKSPACE / "06_Scripts" / "build_penginapan_sentiment_baseline.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        summary = json.loads(result.stdout)
        print(json.dumps({
            "review_rows_input": summary["review_rows_input"],
            "review_rows_with_text_inference": summary["review_rows_with_text_inference"],
            "parent_hotels_with_sentiment": summary["parent_hotels_with_sentiment"],
            "parent_master_rows": summary["parent_master_rows"],
            "parent_master_with_sentiment_rows": summary["parent_master_with_sentiment_rows"],
            "distance_weight": summary["distance_weighted_baseline"]["weights"]["distance"],
            "sentiment_weight": summary["distance_weighted_baseline"]["weights"]["sentiment"],
        }, indent=2, ensure_ascii=False))
        """),
        md("""
        Keputusan: sentiment berhasil masuk ke 28 parent hotel dari batch test. Ranking hotel dibuat distance-heavy karena user biasanya mencari penginapan dekat tujuan.
        """),
        md("""
        ### H3 - Audit Agregasi Sentiment

        Tujuan: lihat hasil sentiment per hotel yang sudah punya review teks.
        """),
        code("""
        aggregated_path = CURATED_DIR / "PENGINAPAN_SENTIMENT_AGGREGATED_2026-06-10.csv"
        aggregated = pd.read_csv(aggregated_path)

        display(
            aggregated[
                [
                    "parent_penginapan_id",
                    "hotel_review_count_analyzed",
                    "hotel_sentiment_score",
                    "hotel_adjusted_sentiment_score",
                    "hotel_adjusted_sentiment_label",
                    "hotel_review_confidence_label",
                    "positive_review_count",
                    "neutral_review_count",
                    "negative_review_count",
                ]
            ]
            .sort_values(["hotel_review_count_analyzed", "hotel_adjusted_sentiment_score"], ascending=[False, False])
            .head(15)
        )

        aggregated["hotel_adjusted_sentiment_label"].value_counts().rename_axis("label").reset_index(name="count")
        """),
        md("""
        Keputusan: hasil ini layak sebagai sinyal awal. Hotel tanpa review batch tetap diberi status sentiment belum tersedia, bukan dipaksa netral.
        """),
        md("""
        ### H4 - Dataset Parent Dengan Sentiment

        Tujuan: cek dataset parent master setelah kolom sentiment digabung.
        """),
        code("""
        parent_sentiment_path = CURATED_DIR / "PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10.csv"
        parent_with_sentiment = pd.read_csv(parent_sentiment_path)

        audit_parent = {
            "rows": len(parent_with_sentiment),
            "with_sentiment": int(parent_with_sentiment["hotel_sentiment_available"].sum()),
            "without_sentiment": int((~parent_with_sentiment["hotel_sentiment_available"].astype(bool)).sum()),
            "columns": len(parent_with_sentiment.columns),
        }
        print(json.dumps(audit_parent, indent=2, ensure_ascii=False))

        parent_with_sentiment[
            [
                "penginapan_id",
                "name",
                "property_type",
                "overall_rating",
                "reviews",
                "price_lowest",
                "hotel_sentiment_available",
                "hotel_adjusted_sentiment_score",
                "hotel_adjusted_sentiment_label",
                "hotel_review_confidence_label",
            ]
        ].query("hotel_sentiment_available == True").head(10)
        """),
        md("""
        Keputusan: file ini menjadi kandidat runtime hotel berikutnya. Coverage sentiment masih kecil karena input review baru batch test.
        """),
        md("""
        ### H5 - Baseline Ranking Dengan Jarak Lebih Besar

        Tujuan: audit contoh ranking hotel saat jarak menjadi bobot terbesar.
        """),
        code("""
        sample_path = CURATED_DIR / "PENGINAPAN_DISTANCE_WEIGHTED_BASELINE_SAMPLE_2026-06-10.csv"
        sample = pd.read_csv(sample_path)

        display(
            sample[
                [
                    "penginapan_id",
                    "name",
                    "property_type",
                    "distance_km_reference",
                    "hotel_recommendation_score",
                    "hotel_distance_score",
                    "hotel_rating_score",
                    "hotel_sentiment_ranking_score",
                    "hotel_price_score",
                    "hotel_review_count_analyzed",
                    "hotel_adjusted_sentiment_label",
                ]
            ].head(20)
        )

        sample[["hotel_recommendation_score", "distance_km_reference"]].describe()
        """),
        md("""
        Keputusan: bobot jarak dibuat 45%, paling besar dibanding rating dan sentiment. Ini cocok untuk hotel sebagai pendukung wisata terdekat.
        """),
        md("""
        ### H6 - Endpoint Baseline Hotel

        Tujuan: pastikan endpoint baseline hotel sudah tersedia di backend.
        """),
        code("""
        app_path = ROOT / "Scripts" / "app.py"
        recommender_path = ROOT / "Scripts" / "penginapan_recommender.py"
        app_text = app_path.read_text(encoding="utf-8")

        endpoint_audit = {
            "penginapan_recommender_exists": recommender_path.exists(),
            "endpoint_registered": "/api/penginapan/recommend" in app_text,
            "schema_version_registered": "muterbandung.api.penginapan.recommend.v1" in app_text,
            "ranking_mode": "distance_weighted_baseline",
        }
        print(json.dumps(endpoint_audit, indent=2, ensure_ascii=False))
        """),
        md("""
        Keputusan: endpoint baseline hotel tersedia. Statusnya masih baseline karena sentiment baru dari batch test.
        """),
        md("""
        ### H7 - Output Fase Ini

        Tujuan: catat file yang dihasilkan untuk langkah berikutnya.
        """),
        code("""
        output_files = [
            CURATED_DIR / "PENGINAPAN_REVIEW_SENTIMENT_INFERENCE_2026-06-10.csv",
            CURATED_DIR / "PENGINAPAN_SENTIMENT_AGGREGATED_2026-06-10.csv",
            CURATED_DIR / "PENGINAPAN_PARENT_MASTER_WITH_SENTIMENT_2026-06-10.csv",
            CURATED_DIR / "PENGINAPAN_DISTANCE_WEIGHTED_BASELINE_SAMPLE_2026-06-10.csv",
            CURATED_DIR / "penginapan_sentiment_baseline_summary_2026-06-10.json",
        ]

        pd.DataFrame([
            {
                "file": str(path.relative_to(ROOT)),
                "exists": path.exists(),
                "size_mb": round(path.stat().st_size / 1024 / 1024, 2) if path.exists() else None,
            }
            for path in output_files
        ])
        """),
        md("""
        Ringkasan: sentiment hotel sudah bisa dipakai untuk batch awal. Langkah berikutnya adalah menjalankan proses yang sama pada full review, lalu membuat endpoint hotel baseline.
        """),
    ]


def main():
    nb = nbf.read(NOTEBOOK_PATH, as_version=4)
    cleaned_cells = []
    skip = False
    for cell in nb.cells:
        source = "".join(cell.get("source", ""))
        if SECTION_TITLE in source:
            skip = True
            continue
        if skip and source.startswith("## Fase "):
            skip = False
        if not skip:
            cleaned_cells.append(cell)

    phase_nb = nbf.v4.new_notebook()
    phase_nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    phase_nb.cells = build_cells()
    executed = NotebookClient(phase_nb, timeout=180, kernel_name="python3").execute()

    nb.cells = cleaned_cells + executed.cells
    nbf.write(nb, NOTEBOOK_PATH)
    print(NOTEBOOK_PATH)


if __name__ == "__main__":
    main()
