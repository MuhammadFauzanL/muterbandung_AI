import pandas as pd

# Baca database utama
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Ambil kolom nama dan buat kolom daerah/alamat untuk konteks AI
# Asumsikan kalau ada kecamatan/kabupaten, kita ambil dari nama atau lokasi
# Kita gabungkan nama lokasi dengan "Bandung Jawa Barat" agar spesifik
df_template = pd.DataFrame()
df_template['location_name'] = df['location_name']
df_template['daerah_pencarian'] = df['location_name'] + ", Bandung, Jawa Barat"
df_template['jam_buka'] = ""
df_template['jam_tutup'] = ""
df_template['tags'] = ""

# Simpan template
output_path = 'Apify_Workspace/Inputs/template_untuk_ai_agent.csv'
df_template.to_csv(output_path, index=False)

print(f"File template CSV berhasil dibuat: {output_path}")
