import json
from pathlib import Path

notebook_path = Path(r'D:\File\file\Fauzan Lubada\PIJAK\Behaviour_Workspace\02_Notebooks\Behaviour_Model_Training.ipynb')

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

markdown_tahap4 = [
    "## TAHAP 4: Filtering & Pemetaan Kategori (Mapping)\n",
    "Tahap ini merupakan proses \"Pembersihan Besar-besaran\".\n",
    "\n",
    "* **Membuang** puluhan ribu data aktivitas warga lokal (*noise* seperti sekolah, kampus, dan kantor).\n",
    "* **Memetakan** kategori Foursquare komersial yang valid ke dalam **17 Taksonomi MuterBandung** (seperti Kuliner, Belanja, Hiburan, dll)."
]

code_tahap4 = [
    "# 1. Mendefinisikan aturan pemetaan (Foursquare Mentah -> Kategori MuterBandung)\n",
    "# Kategori yang tidak ada di daftar ini otomatis bernilai NaN dan akan di-drop\n",
    "category_mapping = {\n",
    "    # --- KULINER ---\n",
    "    'Café': 'Kuliner', 'Indonesian Restaurant': 'Kuliner', 'Asian Restaurant': 'Kuliner',\n",
    "    'Coffee Shop': 'Kuliner', 'Restaurant': 'Kuliner', 'Food Court': 'Kuliner',\n",
    "    'Japanese Restaurant': 'Kuliner', 'Ramen Restaurant': 'Kuliner', 'Fried Chicken Joint': 'Kuliner',\n",
    "    'Bakery': 'Kuliner', 'Burger Joint': 'Kuliner', 'Pizza Place': 'Kuliner',\n",
    "    'Fast Food Restaurant': 'Kuliner', 'Steakhouse': 'Kuliner', 'Donut Shop': 'Kuliner',\n",
    "    'Sushi Restaurant': 'Kuliner', 'Chinese Restaurant': 'Kuliner', 'Seafood Restaurant': 'Kuliner',\n",
    "    'Food Truck': 'Kuliner',\n",
    "    \n",
    "    # --- BELANJA ---\n",
    "    'Shopping Mall': 'Belanja', 'Bookstore': 'Belanja', \n",
    "    'Clothing Store': 'Belanja', 'Department Store': 'Belanja',\n",
    "    \n",
    "    # --- HIBURAN ---\n",
    "    'Multiplex': 'Hiburan', 'Arcade': 'Hiburan', 'Karaoke Bar': 'Hiburan Malam',\n",
    "    \n",
    "    # --- RELIGI ---\n",
    "    'Mosque': 'Religi', 'Church': 'Religi',\n",
    "    \n",
    "    # --- PENGINAPAN ---\n",
    "    'Hotel': 'Santai' # Turis kembali ke hotel untuk bersantai\n",
    "}\n",
    "\n",
    "# 2. Mengaplikasikan mapping ke kolom baru\n",
    "df_raw['muterbandung_category'] = df_raw['venue_category'].map(category_mapping)\n",
    "\n",
    "# 3. Membuang kategori noise\n",
    "total_awal = len(df_raw)\n",
    "df_clean = df_raw.dropna(subset=['muterbandung_category']).copy()\n",
    "total_akhir = len(df_clean)\n",
    "\n",
    "print(\"=== HASIL FILTERING DATA ===\")\n",
    "print(f\"Data Mentah Awal        : {total_awal} baris\")\n",
    "print(f\"Data Noise (Dibuang)    : {total_awal - total_akhir} baris\")\n",
    "print(f\"Data Murni Wisata (Sisa): {total_akhir} baris\\n\")\n",
    "\n",
    "# 4. Melihat distribusi kategori MuterBandung yang baru\n",
    "print(\"=== DISTRIBUSI KATEGORI MUTERBANDUNG ===\")\n",
    "print(df_clean['muterbandung_category'].value_counts())\n",
    "\n",
    "# 5. Mengurutkan data berdasarkan urutan waktu kunjungan untuk persiapan Markov Chain\n",
    "df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'])\n",
    "df_clean = df_clean.sort_values(by=['trail_id', 'timestamp'])\n"
]

cell_md = {
    "cell_type": "markdown",
    "metadata": {},
    "source": markdown_tahap4
}

cell_code = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": code_tahap4
}

# Append cells to the end of the notebook
nb['cells'].append(cell_md)
nb['cells'].append(cell_code)

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print("Berhasil!")
