import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

SENTIMENT_MODEL_SOURCE = "tfidf_linearsvc"
SENTIMENT_MODEL_VERSION = "run_nlp_pipeline_v2"

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove punctuation, keep alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def label_sentimen(rating):
    if rating >= 4:
        return 'positif'
    elif rating == 3:
        return 'netral'
    else:   # 1 or 2
        return 'negatif'

def run_nlp_pipeline():
    print("="*65)
    print("FASE B: RETRAINING MODEL SENTIMEN DARI AWAL (34.150 DATA)")
    print("="*65)

    # 1. Load Data
    print("\n[1] Memuat dataset bersih...")
    df = pd.read_csv('Dataset/MASTER_REVIEWS_ENRICHED.csv', low_memory=False)
    
    # 2. Text Preprocessing Massal
    print("\n[2] Mencuci teks massal (NLP Preprocessing) untuk 34.150 baris...")
    df['review_nlp'] = df['review_text'].apply(clean_text)
    
    # Drop any rows that became empty after cleaning
    df = df[df['review_nlp'] != '']
    print(f"    -> Tersisa {len(df)} baris valid setelah teks dibersihkan.")

    # 3. Labeling Ground Truth
    print("\n[3] Melabeli Ground Truth dari Bintang/Rating...")
    df['sentimen'] = df['rating'].apply(label_sentimen)
    print("    Distribusi Label Sentimen:")
    print(df['sentimen'].value_counts().to_string())

    # 4. Train-Test Split
    print("\n[4] Train-Test Split (80:20 Stratified)...")
    X = df['review_nlp']
    y = df['sentimen']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 5. TF-IDF Vectorizer
    print("\n[5] Ekstraksi Fitur Teks (TF-IDF Vectorizer)...")
    tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    X_train_vec = tfidf.fit_transform(X_train)
    X_test_vec = tfidf.transform(X_test)
    print(f"    -> Kosakata yang berhasil dipelajari: {X_train_vec.shape[1]} kata/frasa")

    # 6. Train LinearSVC
    print("\n[6] Melatih Model Linear SVC (Machine Learning)...")
    svm_model = LinearSVC(C=1.0, max_iter=2000, class_weight='balanced', random_state=42)
    svm_model.fit(X_train_vec, y_train)

    # 7. Evaluasi Model
    print("\n[7] Evaluasi Akurasi Model Baru...")
    y_pred = svm_model.predict(X_test_vec)
    akurasi = accuracy_score(y_test, y_pred)
    print(f"    -> AKURASI MODEL: {akurasi*100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=['negatif', 'netral', 'positif']))

    # 8. Menerapkan Prediksi ke Seluruh Data
    print("\n[8] Memprediksi Sentimen untuk Seluruh Dataset...")
    X_all_vec = tfidf.transform(df['review_nlp'])
    df['sentimen_prediksi'] = svm_model.predict(X_all_vec)
    
    skor_map = {'positif': 1, 'netral': 0, 'negatif': -1}
    df['sentimen_skor'] = df['sentimen_prediksi'].map(skor_map)
    df['sentiment_model_source'] = SENTIMENT_MODEL_SOURCE
    df['sentiment_model_version'] = SENTIMENT_MODEL_VERSION
    df['sentiment_available'] = True

    # 9. Agregasi per Lokasi
    print("\n[9] Menghitung Skor Agregasi per Lokasi Wisata...")
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

    # 10. Save Output
    print("\n[10] Menyimpan File Akhir...")
    df.to_csv('Dataset/MASTER_REVIEWS_LABELED.csv', index=False)
    agg.to_csv('Dataset/SENTIMENT_SCORES_PER_LOKASI.csv', index=False)
    print("    -> Berhasil: Dataset/MASTER_REVIEWS_LABELED.csv")
    print("    -> Berhasil: Dataset/SENTIMENT_SCORES_PER_LOKASI.csv")
    print("="*65)
    print("PIPELINE SELESAI DENGAN SUKSES!")
    print("="*65)

if __name__ == "__main__":
    run_nlp_pipeline()
