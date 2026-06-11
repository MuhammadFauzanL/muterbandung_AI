import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

# Load existing notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# Tambahkan Cell baru khusus untuk Analisis Harga per Kategori
kode_eda_harga_kategori = """# Analisis Harga (Tertinggi, Terendah, dan Rata-rata) per Kategori
harga_kategori = df_master.groupby('category').agg(
    Harga_Termurah=('price_min', 'min'),
    Harga_Termahal=('price_max', 'max'),
    Rata_Rata_Harga=('price_min', 'mean'),
    Jumlah_Lokasi=('location_name', 'count')
).sort_values('Rata_Rata_Harga', ascending=False)

# Memformat angka menjadi Rupiah agar mudah dibaca
harga_kategori_display = harga_kategori.copy()
for col in ['Harga_Termurah', 'Harga_Termahal', 'Rata_Rata_Harga']:
    harga_kategori_display[col] = harga_kategori_display[col].apply(lambda x: f"Rp {x:,.0f}")

print("Tabel Analisis Harga per Kategori:")
display(harga_kategori_display)

# Visualisasi Boxplot untuk melihat rentang dan sebaran harga tiap kategori
plt.figure(figsize=(14, 8))
# Kita buat DataFrame yang panjang (melted) jika perlu, 
# tapi lebih mudah memvisualisasikan price_min langsung
sns.boxplot(data=df_master, x='price_min', y='category', palette='coolwarm')
plt.title('Sebaran Harga Tiket Masuk Berdasarkan Kategori', fontsize=16)
plt.xlabel('Harga Tiket Minimal (Rp)')
plt.ylabel('Kategori Wisata')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.show()

print("Insight:")
print("- Kotak (Box) menunjukkan harga wajar/rata-rata untuk kategori tersebut.")
print("- Titik-titik di luar kotak adalah 'Outlier' (Tempat wisata yang harganya jauh lebih mahal dari standar kategorinya).")"""

nb.cells.append(nbf.v4.new_code_cell(kode_eda_harga_kategori))

# Save the notebook back
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil menambahkan cell Harga per Kategori ke wisata_traning.ipynb!")
