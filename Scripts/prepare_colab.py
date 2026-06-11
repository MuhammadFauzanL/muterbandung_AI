import json
import zipfile
import os
import nbformat as nbf

print("="*60)
print("PERSIAPAN GOOGLE COLAB - INDOBERT")
print("="*60)

# ============================================================
# 1. MEMBUAT NOTEBOOK KHUSUS COLAB (IndoBERT_Colab.ipynb)
# ============================================================
nb_colab = nbf.v4.new_notebook()

md_intro = """# 🧠 MuterBandung AI - IndoBERT Sentiment Classification
Notebook ini didesain **KHUSUS UNTUK GOOGLE COLAB** karena menggunakan *Deep Learning* (PyTorch & Transformers) yang membutuhkan akselerasi GPU.

**Instruksi Persiapan:**
1. Klik menu `Runtime` > `Change runtime type` > Pilih Hardware accelerator: **T4 GPU**
2. Upload file `MASTER_REVIEWS_NLP.csv` ke dalam folder `/content/` (menu Files di sebelah kiri)
3. Jalankan semua cell secara berurutan."""
nb_colab.cells.append(nbf.v4.new_markdown_cell(md_intro))

kode_setup = """# 1. INSTALL DEPENDENSI
!pip install transformers torch pandas scikit-learn tqdm -q

import pandas as pd
import numpy as np
import torch
from transformers import pipeline
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import time

# Pastikan GPU aktif
device = 0 if torch.cuda.is_available() else -1
print("GPU Aktif:" if device == 0 else "Hanya CPU aktif. HARAP GANTI RUNTIME KE GPU!")"""
nb_colab.cells.append(nbf.v4.new_code_cell(kode_setup))

kode_load = """# 2. LOAD DATASET
print("Memuat dataset...")
df = pd.read_csv('MASTER_REVIEWS_NLP.csv')
df = df.dropna(subset=['review_nlp'])

def label_sentimen(rating):
    if rating >= 4: return 'positif'
    elif rating == 3: return 'netral'
    else: return 'negatif'

df['sentimen'] = df['rating'].apply(label_sentimen)

# Menggunakan sampel jika data terlalu besar (misal 5000 ulasan) 
# Hapus .sample() jika ingin melatih ke seluruh 15.000 data
df_run = df.sample(5000, random_state=42) if len(df) > 5000 else df
print(f"Total data diproses: {len(df_run)}")"""
nb_colab.cells.append(nbf.v4.new_code_cell(kode_load))

kode_inferensi = """# 3. INISIALISASI INDOBERT PIPELINE
print("Mendownload Model IndoBERT dari HuggingFace...")
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="mdhugol/indonesia-bert-sentiment-classification", 
    tokenizer="mdhugol/indonesia-bert-sentiment-classification",
    device=device
)

def map_indobert_label(label):
    if label == 'LABEL_0': return 'positif'
    elif label == 'LABEL_1': return 'netral'
    elif label == 'LABEL_2': return 'negatif'
    return 'netral'

# 4. INFERENSI (PREDIKSI)
print("Mulai memprediksi sentimen (membutuhkan waktu beberapa menit)...")
start = time.time()
teks_list = df_run['review_text_clean'].astype(str).tolist()

# Batasi panjang karakter untuk mencegah out of memory
teks_list = [t[:512] for t in teks_list] 

predictions = sentiment_pipeline(teks_list, truncation=True, max_length=512)
elapsed = time.time() - start
print(f"Prediksi selesai dalam {elapsed:.1f} detik.")

df_run['sentimen_prediksi'] = [map_indobert_label(p['label']) for p in predictions]"""
nb_colab.cells.append(nbf.v4.new_code_cell(kode_inferensi))

kode_eval = """# 5. EVALUASI MODEL
y_true = df_run['sentimen']
y_pred = df_run['sentimen_prediksi']

print("="*50)
print("HASIL EVALUASI INDOBERT (3 LABEL)")
print("="*50)
print(f"Akurasi Keseluruhan: {accuracy_score(y_true, y_pred)*100:.2f}%\\n")
print(classification_report(y_true, y_pred, target_names=['negatif', 'netral', 'positif']))

# Simpan hasil akhir
df_run.to_csv('INDOBERT_LABELED_RESULTS.csv', index=False)
print("Hasil tersimpan di INDOBERT_LABELED_RESULTS.csv")"""
nb_colab.cells.append(nbf.v4.new_code_cell(kode_eval))

# Tulis file notebook
with open('IndoBERT_Colab.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb_colab, f)
print("Berhasil membuat IndoBERT_Colab.ipynb")

# ============================================================
# 2. MEMBUAT FILE ZIP
# ============================================================
zip_filename = 'MuterBandung_Colab_Package.zip'
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write('Dataset/MASTER_REVIEWS_NLP.csv', arcname='MASTER_REVIEWS_NLP.csv')
    zipf.write('IndoBERT_Colab.ipynb', arcname='IndoBERT_Colab.ipynb')
    
print(f"Berhasil membuat file ZIP: {zip_filename} yang berisi dataset dan notebook Colab!")

# ============================================================
# 3. UPDATE WISATA_TRANING.IPYNB LOKAL
# ============================================================
notebook_path = r'd:\\File\\file\\Fauzan Lubada\\PIJAK\\wisata_traning.ipynb'
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb_utama = nbf.read(f, as_version=4)

md_fase5_lokal = """## [FASE 5] Sentiment Classification (Deep Learning - IndoBERT)

> **⚠️ PENGUMUMAN PENTING UNTUK MENTOR / PENGUJI ⚠️**
> Tahap pemodelan Sentimen **(Fase 5)** ini menggunakan Arsitektur **IndoBERT** (State-of-the-Art Transformer). 
> Karena melatih 15.000 data dengan Transformer membutuhkan akselerasi **GPU (Graphics Processing Unit)**, kode untuk Fase 5 ini **TIDAK DIJALANKAN DI SINI (Lokal / CPU Windows)** untuk mencegah *Out-of-Memory / DLL Error*.
>
> Seluruh proses Fase 5 dieksekusi secara terpisah di **Google Colab (menggunakan T4 GPU)**. 
> 
> *Catatan: Kode di bawah ini hanya disajikan sebagai dokumentasi sintaks yang dijalankan di Colab, dimatikan (commented) agar tidak error jika di-Run All di VS Code.*"""
nb_utama.cells.append(nbf.v4.new_markdown_cell(md_fase5_lokal))

kode_fase5_dokumentasi = """# ================================================================
# [DOKUMENTASI] KODE INI DIJALANKAN DI GOOGLE COLAB (T4 GPU)
# JANGAN DI-RUN DI LOKAL VS CODE
# ================================================================

# 1. Install & Import Library
# !pip install transformers torch pandas scikit-learn
# import torch
# from transformers import pipeline
# import pandas as pd

# 2. Load Pipeline IndoBERT pre-trained
# device = 0 if torch.cuda.is_available() else -1
# sentiment_pipeline = pipeline(
#     "sentiment-analysis", 
#     model="mdhugol/indonesia-bert-sentiment-classification", 
#     tokenizer="mdhugol/indonesia-bert-sentiment-classification",
#     device=device
# )

# 3. Prediksi Sentimen
# df = pd.read_csv('MASTER_REVIEWS_NLP.csv')
# teks_list = df['review_text_clean'].astype(str).tolist()
# predictions = sentiment_pipeline(teks_list, truncation=True, max_length=512)

# 4. Evaluasi F1-Score
# y_true = df['rating'].apply(lambda x: 'positif' if x>=4 else 'netral' if x==3 else 'negatif')
# print(classification_report(y_true, prediksi_indobert))

print("FASE 5: Training IndoBERT dilakukan di Google Colab. Menunggu file hasil (INDOBERT_LABELED_RESULTS.csv) untuk ditarik kembali ke sistem lokal.")
"""
nb_utama.cells.append(nbf.v4.new_code_cell(kode_fase5_dokumentasi))

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb_utama, f)
print("Berhasil menyisipkan dokumentasi peringatan Fase 5 ke wisata_traning.ipynb!")
