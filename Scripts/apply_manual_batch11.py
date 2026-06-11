import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-230': {
            'description': "Kampung wisata Buricak Burinong adalah destinasi wisata alam berwarna-warni di pesisir Waduk Jatigede Sumedang yang menawarkan keindahan panorama waduk, spot Masjid Al-Kamil, serta aktivitas paralayang.",
            'jam_buka_weekday': '06:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '06:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-232': {
            'description': "Kampung Wisata Pangjugjugan adalah destinasi ekowisata dan edukasi pedesaan di kaki Gunung Kareumbi Sumedang yang menyuguhkan suasana hutan pinus rindang, kolam renang, serta peternakan.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '16:00'
        },
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            if u.get('description') is not None:
                df_db.loc[idx, 'description'] = u['description']
            df_db.loc[idx, 'jam_buka_weekday'] = u['jam_buka_weekday']
            df_db.loc[idx, 'jam_tutup_weekday'] = u['jam_tutup_weekday']
            df_db.loc[idx, 'jam_buka_weekend'] = u['jam_buka_weekend']
            df_db.loc[idx, 'jam_tutup_weekend'] = u['jam_tutup_weekend']
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 11 applied successfully.")

if __name__ == '__main__':
    main()
