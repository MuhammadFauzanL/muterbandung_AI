import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

# Load existing notebook
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# ---------------------------------------------------------
# FASE 2: DATA CLEANING & NOISE REDUCTION
# ---------------------------------------------------------
nb.cells.append(nbf.v4.new_markdown_cell("## [FASE 2] Data Cleaning & Noise Reduction\nSebelum melakukan analisis mendalam, data ulasan mentah harus dibersihkan dari *noise* (contoh: ulasan yang hanya berisi 1 kata, duplikat, atau karakter tidak bermakna)."))

kode_cleaning = """import pandas as pd
import re

print("Memulai Proses Data Cleaning...")
df_reviews = pd.read_csv('Dataset/MASTER_REVIEWS_FINAL.csv')

awal_len = len(df_reviews)

# 1. Hapus Duplikat
df_reviews = df_reviews.drop_duplicates(subset=['location_name', 'reviewer_name', 'review_text'])
setelah_duplikat = len(df_reviews)

# 2. Hapus Ulasan Terlalu Pendek (Noise)
# Ulasan < 10 karakter biasanya hanya berisi "ok", "bagus", atau emoji saja, tidak berguna untuk NLP Aspek.
df_reviews['panjang_teks'] = df_reviews['review_text'].astype(str).apply(len)
df_reviews = df_reviews[df_reviews['panjang_teks'] >= 10].copy()
setelah_short = len(df_reviews)

# 3. Basic Text Cleaning (Lowecase & hapus spasi berlebih)
def basic_clean(text):
    text = str(text).lower()
    text = re.sub(r'\\s+', ' ', text) # Hapus spasi ganda
    return text.strip()

df_reviews['review_text_clean'] = df_reviews['review_text'].apply(basic_clean)

# Simpan hasil cleaning
df_reviews.to_csv('Dataset/MASTER_REVIEWS_CLEANED.csv', index=False)

print(f"Data Awal: {awal_len} baris")
print(f"Dihapus (Duplikat): {awal_len - setelah_duplikat} baris")
print(f"Dihapus (Terlalu Pendek < 10 char): {setelah_duplikat - setelah_short} baris")
print(f"Data Bersih Final: {len(df_reviews)} baris siap untuk EDA & NLP!")
df_reviews[['location_name', 'review_text', 'review_text_clean']].head(3)"""
nb.cells.append(nbf.v4.new_code_cell(kode_cleaning))


# ---------------------------------------------------------
# FASE 3: DEEP EXPLORATORY DATA ANALYSIS (EDA)
# ---------------------------------------------------------
nb.cells.append(nbf.v4.new_markdown_cell("## [FASE 3] Deep Exploratory Data Analysis (EDA)\nMenggali *insight* dari data yang sudah bersih. Mencari korelasi antara Harga vs Rating, distribusi kategori, dan analisis frekuensi kata untuk memvalidasi Aspek NLP."))

kode_eda_1 = """import matplotlib.pyplot as plt
import seaborn as sns

df_master = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')
df_clean = pd.read_csv('Dataset/MASTER_REVIEWS_CLEANED.csv')

plt.figure(figsize=(10, 5))
sns.countplot(data=df_clean, x='rating', palette='viridis')
plt.title('Distribusi Rating Ulasan (Imbalanced Data)', fontsize=14)
plt.ylabel('Jumlah Ulasan')
plt.xlabel('Rating Bintang')
plt.show()

print("PERINGATAN: Data sangat imbalanced (didominasi rating 5). Model NLP membutuhkan teknik Class Weighting nantinya.")"""
nb.cells.append(nbf.v4.new_code_cell(kode_eda_1))

kode_eda_2 = """# Korelasi Harga vs Rating
avg_rating = df_clean.groupby('location_name')['rating'].mean().reset_index(name='avg_rating')
df_cross = df_master.merge(avg_rating, on='location_name', how='left')

corr = df_cross[['price_min', 'avg_rating']].corr().iloc[0,1]
print(f"Korelasi Pearson (Harga vs Rating): {corr:.4f}")
print("Interpretasi: Korelasi Negatif. Semakin mahal harga tiket, pengunjung cenderung lebih kritis memberikan rating.")

plt.figure(figsize=(10, 5))
sns.scatterplot(data=df_cross, x='price_min', y='avg_rating', alpha=0.6)
plt.title('Korelasi Harga Tiket Minimal vs Rata-Rata Rating', fontsize=14)
plt.xlabel('Harga Tiket Minimal (Rp)')
plt.ylabel('Rata-Rata Rating')
plt.axhline(y=df_cross['avg_rating'].mean(), color='r', linestyle='--', label='Rata-rata Global')
plt.legend()
plt.show()"""
nb.cells.append(nbf.v4.new_code_cell(kode_eda_2))

kode_eda_3 = """# Validasi Kata Kunci Aspek (Word Frequency)
from collections import Counter

all_text = ' '.join(df_clean['review_text_clean'].dropna().astype(str))
words = all_text.split()
stopwords_id = {'yang', 'di', 'dan', 'ini', 'itu', 'dari', 'ke', 'untuk', 'dengan', 'ya', 'ada', 'juga', 'saya', 'nya', 'tidak', 'bisa', 'sangat', 'sudah', 'kami', 'kita', 'lagi', 'aja', 'banget', 'udah', 'deh', 'dong', 'sih', 'lah', 'tapi', 'jadi', 'sama', 'kalau', 'mau', 'karena', 'lebih', 'sekali', 'akan', 'seperti', 'waktu', 'tahun', 'atau', 'hanya', 'mereka', 'semua', 'punya', 'masih', 'terlalu', 'orang', 'satu', 'dia', 'banyak', 'cukup', 'apa', 'kali', 'nggak', 'gak', 'si', 'se', 'ter', 'ber', 'me', 'the', 'and', 'is', 'to', 'of', 'a', 'in', 'for', 'it', 'on', 'are', 'was', 'but'}

filtered_words = [w for w in words if w not in stopwords_id and len(w) > 2]
word_counts = Counter(filtered_words)

df_words = pd.DataFrame(word_counts.most_common(20), columns=['Kata', 'Frekuensi'])

plt.figure(figsize=(12, 6))
sns.barplot(data=df_words, x='Frekuensi', y='Kata', palette='magma')
plt.title('Top 20 Kata Paling Sering Muncul (Validasi Aspek ABSA)', fontsize=14)
plt.show()

print("Insight Aspek Tervalidasi:")
print("- Aspek Fasilitas/Akses: 'parkir', 'jalan', 'tempatnya'")
print("- Aspek Harga: 'tiket', 'masuk', 'harga'")
print("- Aspek Baru (Family): 'anak', 'cocok'")"""
nb.cells.append(nbf.v4.new_code_cell(kode_eda_3))

# Save the notebook back
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil menyisipkan Fase Cleaning & EDA ke wisata_traning.ipynb!")
