import pandas as pd

df = pd.read_csv('Dataset/MASTER_REVIEWS_FINAL.csv')
print('=== PROFIL DATA ===')
print(f'Total baris: {len(df)}')
print(f'Lokasi unik: {df["location_name"].nunique()}')
print(f'Kolom: {df.columns.tolist()}')
print()

# Distribusi rating
print('=== DISTRIBUSI RATING ===')
print(df['rating'].value_counts().sort_index())
print()

# Panjang teks rata-rata
df['panjang_teks'] = df['review_text'].astype(str).apply(len)
print('=== STATISTIK PANJANG TEKS ===')
print(f'Rata-rata: {df["panjang_teks"].mean():.0f} karakter')
print(f'Median: {df["panjang_teks"].median():.0f} karakter')
print(f'Min: {df["panjang_teks"].min()} karakter')
print(f'Max: {df["panjang_teks"].max()} karakter')
print()

# Cek bahasa (sampel kata kunci)
sample_texts = df['review_text'].dropna().sample(200, random_state=42).str.lower()
indo_count = sample_texts.str.contains('bagus|tempat|indah|bersih|kotor|enak|pemandangan|keren|mantap|seru').sum()
eng_count = sample_texts.str.contains('good|beautiful|nice|great|clean|amazing|view|place|bad').sum()
print(f'=== DETEKSI BAHASA (Sampel 200) ===')
print(f'Mengandung kata Indonesia: {indo_count}')
print(f'Mengandung kata Inggris: {eng_count}')
print()

# Distribusi sumber
print('=== SUMBER DATA ===')
print(df['source_file'].value_counts())
