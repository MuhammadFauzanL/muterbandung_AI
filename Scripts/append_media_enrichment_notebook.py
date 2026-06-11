import nbformat as nbf


NOTEBOOK_PATH = "Notebooks/wisata_training.ipynb"
MARKER = "MUTERBANDUNG_MEDIA_ENRICHMENT_PIPELINE_2026_05_25"


def append_media_enrichment_section():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## Media Enrichment Pipeline + Groundtruth Audit

`{MARKER}`

Tahap ini menambahkan URL gambar, link Google Maps, dan website ke dataset curated secara konservatif. Tujuannya agar frontend dan LLM evidence pack boleh menampilkan media hanya jika media tersebut benar-benar berasal dari raw data yang sudah cocok dengan `location_id`.

Kebijakan audit:

- Dataset aktif tetap `Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv`.
- Raw source: `Dataset/dataset_google-maps-extractor_2026-05-19_08-42-08-170.csv` dan `Dataset/1_Raw_Data/apify_jam_buka_semua_lokasi_raw.csv`.
- Match otomatis hanya menerima exact normalized title dan fuzzy high-confidence.
- Match borderline/mencurigakan tidak diaktifkan; masuk review queue.
- Road-level result seperti `Jl. Curug Panganten` dan `Jl. Gn. Tampomas` ditolak manual.
- `llm_guard` tetap menolak URL/fasilitas yang tidak ada di evidence pack.

Output audit:

- `Dokumentasi_Sistem/MEDIA_ENRICHMENT_AUDIT_2026-05-25.md`
- `Dataset/3_Curated/media_groundtruth_audit.csv`
- `Dataset/3_Curated/media_match_review_queue.csv`
"""

    code = """# Media enrichment smoke test
# Jalankan dari root project PIJAK.

import pandas as pd

curated_path = "Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv"
groundtruth_path = "Dataset/3_Curated/media_groundtruth_audit.csv"
review_queue_path = "Dataset/3_Curated/media_match_review_queue.csv"

df = pd.read_csv(curated_path)
gt = pd.read_csv(groundtruth_path)
rq = pd.read_csv(review_queue_path)

media_cols = [col for col in df.columns if col.startswith("media_")]
print("media_columns:", media_cols)
print("rows:", len(df))
print("accepted_media_rows:", int(df["media_available"].sum()))
print("missing_or_review_rows:", int((~df["media_available"]).sum()))
print("groundtruth_rows:", len(gt))
print("review_queue_rows:", len(rq))

sample = df[df["media_available"] == True][[
    "location_id",
    "location_name",
    "media_match_title",
    "media_match_method",
    "media_image_url",
    "media_destination_url",
]].head(5)
display(sample)
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(code))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)

    print(f"Updated {NOTEBOOK_PATH}")


if __name__ == "__main__":
    append_media_enrichment_section()
