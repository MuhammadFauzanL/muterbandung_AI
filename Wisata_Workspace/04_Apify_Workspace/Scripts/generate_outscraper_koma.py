import pandas as pd

# Baca database wisata kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Buat list dengan format memakai KOMA sesuai contoh Outscraper
queries = []
for nama in df['location_name']:
    # Format: Nama Tempat, Bandung, Jawa Barat
    queries.append(f"{nama}, Bandung, Jawa Barat")

# Simpan ke file teks baru
output_path = 'Apify_Workspace/Inputs/daftar_lokasi_outscraper_koma.txt'
with open(output_path, 'w') as f:
    f.write('\n'.join(queries))

print(f"Berhasil! File dengan format koma dibuat di: {output_path}")
