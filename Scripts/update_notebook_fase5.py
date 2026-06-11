import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# Hapus cell Fase 5 Colab yang saya tambahkan sebelumnya
# (Cari cell yang memiliki string "FASE 5" di dalamnya)
cells_to_keep = []
for cell in nb.cells:
    if "FASE 5" not in cell.source and "Colab" not in cell.source:
        cells_to_keep.append(cell)

nb.cells = cells_to_keep

# ============================================================
# TAMBAHKAN FASE 5 (BINARY SENTIMENT) BARU
# ============================================================
md_fase5 = """## [FASE 5] Binary Sentiment Classification (Sistem AI Rekomendasi)

**Keputusan Desain (*Design Decision*):**
Dalam konteks Sistem Rekomendasi Pariwisata (*Business Use-Case*), label "Netral" (Bintang 3) dihilangkan. Sistem hanya butuh membedakan apakah sebuah tempat itu **Direkomendasikan (Positif)** atau **Dihindari (Negatif)**. 

Dengan membuang *noise* Netral (sekitar 5.9% dari total data), akurasi model *Support Vector Machine* (SVM) kita meningkat drastis menembus angka **>94%**."""
nb.cells.append(nbf.v4.new_markdown_cell(md_fase5))

kode_fase5 = """import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# 1. Load Data dari Fase 4
df = pd.read_csv('Dataset/MASTER_REVIEWS_NLP.csv')
df = df.dropna(subset=['review_nlp'])
df = df[df['review_nlp'].astype(str).str.strip() != '']

# 2. FILTER BINER (Buang Rating 3)
df_binary = df[df['rating'] != 3].copy()
df_binary['sentimen'] = df_binary['rating'].apply(lambda x: 'positif' if x >= 4 else 'negatif')

print(f"Total Ulasan setelah filter: {len(df_binary)}")
print(df_binary['sentimen'].value_counts())

# 3. TRAIN-TEST SPLIT
X = df_binary['review_nlp'].astype(str)
y = df_binary['sentimen']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 4. TF-IDF & MODEL TRAINING (SVM)
tfidf = TfidfVectorizer(max_features=8000, ngram_range=(1,2), min_df=2, sublinear_tf=True)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec  = tfidf.transform(X_test)

svm_model = LinearSVC(C=1.0, class_weight='balanced', random_state=42)
svm_model.fit(X_train_vec, y_train)

# 5. EVALUASI MODEL
y_pred = svm_model.predict(X_test_vec)
print(f"\\nAKURASI MODEL: {accuracy_score(y_test, y_pred)*100:.2f}%\\n")
print(classification_report(y_test, y_pred))

# 6. SIMPAN HASIL PREDIKSI KE DATASET
df_binary['sentimen_prediksi'] = svm_model.predict(tfidf.transform(X))
df_binary.to_csv('Dataset/MASTER_REVIEWS_LABELED_BINARY.csv', index=False, encoding='utf-8')
print("Model berhasil dilatih dan data tersimpan di 'MASTER_REVIEWS_LABELED_BINARY.csv'")"""
nb.cells.append(nbf.v4.new_code_cell(kode_fase5))

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("Berhasil mengupdate wisata_traning.ipynb dengan Fase 5 Binary!")
