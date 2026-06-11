import pandas as pd

# Load Database Master Lengkap
df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

print("=== AUDIT GEOSPATIAL (GPS) ===")
lat_kosong = df_master['latitude'].isnull().sum()
lon_kosong = df_master['longitude'].isnull().sum()
print(f"Lokasi tanpa Latitude: {lat_kosong}")
print(f"Lokasi tanpa Longitude: {lon_kosong}")

print("\n=== AUDIT HARGA TIKET (PRICING) ===")
if 'price_min' in df_master.columns:
    price_min_kosong = df_master['price_min'].isnull().sum()
    print(f"Harga Min kosong (Null): {price_min_kosong}")
    
    # Cek nilai 0
    nol_count = (df_master['price_min'] == 0).sum()
    print(f"Lokasi dengan harga Rp 0: {nol_count} Lokasi")
else:
    print("Kolom price_min tidak ditemukan, harap sesuaikan nama kolom harga.")

print("\n=== AUDIT KATEGORI PARIWISATA ===")
print(df_master['category'].value_counts(dropna=False).head())

print("\nKESIMPULAN AUDIT:")
if lat_kosong == 0 and lon_kosong == 0:
    print("[AMAN] Seluruh lokasi memiliki koordinat GPS!")
else:
    print(f"[WARNING] Ditemukan {lat_kosong} data bocor tanpa GPS, butuh imputasi.")
