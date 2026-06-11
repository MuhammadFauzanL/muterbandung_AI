import pandas as pd

print('=== AUDIT PREDIKSI SENTIMEN MODEL SVM ===\n')

try:
    df = pd.read_csv('Dataset/MASTER_REVIEWS_LABELED.csv', low_memory=False)
    agg = pd.read_csv('Dataset/SENTIMENT_SCORES_PER_LOKASI.csv')

    print('1. HASIL KLASIFIKASI MODEL (34.003 Ulasan):')
    dist = df['sentimen_prediksi'].value_counts()
    for k, v in dist.items():
        print(f'   - {k.capitalize()}: {v} ulasan ({v/len(df)*100:.1f}%)')

    print('\n2. KEMAMPUAN MODEL MENDETEKSI KRITIK TERSEMBUNYI (Contoh Kasus):')
    hidden_neg = df[(df['rating'] >= 4) & (df['sentimen_prediksi'] == 'negatif')]
    print(f'   Model menemukan {len(hidden_neg)} ulasan ber-rating tinggi yang gaya bahasanya negatif/mengkritik.')
    if not hidden_neg.empty:
        sample = hidden_neg['review_nlp'].head(3).tolist()
        for i, s in enumerate(sample):
            print(f'   -> Contoh {i+1}: "{s[:100]}..."')

    print('\n3. TOP 5 DESTINASI PALING POSITIF (Berdasarkan Skor Sentimen AI):')
    top5 = agg.head(5)
    for idx, row in top5.iterrows():
        print(f'   {idx+1}. {row["location_name"]} (Skor: {row["avg_sentimen_skor"]:.2f} | {row["total_ulasan"]} ulasan)')

    print('\n4. TOP 5 DESTINASI PALING NEGATIF (Berdasarkan Skor Sentimen AI):')
    bot5 = agg.tail(5)
    for idx, row in bot5.iterrows():
        print(f'   {idx+1}. {row["location_name"]} (Skor: {row["avg_sentimen_skor"]:.2f} | {row["total_ulasan"]} ulasan)')

except Exception as e:
    print(f'Error: {e}')
