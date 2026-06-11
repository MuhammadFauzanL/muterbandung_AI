import nbformat as nbf


NOTEBOOK_PATH = "Notebooks/wisata_training.ipynb"
MARKER = "MUTERBANDUNG_MEDIA_FILL_GOOGLE_COLAB_2026_05_25"


def append_media_fill_colab_section():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## Media Fill Google Colab Workflow

`{MARKER}`

Tahap ini menyiapkan workflow Google Colab untuk pengisian media saja, tanpa Apify. Colab digunakan untuk membuka link bantu Google Search/Maps/Images, mengisi URL gambar/link destinasi, memvalidasi URL, lalu mengekspor CSV apply-ready.

File penting:

- `Notebooks/Media_Fill_Google_Colab.ipynb`
- `Dataset/3_Curated/manual_media_fill_queue.csv`
- `Scripts/apply_manual_media_updates.py`
- `Dokumentasi_Sistem/MEDIA_FILL_COLAB_WORKFLOW.md`

Aturan:

- Colab tidak langsung mengubah dataset utama.
- Isi `reviewer_status=approved` untuk baris yang siap dipakai.
- Download `media_manual_apply_ready.csv`, lalu apply lokal dengan script backup-safe.
"""

    code = """# Ringkasan workflow Colab media fill
import pandas as pd

queue = pd.read_csv("Dataset/3_Curated/manual_media_fill_queue.csv")

print("media queue rows:", len(queue))
print("high priority:", int((queue["priority"] == "HIGH").sum()))
print("has helper search columns:", all(col in queue.columns for col in [
    "google_search_url",
    "google_maps_search_url",
    "google_image_search_url",
]))
display(queue.head(5))
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(code))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)

    print(f"Updated {NOTEBOOK_PATH}")


if __name__ == "__main__":
    append_media_fill_colab_section()
