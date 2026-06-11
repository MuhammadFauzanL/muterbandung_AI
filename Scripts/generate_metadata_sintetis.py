import pandas as pd
import numpy as np

# 1. Baca dataset utama kita
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# 2. Fungsi cerdas untuk menentukan Jam Buka & Durasi berdasarkan Kategori
def generate_metadata(row):
    cat = str(row['category']).lower()
    subcat = str(row['subcategory']).lower()
    
    # Aturan Jam Buka & Durasi
    if 'alam' in cat or 'hutan' in cat or 'gunung' in cat or 'curug' in cat or 'kawah' in cat or 'danau' in cat:
        jam_buka, jam_tutup = '07:00', '17:00'
        durasi = 120  # 2 jam
        tags = 'Alam, Outdoor, Pemandangan, Udara Segar'
    elif 'taman kota' in cat or 'ibadah' in cat or 'masjid' in subcat or 'alun-alun' in subcat:
        jam_buka, jam_tutup = '00:00', '23:59' # 24 Jam
        durasi = 60   # 1 jam
        tags = 'Ruang Publik, Santai, Jalan-jalan'
    elif 'belanja' in cat or 'mall' in subcat:
        jam_buka, jam_tutup = '10:00', '22:00'
        durasi = 150  # 2.5 jam
        tags = 'Belanja, Indoor, Kuliner, Modern'
    elif 'edukasi' in cat or 'museum' in cat or 'seni' in cat or 'sejarah' in cat:
        jam_buka, jam_tutup = '08:00', '16:00'
        durasi = 90   # 1.5 jam
        tags = 'Edukasi, Sejarah, Budaya, Indoor'
    elif 'rekreasi keluarga' in cat or 'taman hiburan' in cat or 'waterpark' in subcat:
        jam_buka, jam_tutup = '08:00', '18:00'
        durasi = 180  # 3 jam
        tags = 'Keluarga, Anak-anak, Wahana, Seru'
    elif 'kuliner' in cat or 'cafe' in subcat or 'resto' in subcat:
        jam_buka, jam_tutup = '11:00', '22:00'
        durasi = 90
        tags = 'Kuliner, Nongkrong, Santai'
    else:
        # Default jika tidak masuk kategori spesifik di atas
        jam_buka, jam_tutup = '08:00', '17:00'
        durasi = 90
        tags = 'Wisata, Umum, Menarik'
        
    return pd.Series([jam_buka, jam_tutup, durasi, tags])

# 3. Terapkan fungsi ke dataframe
print("Membuat data jam buka, durasi, dan tags secara otomatis...")
df[['jam_buka', 'jam_tutup', 'estimasi_durasi_menit', 'tags_sintetis']] = df.apply(generate_metadata, axis=1)

# 4. Simpan ke file CSV baru
output_file = 'DATABASE_WISATA_DENGAN_METADATA.csv'
df.to_csv(output_file, index=False)

print(f"BERHASIL! {len(df)} data wisata telah sukses diperkaya.")
print(f"File disimpan sebagai: {output_file}")

# Tampilkan 5 sampel
print("\n=== HASIL SINTETIS (5 Data Pertama) ===")
print(df[['location_name', 'category', 'jam_buka', 'jam_tutup', 'estimasi_durasi_menit']].head().to_string())
