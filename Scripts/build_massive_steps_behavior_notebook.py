from pathlib import Path
from textwrap import dedent

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "MuterBandung_Behavior_Model_Workspace"
NOTEBOOK_DIR = WORKSPACE / "02_Notebooks"
NOTEBOOK_PATH = NOTEBOOK_DIR / "massive_steps_behavior_training.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(dedent(text).strip())


def code(text):
    return nbf.v4.new_code_cell(dedent(text).strip())


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.metadata["language_info"] = {
        "name": "python",
        "pygments_lexer": "ipython3",
    }

    nb.cells = [
        md("""
        # Massive-STEPS Bandung - Behavior Preparation

        Notebook ini untuk filtering dan mapping data Massive-STEPS Bandung.
        Tahap ini belum training model. Fokusnya menyiapkan data behavior agar cocok dengan arah MuterBandung.
        """),
        md("""
        ## Tahap A - Cek File Raw

        Tujuan: pastikan file tabular train, validation, dan test tersedia.
        """),
        code("""
        from pathlib import Path
        import json
        import pandas as pd

        ROOT = Path.cwd()
        WORKSPACE = ROOT / "MuterBandung_Behavior_Model_Workspace"
        RAW_DIR = WORKSPACE / "01_Raw_Data" / "massive_steps_bandung"

        tabular_files = {
            "train": RAW_DIR / "tabular_train-00000-of-00001.parquet",
            "validation": RAW_DIR / "tabular_validation-00000-of-00001.parquet",
            "test": RAW_DIR / "tabular_test-00000-of-00001.parquet",
        }

        rows = []
        for split, path in tabular_files.items():
            df_head = pd.read_parquet(path)
            rows.append({
                "split": split,
                "exists": path.exists(),
                "rows": len(df_head),
                "columns": len(df_head.columns),
                "column_names": ", ".join(df_head.columns[:8]),
            })

        pd.DataFrame(rows)
        """),
        md("""
        Keputusan: file tabular dipakai sebagai basis karena punya kategori, koordinat, waktu, user, dan trail.
        """),
        md("""
        ## Tahap B - Audit Kategori Awal

        Tujuan: lihat apakah data bisa langsung dipakai atau perlu disaring dulu.
        """),
        code("""
        frames = []
        for split, path in tabular_files.items():
            frame = pd.read_parquet(path)
            frame["split"] = split
            frames.append(frame)

        raw = pd.concat(frames, ignore_index=True)
        raw["timestamp"] = pd.to_datetime(raw["timestamp"], errors="coerce")

        audit_awal = {
            "total_rows": len(raw),
            "unique_users": raw["user_id"].nunique(),
            "unique_trails": raw["trail_id"].nunique(),
            "unique_venues": raw["venue_id"].nunique(),
            "unique_categories": raw["venue_category"].nunique(),
            "missing_name_pct": round(raw["name"].isna().mean() * 100, 2),
            "missing_latitude_pct": round(raw["latitude"].isna().mean() * 100, 2),
            "min_timestamp": str(raw["timestamp"].min()),
            "max_timestamp": str(raw["timestamp"].max()),
        }
        print(json.dumps(audit_awal, indent=2, ensure_ascii=False))

        raw["venue_category"].value_counts().head(20).rename_axis("venue_category").reset_index(name="checkin_count")
        """),
        md("""
        Keputusan: data tidak boleh dipakai mentah. Kategori harian seperti rumah, sekolah, kantor, dan jalan terlalu dominan.
        """),
        md("""
        ## Tahap C - Jalankan Filtering dan Mapping

        Tujuan: pisahkan kategori yang cocok untuk MuterBandung, noise, dan kategori yang masih perlu dicek.
        """),
        code("""
        import subprocess
        import sys

        script_path = ROOT / "Scripts" / "prepare_massive_steps_filter_mapping.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        summary = json.loads(result.stdout)
        print(json.dumps({
            "raw_rows": summary["raw_rows"],
            "mapping_status_counts_rows": summary["mapping_status_counts_rows"],
            "filtered_rows": summary["filtered_rows"],
            "filtered_row_pct": summary["filtered_row_pct"],
            "sequence_rows": summary["sequence_rows"],
        }, indent=2, ensure_ascii=False))
        """),
        md("""
        Keputusan: hanya `mapped_keep` yang masuk kandidat training. Noise dan needs_review ditahan dulu.
        """),
        md("""
        ## Tahap D - Audit Hasil Mapping

        Tujuan: cek komposisi hasil mapping setelah aturan diterapkan.
        """),
        code("""
        CURATED_DIR = WORKSPACE / "03_Curated"
        EVAL_DIR = WORKSPACE / "04_Evaluation"
        DATE_TAG = "2026-06-10"

        mapping_path = CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_MAPPING_CANDIDATE_{DATE_TAG}.csv"
        summary_path = EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_FILTERING_MAPPING_SUMMARY_{DATE_TAG}.json"
        mapping = pd.read_csv(mapping_path)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

        status_table = mapping["mapping_status"].value_counts().rename_axis("mapping_status").reset_index(name="category_count")
        label_table = (
            mapping[mapping["mapping_status"].eq("mapped_keep")]
            .sort_values("checkin_count", ascending=False)
            .groupby("muterbandung_label", as_index=False)
            .agg(category_count=("venue_category", "count"), checkin_count=("checkin_count", "sum"))
            .sort_values("checkin_count", ascending=False)
        )

        display(status_table)
        display(label_table)
        """),
        md("""
        Keputusan: komposisi diterima untuk baseline behavior. Kuliner dan belanja wajar dominan karena ini data check-in, bukan dataset wisata kurasi.
        """),
        md("""
        ## Tahap E - Cek Kategori Rawan Salah

        Tujuan: pastikan kategori harian tidak ikut masuk kandidat karena kata pendek seperti art/bar.
        """),
        code("""
        suspicious = mapping[
            mapping["venue_category"].str.contains(
                "barber|martial|college|school|office|home|road|apartment|arts|bar|building",
                case=False,
                na=False,
            )
        ].sort_values("checkin_count", ascending=False)

        suspicious[["venue_category", "checkin_count", "muterbandung_label", "mapping_status", "rule_reason"]].head(50)
        """),
        md("""
        Keputusan: kategori harian sudah tertahan. `Barbershop`, `apartment`, dan `college` tidak ikut kandidat training.
        """),
        md("""
        ## Tahap F - Queue Manual Review

        Tujuan: tampilkan kategori yang belum aman diputuskan otomatis.
        """),
        code("""
        needs_review_path = EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_MAPPING_NEEDS_REVIEW_{DATE_TAG}.csv"
        needs_review = pd.read_csv(needs_review_path)
        needs_review[["venue_category", "checkin_count", "unique_venues", "missing_name_pct", "missing_latitude_pct"]].head(40)
        """),
        md("""
        Keputusan: needs_review jangan dipaksa. Jika nanti coverage kurang, kategori ini dibuka bertahap.
        """),
        md("""
        ## Tahap G - Candidate Sequence

        Tujuan: cek data sequence yang nanti bisa dipakai untuk baseline next-category.
        """),
        code("""
        sequence_path = CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_CATEGORY_SEQUENCE_CANDIDATE_{DATE_TAG}.csv"
        sequences = pd.read_csv(sequence_path)

        sequence_audit = {
            "sequence_rows": len(sequences),
            "unique_users": sequences["user_id"].nunique(),
            "unique_trails": sequences["trail_id"].nunique(),
            "avg_sequence_length": round(sequences["sequence_length"].mean(), 2),
            "split_counts": sequences["split"].value_counts().to_dict(),
        }
        print(json.dumps(sequence_audit, indent=2, ensure_ascii=False))

        sequences[["trail_id", "user_id", "split", "sequence_length", "history_categories", "target_next_category"]].head(15)
        """),
        md("""
        Keputusan: sequence sudah cukup untuk baseline next-category. Belum dipakai untuk next-POI langsung.
        """),
        md("""
        ## Tahap H - Output Tahap Ini

        Tujuan: catat file hasil filtering dan mapping.
        """),
        code("""
        output_files = [
            mapping_path,
            CURATED_DIR / f"MASSIVE_STEPS_BANDUNG_FILTERED_CHECKINS_CANDIDATE_{DATE_TAG}.csv",
            sequence_path,
            needs_review_path,
            EVAL_DIR / f"MASSIVE_STEPS_BANDUNG_EXCLUDED_NOISE_CATEGORIES_{DATE_TAG}.csv",
            summary_path,
        ]

        pd.DataFrame([
            {"file": str(path.relative_to(ROOT)), "exists": path.exists(), "size_mb": round(path.stat().st_size / 1024 / 1024, 2)}
            for path in output_files
        ])
        """),
        md("""
        Ringkasan: tahap filtering dan mapping selesai. Langkah berikutnya adalah review kategori needs_review, lalu training baseline next-category.
        """),
    ]
    return nb


def main():
    NOTEBOOK_DIR.mkdir(parents=True, exist_ok=True)
    nb = build_notebook()
    client = NotebookClient(nb, timeout=180, kernel_name="python3")
    executed = client.execute()
    nbf.write(executed, NOTEBOOK_PATH)
    print(NOTEBOOK_PATH)


if __name__ == "__main__":
    main()
