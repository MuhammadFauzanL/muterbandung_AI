import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-135': {
            'description': "Taman Main Mili-Mili & Hutan Mycelia adalah wahana wisata malam interaktif di Grafika Cikole yang mengangkat tema peradaban jamur dengan instalasi cahaya, video mapping, dan treasure hunt di hutan pinus.",
            'jam_buka_weekday': '18:00',
            'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '18:00',
            'jam_tutup_weekend': '22:00'
        },
        'LOC-137': {
            'description': "Rumah Belanda Lembang adalah destinasi wisata tematik bertema Negeri Kincir Angin di Maribaya yang menawarkan spot foto arsitektur Belanda, sewa kostum tradisional, dan kuliner khas Eropa.",
            'jam_buka_weekday': '10:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '10:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-139': {
            'description': "Kawah Rengganis adalah kawah vulkanik di Rancabali yang menyuguhkan kolam rendam air panas alami, jembatan gantung ikonik Rengganis Suspension Bridge, dan wahana Keranjang Sultan.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-141': {
            'description': "Taman Wisata Bougenville di Gunung Puntang merupakan kawasan wisata alam yang menyuguhkan taman bunga, sungai Cigeureuh yang jernih, wahana flying fox, serta penginapan villa di ketinggian 1.200 mdpl.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-142': {
            'description': "Hejo Forest Ciwidey adalah kawasan camping dan glamping di lereng Gunung Patuha seluas 5,5 hektar yang menawarkan kolam rendam air panas alami di tengah suasana hutan sejuk bersuhu 12-16°C.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-143': {
            'description': "D'Riam Riverside Ciwidey adalah destinasi wisata tepi sungai di Pasirjambu yang memadukan penginapan, restoran, dan wahana petualangan alam seperti river tubing dan offroad dalam satu kawasan.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
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
    print("Batch 6 applied successfully.")

if __name__ == '__main__':
    main()
