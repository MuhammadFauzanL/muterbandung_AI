import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
import warnings

warnings.filterwarnings('ignore')

print("="*65)
print("FASE 5: BINARY SENTIMENT CLASSIFICATION (Positif vs Negatif)")
print("="*65)

# 1. Load Data
df = pd.read_csv('Dataset/MASTER_REVIEWS_NLP.csv')
print(f"Total baris awal: {len(df)}")

# 2. Hapus baris NULL
df = df.dropna(subset=['review_nlp'])
df = df[df['review_nlp'].astype(str).str.strip() != '']

# 3. LABELING BINER (Hapus Netral)
# Bintang 4-5 = Positif, Bintang 1-2 = Negatif. Bintang 3 = Drop.
df_binary = df[df['rating'] != 3].copy()
print(f"Total baris setelah menghapus Netral (rating 3): {len(df_binary)}")

def label_biner(rating):
    return 'positif' if rating >= 4 else 'negatif'

df_binary['sentimen'] = df_binary['rating'].apply(label_biner)
print("\\nDistribusi Kelas Biner:")
print(df_binary['sentimen'].value_counts())

# 4. Train-Test Split
X = df_binary['review_nlp'].astype(str)
y = df_binary['sentimen']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 5. TF-IDF & Training SVM
print("\\nMengekstraksi fitur dan melatih model LinearSVC...")
tfidf = TfidfVectorizer(max_features=8000, ngram_range=(1,2), min_df=2, sublinear_tf=True)
X_train_vec = tfidf.fit_transform(X_train)
X_test_vec  = tfidf.transform(X_test)

svm_model = LinearSVC(C=1.0, max_iter=2000, class_weight='balanced', random_state=42)
svm_model.fit(X_train_vec, y_train)

# 6. Evaluasi
y_pred = svm_model.predict(X_test_vec)
akurasi = accuracy_score(y_test, y_pred)
print(f"\\nAKURASI MODEL BINER: {akurasi*100:.2f}%")
print("\\nLaporan Klasifikasi:")
print(classification_report(y_test, y_pred))

# 7. Simpan model & hasil ke seluruh dataset Biner
df_binary['sentimen_prediksi'] = svm_model.predict(tfidf.transform(X))

# Simpan hasil untuk engine rekomendasi
df_binary.to_csv('Dataset/MASTER_REVIEWS_LABELED_BINARY.csv', index=False, encoding='utf-8')
print("✅ Selesai! Data tersimpan di 'Dataset/MASTER_REVIEWS_LABELED_BINARY.csv'")
