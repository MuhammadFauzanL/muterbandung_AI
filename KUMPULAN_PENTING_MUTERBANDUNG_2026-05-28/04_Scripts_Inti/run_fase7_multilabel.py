import pandas as pd
import numpy as np

SENTIMENT_MODEL_SOURCE = "tfidf_linearsvc"
SENTIMENT_MODEL_VERSION = "run_nlp_pipeline_v2"
SENTIMENT_UNAVAILABLE_SOURCE = "unavailable"

def run_multilabel_tagging():
    print("="*65)
    print("FASE 7: MULTI-LABEL ATTRIBUTE CLASSIFIER & DATABASE MERGING")
    print("="*65)

    # 1. Load Data
    print("[1] Memuat dataset...")
    df_reviews = pd.read_csv('Dataset/MASTER_REVIEWS_LABELED.csv', low_memory=False)
    df_master = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv', low_memory=False)
    df_sentimen = pd.read_csv('Dataset/SENTIMENT_SCORES_PER_LOKASI.csv', low_memory=False)

    # Pastikan review_nlp adalah string
    df_reviews['review_nlp'] = df_reviews['review_nlp'].fillna('').astype(str)

    # 2. Kamus Kategori (Keyword Dictionary)
    # Kita menggunakan kata berimbuhan bahasa Indonesia umum & bahasa gaul
    kamus_label = {
        'Alam': ['gunung', 'curug', 'hutan', 'pohon', 'danau', 'sejuk', 'kawah', 'alam', 'pemandangan', 'camping', 'kemah', 'pinus', 'air terjun'],
        'Ramah Anak': ['anak', 'bocil', 'keluarga', 'stroller', 'mainan', 'playground', 'balita', 'edukatif'],
        'Spot Foto': ['foto', 'instagramable', 'estetik', 'kamera', 'pemandangan', 'spot', 'selfie'],
        'Edukasi': ['sejarah', 'museum', 'belajar', 'edukasi', 'ilmu', 'budaya', 'pengetahuan', 'pemandu', 'guide'],
        'Kuliner': ['makan', 'minum', 'restoran', 'cafe', 'kuliner', 'enak', 'kopi', 'jajan', 'resto', 'warung'],
        'Belanja': ['belanja', 'oleh-oleh', 'pasar', 'mall', 'baju', 'kaos', 'souvenir', 'murah', 'belanjaan'],
        'Santai/Healing': ['healing', 'tenang', 'santai', 'damai', 'sunyi', 'ngadem', 'piknik', 'adem', 'rileks'],
        'Wahana Ekstrem': ['outbound', 'flying fox', 'atv', 'offroad', 'pacu adrenalin', 'ekstrem', 'seru', 'tantangan']
    }

    # 3. Proses Ekstraksi Frekuensi
    print("\n[2] Membaca 34.000 ulasan dan mencari frekuensi kata kunci...")
    
    # Fungsi pembantu untuk cek keywords
    def count_keywords(text, keywords):
        # returns 1 if ANY keyword is in text, else 0
        for kw in keywords:
            if kw in text:
                return 1
        return 0

    # Buat kolom dummy untuk setiap label di level ulasan
    for label, keywords in kamus_label.items():
        col_name = f'has_kw_{label}'
        df_reviews[col_name] = df_reviews['review_nlp'].apply(lambda x: count_keywords(x, keywords))

    # Agregasi ke level lokasi
    print("\n[3] Menghitung persentase kemunculan tag per lokasi...")
    agg_funcs = {'review_nlp': 'count'}
    for label in kamus_label.keys():
        agg_funcs[f'has_kw_{label}'] = 'sum'
        
    df_tags = df_reviews.groupby('location_name').agg(agg_funcs).reset_index()
    df_tags.rename(columns={'review_nlp': 'total_ulasan_tag'}, inplace=True)

    # 4. Filter Threshold & Pembuatan Multi-Label
    # Aturan: Jika > 8% ulasan membicarakan kata kunci tsb, berikan Tag
    threshold = 0.08 
    
    def generate_tags(row):
        tags = []
        total = row['total_ulasan_tag']
        if total == 0: return "[]"
        
        for label in kamus_label.keys():
            persentase = row[f'has_kw_{label}'] / total
            if persentase >= threshold:
                tags.append(label)
        
        # Jika tidak ada tag yg lolos (karena ulasan terlalu sedikit/spesifik)
        if len(tags) == 0:
            tags.append("Umum")
            
        return str(tags)

    df_tags['multi_labels'] = df_tags.apply(generate_tags, axis=1)
    df_tags = df_tags[['location_name', 'multi_labels']]

    # 5. Merging (Penggabungan 3 Tabel Utama)
    print("\n[4] Menggabungkan Master Data + Skor Sentimen + Multi-Labels...")
    
    # 5A. Merge Sentimen
    df_final = pd.merge(df_master, df_sentimen, on='location_name', how='left')
    
    # 5B. Merge Tags
    df_final = pd.merge(df_final, df_tags, on='location_name', how='left')
    
    # Bersihkan NaN (untuk lokasi yang belum punya ulasan)
    df_final['avg_sentimen_skor'] = df_final['avg_sentimen_skor'].fillna(0)
    df_final['total_ulasan'] = df_final['total_ulasan'].fillna(0)
    score_source = df_final['sentiment_score'] if 'sentiment_score' in df_final.columns else df_final['avg_sentimen_skor']
    df_final['sentiment_score'] = score_source.fillna(df_final['avg_sentimen_skor'])
    sentiment_available = df_final['total_ulasan'].fillna(0).astype(float).gt(0) & df_final['sentimen_label_lokasi'].fillna('').astype(str).str.strip().ne('')
    df_final['sentiment_available'] = sentiment_available
    source_column = df_final['sentiment_model_source'] if 'sentiment_model_source' in df_final.columns else pd.Series('', index=df_final.index)
    df_final['sentiment_model_source'] = source_column.fillna('').astype(str).str.strip()
    df_final['sentiment_model_source'] = df_final['sentiment_model_source'].mask(
        df_final['sentiment_model_source'].eq(''),
        np.where(sentiment_available, SENTIMENT_MODEL_SOURCE, SENTIMENT_UNAVAILABLE_SOURCE)
    )
    version_column = df_final['sentiment_model_version'] if 'sentiment_model_version' in df_final.columns else pd.Series('', index=df_final.index)
    df_final['sentiment_model_version'] = version_column.fillna('').astype(str).str.strip()
    df_final['sentiment_model_version'] = df_final['sentiment_model_version'].mask(
        df_final['sentiment_model_version'].eq(''),
        np.where(sentiment_available, SENTIMENT_MODEL_VERSION, '')
    )
    df_final['multi_labels'] = df_final['multi_labels'].fillna("['Umum']")

    # Rapikan kolom agar cantik
    kolom_penting = [
        'location_id', 'location_name', 'category', 'multi_labels', 
        'avg_sentimen_skor', 'total_ulasan', 'sentimen_label_lokasi',
        'sentiment_score', 'sentiment_model_source', 'sentiment_model_version', 'sentiment_available',
        'latitude', 'longitude', 'price_min', 'price_max', 'jam_buka', 'jam_tutup',
        'estimasi_durasi_menit', 'deskripsi_google'
    ]
    
    # Masukkan sisa kolom ke akhir
    sisa_kolom = [c for c in df_final.columns if c not in kolom_penting]
    df_final = df_final[kolom_penting + sisa_kolom]

    # 6. Save Database Final
    output_path = 'DATABASE_WISATA_FINAL_PARIPURNA.csv'
    df_final.to_csv(output_path, index=False)
    
    print(f"\n[5] SUKSES! Database Final Paripurna disimpan di: {output_path}")
    print(f"    Total Lokasi: {len(df_final)}")
    print("    Contoh Hasil Pelabelan:")
    print(df_final[['location_name', 'category', 'multi_labels', 'avg_sentimen_skor']].head(10).to_string())
    print("="*65)

if __name__ == "__main__":
    run_multilabel_tagging()
