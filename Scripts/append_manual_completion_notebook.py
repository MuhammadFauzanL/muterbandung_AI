import nbformat as nbf


NOTEBOOK_PATH = "Notebooks/wisata_training.ipynb"
MARKER = "MUTERBANDUNG_MANUAL_COMPLETION_QUEUES_2026_05_25"


def append_manual_completion_section():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## Manual Completion Queues

`{MARKER}`

Tahap ini membuat CSV kerja manual untuk mengisi data yang masih kosong atau belum terverifikasi. CSV ini tidak langsung mengubah dataset utama; reviewer mengisi kolom `new_*`, `new_value`, atau kolom reviewer terlebih dahulu, lalu perubahan nanti diterapkan lewat pipeline apply/merge terpisah agar tetap auditable.

Output:

- `Dataset/3_Curated/manual_media_fill_queue.csv`
- `Dataset/3_Curated/manual_data_fill_queue.csv`
- `Dataset/3_Curated/manual_realworld_verification_queue.csv`
- `Dokumentasi_Sistem/MANUAL_COMPLETION_QUEUES_AUDIT_2026-05-25.md`

Ringkasan awal:

- Media kosong/belum aman: 53 baris.
- Data non-media yang perlu isi/review: 60 isu.
- Real-world flags yang perlu verifikasi: 213 destinasi aktif.
"""

    code = """# Audit ringkas manual completion queues
import pandas as pd

media_queue = pd.read_csv("Dataset/3_Curated/manual_media_fill_queue.csv")
data_queue = pd.read_csv("Dataset/3_Curated/manual_data_fill_queue.csv")
realworld_queue = pd.read_csv("Dataset/3_Curated/manual_realworld_verification_queue.csv")

print("media_missing_rows:", len(media_queue))
print("data_issue_rows:", len(data_queue))
print("realworld_verification_rows:", len(realworld_queue))
print("\\nMedia priority:")
print(media_queue["priority"].value_counts().to_string())
print("\\nData issue type:")
print(data_queue["issue_type"].value_counts().to_string())
display(media_queue.head(10))
display(data_queue.head(10))
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(code))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)

    print(f"Updated {NOTEBOOK_PATH}")


if __name__ == "__main__":
    append_manual_completion_section()
