import pandas as pd
import json

def append_new_locations():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_locs = pd.read_csv(db_path, low_memory=False)
    
    # Check if LOC-233 or LOC-234 exists
    if 'LOC-233' not in df_locs['location_id'].values:
        new_row1 = {
            'location_id': 'LOC-233',
            'location_name': 'Kampung Wisata Pangjugjugan',
            'latitude': -6.8920,
            'longitude': 107.8280,
            'price_min': 0,
            'price_max': 0,
            'price_type': 'Berbayar',
            'category': 'Rekreasi Alam',
            'subcategory': 'Ekowisata & Outbound',
            'jam_buka': '09:00',
            'jam_tutup': '16:00',
            'estimasi_durasi_menit': 180,
            'tags_sintetis': 'Keluarga, Alam, Edukasi, Outbound',
            'deskripsi_google': 'Wisata alam dan edukasi di kaki Gunung Kareumbi yang menawarkan waterpark bukit, flying fox, dan kegiatan pertanian organik.',
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '16:00',
            'sumber_deskripsi': 'internet_research_verified',
            'sumber_jam': 'internet_research_verified',
            'status_deskripsi': 'filled_from_reliable_source',
            'status_jam': 'general_schedule_used_for_both',
            'catatan_jam': 'Jadwal umum digunakan untuk weekday dan weekend.'
        }
        df_locs = pd.concat([df_locs, pd.DataFrame([new_row1])], ignore_index=True)
        print("Ditambahkan: Kampung Wisata Pangjugjugan")
        
    if 'LOC-234' not in df_locs['location_id'].values:
        new_row2 = {
            'location_id': 'LOC-234',
            'location_name': 'Perkebunan Teh Rancabali',
            'latitude': -7.154167,
            'longitude': 107.371111,
            'price_min': 0,
            'price_max': 0,
            'price_type': 'Gratis',
            'category': 'Rekreasi Alam',
            'subcategory': 'Perkebunan Teh',
            'jam_buka': '07:00',
            'jam_tutup': '17:00',
            'estimasi_durasi_menit': 120,
            'tags_sintetis': 'Alam, Pemandangan, Santai, Fotografi',
            'deskripsi_google': 'Perkebunan teh yang menawarkan pemandangan hijau asri, fasilitas tea walk, dan wisata edukasi proses pengolahan teh.',
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00',
            'sumber_deskripsi': 'internet_research_verified',
            'sumber_jam': 'internet_research_verified',
            'status_deskripsi': 'filled_from_reliable_source',
            'status_jam': 'general_schedule_used_for_both',
            'catatan_jam': 'Jadwal umum digunakan untuk weekday dan weekend.'
        }
        df_locs = pd.concat([df_locs, pd.DataFrame([new_row2])], ignore_index=True)
        print("Ditambahkan: Perkebunan Teh Rancabali")
        
    df_locs.to_csv(db_path, index=False)
    # also export to XLSX
    df_locs.to_excel(db_path.replace('.csv', '.xlsx'), index=False, engine='openpyxl')
    print("Master database diperbarui dan diekspor ke XLSX.")


def process_reviews(file_path):
    print(f"\nMemproses: {file_path}")
    try:
        df = pd.read_csv(file_path, low_memory=False)
    except FileNotFoundError:
        print("File tidak ditemukan.")
        return
        
    initial_rows = len(df)
    
    # 1. Deletions
    to_delete = [
        'Punclut cafe lereng',
        'TOKO GOBERZ AUDIO MOBIL 97',
        'Cikahuripan',
        'Curug Ngebul Cianjur Selatan',
        'Curug Walanda',
        'Palayangan River',
        'Punclut Puncak',
        'Taman Rusa'
    ]
    df = df[~df['location_name'].isin(to_delete)]
    deleted_count = initial_rows - len(df)
    print(f"Berhasil menghapus {deleted_count} baris dari 8 lokasi yang tidak relevan.")
    
    # 2. Manual User Mapping
    manual_mapping = {
        'Air Terjun Anom': 'Curug Anom',
        'CURUG BATU TEMPLEK CISANGGARUNG': 'Curug Batu Templek',
        'Hutan Mycelia Wahana Edukasi & Interaktif': 'Taman Main Mili-Mili & Hutan Mycelia',
        'KAWAH CIBUNI Rengganis': 'Kawah Rengganis Ciwidey',
        'MUARA RAHONG HILL\'S': 'Muara Rahong Hills',
        'Gn. Hawu': 'Tebing Gunung Hawu'
    }
    
    # 3. Load Auto Mapping from previous step
    try:
        with open('proposed_location_mapping.json') as f:
            auto_mapping = json.load(f)['mapping']
    except:
        auto_mapping = {}
        print("Warning: JSON mapping otomatis tidak ditemukan.")
    
    # Remove wrong auto-mappings that were overridden by user (or deleted)
    for k in list(auto_mapping.keys()):
        if k in to_delete or k in manual_mapping:
            del auto_mapping[k]
    
    # Merge mappings
    final_mapping = {**auto_mapping, **manual_mapping}
    
    # Apply mapping
    mapped_count = df['location_name'].isin(final_mapping.keys()).sum()
    df['location_name'] = df['location_name'].replace(final_mapping)
    print(f"Berhasil menormalisasi {mapped_count} baris ulasan.")
    
    # Final Validation
    df_locs = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv', low_memory=False)
    master_locs = set(df_locs['location_name'].unique())
    review_locs = set(df['location_name'].unique())
    mismatches = list(review_locs - master_locs)
    
    if len(mismatches) == 0:
        print("VERIFIKASI SUKSES: 100% lokasi ulasan cocok dengan database master.")
    else:
        print(f"WARNING: Masih ada {len(mismatches)} lokasi yang tidak cocok: {mismatches}")
    
    df.to_csv(file_path, index=False)
    print(f"Selesai menyimpan {file_path}. Total baris akhir: {len(df)}")

if __name__ == "__main__":
    append_new_locations()
    process_reviews('MASTER_REVIEWS_ENRICHED.csv')
    process_reviews('MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv')
