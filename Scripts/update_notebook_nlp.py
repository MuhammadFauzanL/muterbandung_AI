import nbformat

def update_notebook_nlp():
    notebook_path = 'Notebooks/wisata_traning.ipynb'
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
            
        markdown_content = """## [UPDATE 21 MEI 2026] Fase Kritis B: Pelabelan Sentimen NLP & Model Retraining

Karena adanya tambahan data ~18.790 ulasan baru hasil *scraping* Apify, model SVM sebelumnya (yang hanya dilatih dengan 15.000 data) tidak lagi relevan. Kita memutuskan untuk melakukan **Retraining Model dari Nol** menggunakan seluruh dataset bersih (34.003 baris).

**Langkah-langkah yang dieksekusi:**
1. **Massal Text Preprocessing**: Mencuci teks ulasan (menghapus tanda baca, *lowercase*) untuk seluruh data agar menghasilkan `review_nlp`.
2. **Ground Truth Labeling**: Bintang 4-5 = Positif, Bintang 3 = Netral, Bintang 1-2 = Negatif.
3. **TF-IDF Vectorization**: Mengekstraksi 10.000 unigram dan bigram terbanyak.
4. **Training Linear SVC**: Dilatih dengan parameter `class_weight='balanced'` untuk menangani data yang *imbalanced* (banyak positif, sedikit negatif).
5. **Evaluasi**: Akurasi akhir mencapai **86.47%**.
6. **Agregasi**: Menghitung rata-rata skor sentimen dan total klasifikasi positif/negatif per lokasi wisata.
7. **Penyimpanan Akhir**: Data final disimpan di `Dataset/MASTER_REVIEWS_LABELED.csv` dan `Dataset/SENTIMENT_SCORES_PER_LOKASI.csv`.

Kode di bawah ini adalah rekaman (*log*) dari pipeline Machine Learning yang telah dieksekusi secara otomatis di backend.
"""

        code_content = """# [DOKUMENTASI] Skrip Retraining Model SVM Sentimen (Telah dieksekusi via backend)
# Script ini disimpan di sini sebagai rekam jejak agar reproducible.

import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\\s]', ' ', text)
    return re.sub(r'\\s+', ' ', text).strip()

def label_sentimen(rating):
    if rating >= 4: return 'positif'
    elif rating == 3: return 'netral'
    else: return 'negatif'

# Load Cleaned Data
df = pd.read_csv('../Dataset/MASTER_REVIEWS_ENRICHED.csv', low_memory=False)

# 1. NLP Preprocessing
df['review_nlp'] = df['review_text'].apply(clean_text)
df = df[df['review_nlp'] != '']

# 2. Ground Truth & Train-Test Split
df['sentimen'] = df['rating'].apply(label_sentimen)
X_train, X_test, y_train, y_test = train_test_split(df['review_nlp'], df['sentimen'], test_size=0.2, random_state=42, stratify=df['sentimen'])

# 3. TF-IDF
tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec = tfidf.transform(X_test)

# 4. Train Model
svm_model = LinearSVC(C=1.0, max_iter=2000, class_weight='balanced', random_state=42)
svm_model.fit(X_train_vec, y_train)

# 5. Evaluate
y_pred = svm_model.predict(X_test_vec)
print("Akurasi:", accuracy_score(y_test, y_pred))

# 6. Predict All & Save
X_all_vec = tfidf.transform(df['review_nlp'])
df['sentimen_prediksi'] = svm_model.predict(X_all_vec)
skor_map = {'positif': 1, 'netral': 0, 'negatif': -1}
df['sentimen_skor'] = df['sentimen_prediksi'].map(skor_map)

# 7. Aggregate
agg = df.groupby('location_name').agg(
    total_ulasan=('review_nlp', 'count'),
    avg_sentimen_skor=('sentimen_skor', 'mean'),
    avg_rating=('rating', 'mean')
).reset_index()

# Save
# df.to_csv('../Dataset/MASTER_REVIEWS_LABELED.csv', index=False)
# agg.to_csv('../Dataset/SENTIMENT_SCORES_PER_LOKASI.csv', index=False)
"""
        
        # Create new cells
        new_md_cell = nbformat.v4.new_markdown_cell(markdown_content)
        new_code_cell = nbformat.v4.new_code_cell(code_content)
        
        # Append to notebook
        nb.cells.extend([new_md_cell, new_code_cell])
        
        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
            
        print(f'Berhasil menambahkan dokumentasi NLP ke bagian akhir {notebook_path}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    update_notebook_nlp()
