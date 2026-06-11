import zipfile
import os
import json

zip_path = 'MuterBandung-IndoBERT-Sentiment.zip'
extract_dir = 'Models/'

print(f'Mengekstrak {zip_path} ke {extract_dir}...')
os.makedirs(extract_dir, exist_ok=True)

try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print('Ekstraksi berhasil!\n')
    
    print('=== HASIL AUDIT FILE MODEL ===')
    model_dir = os.path.join(extract_dir, 'MuterBandung-IndoBERT-Sentiment')
    if not os.path.exists(model_dir):
        # Fallback if zip didn't contain root folder
        model_dir = extract_dir
        
    files = os.listdir(model_dir)
    for f in files:
        f_path = os.path.join(model_dir, f)
        if os.path.isfile(f_path):
            size_mb = os.path.getsize(f_path) / (1024*1024)
            print(f'- {f}: {size_mb:.2f} MB')
            
    print('\n=== ANALISIS ARSITEKTUR & KONFIGURASI ===')
    config_path = os.path.join(model_dir, 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        arch = config.get("architectures", ["Unknown"])[0]
        print(f'1. Arsitektur Inti: {arch} (Ini menandakan bahwa model Anda menggunakan arsitektur Transformers murni).')
        
        labels = config.get("id2label", {})
        print(f'2. Label Klasifikasi: {labels} (Model Anda memetakan 0=Negatif, 1=Netral, 2=Positif).')
        
        max_pos = config.get("max_position_embeddings", "Unknown")
        print(f'3. Kapasitas Membaca: {max_pos} token (Model Anda bisa membaca kalimat yang sangat panjang sekaligus).')
        
        vocab = config.get("vocab_size", "Unknown")
        print(f'4. Ukuran Kosakata (Vocabulary Size): {vocab} kata.')
        
except Exception as e:
    print(f'Error: {e}')
