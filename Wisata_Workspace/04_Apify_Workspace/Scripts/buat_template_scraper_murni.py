import pandas as pd

# Baca database utama
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Buat dataframe baru untuk template AI (Mode Scraper Murni)
df_template = pd.DataFrame()
df_template['location_name'] = df['location_name']
df_template['daerah_pencarian'] = df['location_name'] + ", Bandung, Jawa Barat"

# Kolom-kolom realistis yang HANYA ADA di alat Scraper Google Maps berbayar
df_template['jam_buka'] = ""
df_template['jam_tutup'] = ""
df_template['deskripsi_google'] = ""  # Diambil dari tab "About" atau cuplikan Maps
df_template['google_tags'] = ""       # Diambil dari label/fasilitas di Google Maps

# Simpan template
output_path = 'Apify_Workspace/Inputs/template_scraper_murni.csv'
df_template.to_csv(output_path, index=False)

print(f"File template CSV Scraper Murni berhasil dibuat: {output_path}")
