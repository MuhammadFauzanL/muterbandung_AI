from __future__ import annotations

from pathlib import Path

import nbformat
from nbformat.v4 import new_markdown_cell


ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = ROOT / "Penginapan_Workspace" / "03_Notebooks" / "penginapan_training.ipynb"
TAG = "manual_review_parent_child_2026_06_05"


def main() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    nb.cells = [cell for cell in nb.cells if TAG not in cell.get("metadata", {}).get("tags", [])]

    note = new_markdown_cell(
        """
## Catatan Review Manual - Parent-Child Candidate

Review manual untuk kandidat nomor **1-13** menyatakan bahwa pasangan tersebut merujuk ke properti/lokasi yang sama.

Perbedaan nama berasal dari format OTA: **nama properti + tipe kamar**. Jadi label seperti `Deluxe Double Room`, `Standard Double Room`, `Family Room`, `King Room`, `Twin Room`, atau variasi kamar lain dipahami sebagai unit kamar, bukan tempat berbeda.

Keputusan manual:

| No | Keputusan |
|---:|---|
| 1 | Accept - child milik Sans Hotel Skyland Pasteur Bandung |
| 2 | Accept - child milik Sans Hotel Skyland Pasteur Bandung |
| 3 | Accept - child milik Grha Blue Sky |
| 4 | Accept - child milik Vila Kopi Ciwidey |
| 5 | Accept - child milik Vila Kopi Ciwidey |
| 6 | Accept - child milik Vila Kopi Ciwidey |
| 7 | Accept - child milik Bantal Guling Guesthouse Trans |
| 8 | Accept - child milik Bantal Guling Guesthouse Trans |
| 9 | Accept - child milik Bantal Guling Guesthouse Trans |
| 10 | Accept - child milik RedDoorz Syariah near BTC Fashion Mall |
| 11 | Accept - child milik Bantal Guling Guesthouse Trans |
| 12 | Accept - child milik RedDoorz Plus near Asia Afrika 3 |
| 13 | Accept - child milik Penginapan Rio Anakku Syariah Banjaran Mitra RedDoorz |

Catatan: keputusan ini berasal dari review manual dan pengecekan Google, bukan dari auto-merge final. Relasi final tetap dibuat sebagai tahap terpisah agar jejak keputusan jelas.
"""
    )
    note.metadata["tags"] = [TAG, "decision-documentation"]
    nb.cells.append(note)
    nbformat.write(nb, NOTEBOOK_PATH)
    print(f"updated_notebook={NOTEBOOK_PATH}")
    print(f"cells={len(nb.cells)}")


if __name__ == "__main__":
    main()
