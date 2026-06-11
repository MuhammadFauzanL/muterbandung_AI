import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-083': {
            'description': "Stone Garden Citatah adalah geopark berupa hamparan formasi batuan kapur purba berusia 20-30 juta tahun di puncak Gunung Masigit, Cipatat, yang menyuguhkan panorama perbukitan eksotis.",
            'jam_buka_weekday': '06:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '06:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-086': {
            'description': None,  # already has description
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-095': {
            'description': None,  # already has description
            'jam_buka_weekday': '05:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-096': {
            'description': None,  # already has description
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-098': {
            'description': "Taman Musik Centrum adalah taman tematik di Bandung seluas 4.200 m² yang memiliki tugu gitar raksasa sebagai monumen peringatan tragedi konser 2008 serta berfungsi sebagai ruang kreativitas komunitas musik lokal.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-105': {
            'description': "The Lodge Maribaya merupakan destinasi wisata alam instagramable di hutan pinus Lembang yang menawarkan beragam wahana foto ikonik seperti balon udara dan zip bike serta panorama pegunungan Bandung.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            if u['description'] is not None:
                df_db.loc[idx, 'description'] = u['description']
            df_db.loc[idx, 'jam_buka_weekday'] = u['jam_buka_weekday']
            df_db.loc[idx, 'jam_tutup_weekday'] = u['jam_tutup_weekday']
            df_db.loc[idx, 'jam_buka_weekend'] = u['jam_buka_weekend']
            df_db.loc[idx, 'jam_tutup_weekend'] = u['jam_tutup_weekend']
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 4 applied successfully.")

if __name__ == '__main__':
    main()
