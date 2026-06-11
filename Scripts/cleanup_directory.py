import os
import shutil
import glob

def move_files(file_list, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    moved_count = 0
    for file_path in file_list:
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            dest_path = os.path.join(dest_folder, filename)
            
            # Avoid overwriting or moving if it's already there
            if not os.path.exists(dest_path):
                shutil.move(file_path, dest_path)
                moved_count += 1
                print(f"  [Moved] {filename} -> {dest_folder}")
            else:
                print(f"  [Skip] {filename} sudah ada di {dest_folder}")
    return moved_count

def run_cleanup():
    print("="*60)
    print("MUTERBANDUNG DIRECTORY CLEANUP SCRIPT")
    print("="*60)
    
    raw_dir = 'Dataset/1_Raw_Data'
    inter_dir = 'Dataset/2_Intermediate'
    docs_dir = 'Dokumentasi_Sistem'
    models_dir = 'Models'
    
    # 1. Pindahkan Mentah (Root)
    print("\n[1] Memindahkan Data Mentah & Scraping...")
    mentah_files = glob.glob('dataset_Google-Maps-Reviews-Scraper_*.csv') + \
                   glob.glob('Dataset/dataset_Google-Maps-Reviews-Scraper_*.csv') + \
                   glob.glob('Dataset/apify_reviews_*.csv') + \
                   glob.glob('Dataset/apify_reviews_*.json') + \
                   glob.glob('Dataset/apify_jam_buka_semua_lokasi_raw.csv') + \
                   ['dataset_hotel_cimahi_semua_kolom.csv'] + \
                   glob.glob('Dataset/dataset_mentah_*.csv') + \
                   glob.glob('Dataset/datatset_mentah_*.csv') + \
                   glob.glob('Dataset/dataset_cleaned_*.csv') + \
                   glob.glob('Wisata-20*.zip')
    
    move_files(mentah_files, raw_dir)
    
    # 2. Pindahkan Intermediate / Usang
    print("\n[2] Memindahkan Data Proses & Versi Usang...")
    inter_files = [
        'DATABASE_MUTERBANDUNG_ENGINE.csv',
        'DATABASE_WISATA_FINAL_LENGKAP.csv',
        'DATABASE_WISATA_DENGAN_METADATA.xlsx',
        'mismatched_locations.txt',
        'proposed_location_mapping.json',
        'Dataset/MASTER_REVIEWS_CLEANED.csv',
        'Dataset/MASTER_REVIEWS_FINAL.csv',
        'Dataset/master_reviews_gabungan.csv',
        'Dataset/MASTER_REVIEWS_LABELED_BINARY.csv',
        'Dataset/MASTER_REVIEWS_NLP.csv',
        'MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv',
        'DATABASE_WISATA_VERIFIKASI_INTERNET_BATCH1.xlsx'
    ]
    move_files(inter_files, inter_dir)
    
    # 3. Pindahkan Dokumentasi & File Konteks
    print("\n[3] Memindahkan Dokumentasi & File Konteks...")
    doc_files = [
        'GEMINI_WEB_CONTEXT_PROMPT.md',
        'SKILL_CONTEXT_MUTERBANDUNG.md'
    ]
    
    # Pindahkan foto WA ke Dokumentasi
    wa_photos = glob.glob('Foto/WhatsApp Image*.jpeg')
    doc_files.extend(wa_photos)
    
    move_files(doc_files, docs_dir)
    
    # 4. Pindahkan Model Zip
    print("\n[4] Merapikan File Models...")
    model_files = [
        'MuterBandung-IndoBERT-Sentiment.zip',
        'MuterBandung_Colab_Package.zip'
    ]
    move_files(model_files, models_dir)
    
    print("\n[5] Membersihkan folder kosong (opsional)...")
    if os.path.exists('Foto') and not os.listdir('Foto'):
        os.rmdir('Foto')
        print("  [Deleted] Folder 'Foto' (sudah kosong)")
        
    print("="*60)
    print("BERSIH-BERSIH SELESAI!")
    print("Silakan cek File Explorer/VS Code Anda, sekarang jauh lebih rapi.")
    print("="*60)

if __name__ == '__main__':
    run_cleanup()
