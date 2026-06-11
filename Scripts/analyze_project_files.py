import os
import pandas as pd

def analyze_files():
    root = '.'
    dataset_dir = 'Dataset'
    
    files_to_check = []
    
    for f in os.listdir(root):
        if f.endswith('.csv') or f.endswith('.json') or f.endswith('.txt') or f.endswith('.xlsx'):
            if os.path.isfile(os.path.join(root, f)):
                files_to_check.append((root, f))
                
    if os.path.exists(dataset_dir):
        for f in os.listdir(dataset_dir):
            if f.endswith('.csv') or f.endswith('.json'):
                if os.path.isfile(os.path.join(dataset_dir, f)):
                    files_to_check.append((dataset_dir, f))
                    
    print('=== ANALISIS KEDUDUKAN FILE DALAM PIPELINE ===\n')
    
    for d, f in files_to_check:
        path = os.path.join(d, f)
        size_mb = os.path.getsize(path) / (1024*1024)
        
        category = 'Tidak Diketahui'
        
        if f == 'DATABASE_WISATA_FINAL_PARIPURNA.csv':
            category = '[CORE] Database Utama Sistem Rekomendasi'
        elif f == 'DATABASE_WISATA_DENGAN_METADATA.csv':
            category = '[CORE] Master Lokasi (Tanpa Sentimen)'
        elif f == 'MASTER_REVIEWS_ENRICHED.csv' and d == 'Dataset':
            category = '[CORE] Dataset NLP 34k Ulasan Bersih'
        elif 'apify' in f.lower() or 'scraper' in f.lower():
            category = '[Mentah] Hasil Scraping Langsung dari Apify/Extensi'
        elif f.startswith('dataset_cleaned'):
            category = '[Mentah-Manual] Data Batch Awal (Cleaned by User)'
        elif 'mentah' in f.lower():
            category = '[Mentah-Manual] Data Batch Awal (Belum dibersihkan)'
        elif f == 'MASTER_REVIEWS_LABELED.csv':
            category = '[Proses] Hasil Prediksi Sentimen dari IndoBERT'
        elif 'final_lengkap' in f.lower() or 'engine.csv' in f.lower():
            category = '[Usang/Arsip] Versi Master Database Lama'
        elif 'hotel' in f.lower():
            category = '[Kandidat Eksternal] Database Hotel (Untuk Fase 8)'
        elif 'mismatched' in f.lower() or 'mapping' in f.lower():
            category = '[Log/Temporary] Catatan error atau mapping'
        elif f == 'SENTIMENT_SCORES_PER_LOKASI.csv':
            category = '[Proses] Rapor Sentimen dari NLP'
        else:
            try:
                if f.endswith('.csv'):
                    df = pd.read_csv(path, nrows=1)
                    if 'review_nlp' in df.columns:
                        category = '[Proses/Arsip] Riwayat NLP/Cleansing'
                    elif 'location_name' in df.columns and 'rating' in df.columns:
                        category = '[Proses/Arsip] Arsip Penggabungan Ulasan'
            except:
                pass
                
        print(f'{category: <60} | {d}/{f} ({size_mb:.2f} MB)')

if __name__ == '__main__':
    analyze_files()
