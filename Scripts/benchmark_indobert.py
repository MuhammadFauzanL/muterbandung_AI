import pandas as pd
from transformers import pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split
import warnings
import time

warnings.filterwarnings('ignore')

print("="*65)
print("BENCHMARK INDOBERT UNTUK SENTIMEN NETRAL")
print("="*65)

# 1. Load Data
df = pd.read_csv('Dataset/MASTER_REVIEWS_NLP.csv')
df = df.dropna(subset=['review_nlp'])
df = df[df['review_nlp'].astype(str).str.strip() != '']

def label_sentimen(rating):
    if rating >= 4: return 'positif'
    elif rating == 3: return 'netral'
    else: return 'negatif'

df['sentimen'] = df['rating'].apply(label_sentimen)

# 2. Ambil subset data (500 sampel) untuk pengujian cepat
# Kita fokus pada pengujian seimbang agar bisa lihat kemampuan mendeteksi 'netral'
df_neg = df[df['sentimen'] == 'negatif'].sample(100, random_state=42)
df_net = df[df['sentimen'] == 'netral'].sample(100, random_state=42)
df_pos = df[df['sentimen'] == 'positif'].sample(100, random_state=42)

df_sample = pd.concat([df_neg, df_net, df_pos]).sample(frac=1, random_state=42)

print(f"Menggunakan {len(df_sample)} sampel seimbang (100 Positif, 100 Netral, 100 Negatif)")

# 3. Load Pre-trained IndoBERT Sentiment Model
print("\\nLoading Pre-trained IndoBERT Model (mdhugol/indonesia-bert-sentiment-classification)...")
print("Membutuhkan waktu beberapa detik untuk download model...")
# Model ini outputnya: LABEL_0 (Positive), LABEL_1 (Neutral), LABEL_2 (Negative)
sentiment_pipeline = pipeline(
    "sentiment-analysis", 
    model="mdhugol/indonesia-bert-sentiment-classification", 
    tokenizer="mdhugol/indonesia-bert-sentiment-classification"
)

# 4. Fungsi Mapping
def map_indobert_label(label):
    if label == 'LABEL_0': return 'positif'
    elif label == 'LABEL_1': return 'netral'
    elif label == 'LABEL_2': return 'negatif'
    return 'netral'

# 5. Prediksi
print("\\nMenjalankan inferensi IndoBERT pada 300 sampel...")
start = time.time()
teks_list = df_sample['review_text_clean'].astype(str).tolist() # Menggunakan clean text, BERT lebih suka kalimat utuh
predictions = sentiment_pipeline(teks_list, truncation=True, max_length=512)
elapsed = time.time() - start
print(f"Selesai dalam {elapsed:.1f} detik.")

y_true = df_sample['sentimen'].tolist()
y_pred = [map_indobert_label(p['label']) for p in predictions]

# 6. Evaluasi
print("\\n" + "="*50)
print("HASIL EVALUASI INDOBERT (300 Sampel Seimbang)")
print("="*50)
print(f"Akurasi: {accuracy_score(y_true, y_pred)*100:.2f}%\\n")
print(classification_report(y_true, y_pred, target_names=['negatif', 'netral', 'positif']))

print("\\nKesimpulan Sementara:")
print("Cek F1-Score pada baris 'netral'. Jika jauh di atas 0.17 (hasil SVM tadi),")
print("maka IndoBERT memang terbukti lebih canggih dalam menangkap nuansa bahasa!")
