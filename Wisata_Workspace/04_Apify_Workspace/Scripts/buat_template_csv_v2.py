import pandas as pd

# Baca database utama
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# Buat dataframe baru untuk template AI
df_template = pd.DataFrame()
df_template['location_name'] = df['location_name']
df_template['daerah_pencarian'] = df['location_name'] + ", Bandung, Jawa Barat"

# Kolom-kolom cemerlang yang harus diisi AI eksternal
df_template['jam_buka'] = ""
df_template['jam_tutup'] = ""
df_template['estimasi_durasi_menit'] = ""  # Sangat penting untuk membuat Itinerary!
df_template['deskripsi_singkat'] = ""      # Penting untuk Chatbot RAG
df_template['target_pengunjung'] = ""      # Keluarga / Pasangan / Solo / Anak
df_template['tags'] = ""                   # Fitur & Fasilitas

# Simpan template yang sudah di-upgrade
output_path = 'Apify_Workspace/Inputs/template_untuk_ai_agent_v2.csv'
df_template.to_csv(output_path, index=False)

print(f"File template CSV V2 berhasil dibuat: {output_path}")
