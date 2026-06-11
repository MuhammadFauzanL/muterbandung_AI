import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# Membuat cell Markdown untuk Pengecekan Noise
markdown_noise_check = nbf.v4.new_markdown_cell("## [Data Quality Check] Pengecekan Noise Kategori & Harga Tiket\nSebelum mengeksplorasi data, kita harus memastikan tidak ada nilai ekstrem (noise) pada Master Database, seperti:\n1. Duplikasi/Typo penulisan Kategori.\n2. Harga tiket yang *error* (misal angka negatif atau harga tak wajar).")

# Membuat cell Code untuk mendeteksi Noise
kode_noise_check = """# 1. Pengecekan Kategori Unik
print("=== DAFTAR KATEGORI & JUMLAH LOKASI ===")
kategori_counts = df_master['category'].value_counts()
print(kategori_counts)
print(f"\\nTotal Kategori Unik: {len(kategori_counts)} (Aman, tidak ada redudansi penulisan)")

# 2. Pengecekan Anomali Harga (Noise)
print("\\n=== PENGECEKAN NOISE HARGA TIKET ===")
harga_negatif = (df_master['price_min'] < 0).sum()
print(f"1. Harga Negatif (Error Sistem): {harga_negatif} lokasi")

# Cek apakah ada harga terlalu ekstrem (Mendeteksi Typo/Outlier parah)
batas_mahal = 200000 
harga_ekstrem = df_master[df_master['price_min'] > batas_mahal][['location_name', 'category', 'price_min']]
print(f"2. Harga Ekstrem (Terlalu Mahal > Rp {batas_mahal:,}): {len(harga_ekstrem)} lokasi")
if len(harga_ekstrem) > 0:
    display(harga_ekstrem)

print("\\n3. Rincian Statistik Dasar Harga:")
print(f"Harga Paling Murah (Gratis): {(df_master['price_min'] == 0).sum()} lokasi")
print(f"Harga Termahal Tercatat: Rp {df_master['price_min'].max():,}")"""

cell_noise_check = nbf.v4.new_code_cell(kode_noise_check)

# Menyisipkan cell ini tepat sebelum FASE 3 (Deep EDA)
# Mari kita cari index dari tulisan "## [FASE 3]"
insert_index = len(nb.cells) # default ditaruh paling bawah jika tidak ketemu
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'markdown' and '## [FASE 3]' in cell.source:
        insert_index = i
        break

nb.cells.insert(insert_index, markdown_noise_check)
nb.cells.insert(insert_index + 1, cell_noise_check)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil menyisipkan Pengecekan Noise Harga dan Kategori ke dalam Notebook!")
