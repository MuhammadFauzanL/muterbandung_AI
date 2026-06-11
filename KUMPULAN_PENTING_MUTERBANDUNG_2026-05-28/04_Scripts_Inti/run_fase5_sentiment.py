import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

SENTIMENT_MODEL_SOURCE = "tfidf_linearsvc"
SENTIMENT_MODEL_VERSION = "run_fase5_sentiment"

print("="*65)
print("FASE 5: SENTIMENT LABELING & MODEL TRAINING (Baseline SVM)")
print("="*65)

# ============================================================
# LANGKAH 5A: PERBAIKAN DATA (Hapus 57 NULL)
# ============================================================
print("\n[5A] Perbaikan Data Pre-Training...")
df = pd.read_csv('Dataset/MASTER_REVIEWS_NLP.csv')
sebelum = len(df)
df = df.dropna(subset=['review_nlp'])
df = df[df['review_nlp'].astype(str).str.strip() != '']
sesudah = len(df)
print(f"  Baris sebelum: {sebelum} → Setelah hapus NULL: {sesudah}")
print(f"  Baris dihapus: {sebelum - sesudah} (wajar/tidak signifikan)")

# ============================================================
# LANGKAH 5B: SENTIMENT LABELING (Dari Rating)
# ============================================================
print("\n[5B] Sentiment Labeling dari Rating...")
def label_sentimen(rating):
    if rating >= 4:
        return 'positif'
    elif rating == 3:
        return 'netral'
    else:   # 1 atau 2
        return 'negatif'

df['sentimen'] = df['rating'].apply(label_sentimen)

print("  Distribusi Label Sentimen:")
print(df['sentimen'].value_counts().to_string())
print(f"\n  Proporsi:")
for label, count in df['sentimen'].value_counts().items():
    print(f"    {label}: {count} ({count/len(df)*100:.1f}%)")

# ============================================================
# LANGKAH 5C: TRAIN-TEST SPLIT (80:20 Stratified)
# ============================================================
print("\n[5C] Train-Test Split (80:20 Stratified)...")
X = df['review_nlp'].astype(str)
y = df['sentimen']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y   # Menjaga proporsi label di train & test
)
print(f"  Data Training: {len(X_train)} baris")
print(f"  Data Testing:  {len(X_test)} baris")

# ============================================================
# LANGKAH 5D: TF-IDF VECTORIZER
# ============================================================
print("\n[5D] TF-IDF Feature Extraction...")
tfidf = TfidfVectorizer(
    max_features=8000,          # Ambil 8000 kata paling relevan
    ngram_range=(1, 2),         # Unigram + Bigram agar konteks lebih kaya
    min_df=2,                   # Minimal muncul di 2 dokumen
    sublinear_tf=True           # Normalisasi TF agar tidak didominasi kata sangat sering
)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec  = tfidf.transform(X_test)
print(f"  Dimensi fitur TF-IDF: {X_train_vec.shape}")

# ============================================================
# LANGKAH 5E: MODEL SVM (Dengan Class Weighting - Antisipasi Imbalanced)
# ============================================================
print("\n[5E] Melatih Model Linear SVM (dengan class_weight='balanced')...")
svm_model = LinearSVC(
    C=1.0,
    max_iter=2000,
    class_weight='balanced',    # KRUSIAL: Mengatasi imbalanced data
    random_state=42
)
svm_model.fit(X_train_vec, y_train)
print("  Model selesai dilatih!")

# ============================================================
# LANGKAH 5F: EVALUASI MODEL
# ============================================================
print("\n[5F] Evaluasi Model pada Data Testing...")
y_pred = svm_model.predict(X_test_vec)

akurasi = accuracy_score(y_test, y_pred)
print(f"\n  Akurasi Keseluruhan: {akurasi*100:.2f}%")

print("\n  Laporan Klasifikasi per Label:")
print(classification_report(y_test, y_pred, target_names=['negatif', 'netral', 'positif']))

print("\n  Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred, labels=['negatif', 'netral', 'positif'])
cm_df = pd.DataFrame(cm,
                     index=['Aktual: negatif', 'Aktual: netral', 'Aktual: positif'],
                     columns=['Prediksi: negatif', 'Prediksi: netral', 'Prediksi: positif'])
print(cm_df.to_string())

# ============================================================
# LANGKAH 5G: SIMPAN HASIL PREDIKSI KE SELURUH DATA
# ============================================================
print("\n[5G] Menerapkan model ke seluruh dataset...")
X_all_vec = tfidf.transform(df['review_nlp'].astype(str))
df['sentimen_prediksi'] = svm_model.predict(X_all_vec)

# Skor numerik: positif=1, netral=0, negatif=-1
skor_map = {'positif': 1, 'netral': 0, 'negatif': -1}
df['sentimen_skor'] = df['sentimen_prediksi'].map(skor_map)
df['sentiment_model_source'] = SENTIMENT_MODEL_SOURCE
df['sentiment_model_version'] = SENTIMENT_MODEL_VERSION
df['sentiment_available'] = True

# ============================================================
# LANGKAH 5H: AGREGASI SKOR SENTIMEN PER LOKASI
# ============================================================
print("\n[5H] Menghitung Skor Sentimen rata-rata per Lokasi...")
agg = df.groupby('location_name').agg(
    total_ulasan=('review_nlp', 'count'),
    avg_sentimen_skor=('sentimen_skor', 'mean'),
    avg_rating=('rating', 'mean'),
    ulasan_positif=('sentimen_prediksi', lambda x: (x=='positif').sum()),
    ulasan_negatif=('sentimen_prediksi', lambda x: (x=='negatif').sum()),
).reset_index()

agg['sentimen_label_lokasi'] = agg['avg_sentimen_skor'].apply(
    lambda x: 'Sangat Positif' if x >= 0.6 else
              'Positif' if x >= 0.2 else
              'Netral' if x >= -0.2 else
              'Negatif' if x >= -0.6 else 'Sangat Negatif'
)
agg['sentiment_score'] = agg['avg_sentimen_skor']
agg['sentiment_model_source'] = SENTIMENT_MODEL_SOURCE
agg['sentiment_model_version'] = SENTIMENT_MODEL_VERSION
agg['sentiment_available'] = True

agg = agg.sort_values('avg_sentimen_skor', ascending=False)

print(f"\n  TOP 5 Lokasi PALING POSITIF:")
print(agg[['location_name', 'total_ulasan', 'avg_sentimen_skor', 'sentimen_label_lokasi']].head(5).to_string(index=False))

print(f"\n  TOP 5 Lokasi PALING NEGATIF (perlu perhatian):")
print(agg[['location_name', 'total_ulasan', 'avg_sentimen_skor', 'sentimen_label_lokasi']].tail(5).to_string(index=False))

# Simpan output
df.to_csv('Dataset/MASTER_REVIEWS_LABELED.csv', index=False, encoding='utf-8')
agg.to_csv('Dataset/SENTIMENT_SCORES_PER_LOKASI.csv', index=False, encoding='utf-8')

print("\n✅ File tersimpan:")
print("   - Dataset/MASTER_REVIEWS_LABELED.csv  (semua ulasan + label sentimen)")
print("   - Dataset/SENTIMENT_SCORES_PER_LOKASI.csv  (skor sentimen per lokasi)")
print("\n" + "="*65)
print("FASE 5 SELESAI! Model SVM Baseline berhasil dibangun.")
print("="*65)
