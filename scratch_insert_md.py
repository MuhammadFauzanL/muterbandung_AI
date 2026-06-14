import json
from pathlib import Path

notebook_path = Path(r'D:\File\file\Fauzan Lubada\PIJAK\Behaviour_Workspace\02_Notebooks\Behaviour_Model_Training.ipynb')

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

markdown_source = [
    "### Keputusan Audit Data\n",
    "Berdasarkan hasil audit di atas, ditemukan 26.534 baris data kosong pada kolom koordinat (`latitude`, `longitude`) dan `name`. Mengingat pemodelan Markov Chain ini memprediksi pada level **kategori venue**, ketiadaan nama tempat yang spesifik dapat diabaikan dengan aman.\n",
    "\n",
    "Selain itu, kolom `trail_id` mengidentifikasi rentetan pergerakan pengguna dalam satu periode perjalanan. Kolom ini akan menjadi kunci utama (primary key) untuk merangkai perpindahan kategori (*sequence extraction*) pada tahapan selanjutnya."
]

new_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": markdown_source
}

# Menyisipkan cell markdown setelah cell kode TAHAP 2
# Index cell kode TAHAP 2 adalah 5 (indeks ke-5 dari 0)
nb['cells'].insert(6, new_cell)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Berhasil menyisipkan kesimpulan audit data ke dalam notebook!")
