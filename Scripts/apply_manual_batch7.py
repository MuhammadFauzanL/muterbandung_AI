import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-146': {
            'description': "Taman Love Soreang adalah destinasi wisata bertema cinta di perbukitan Soreang yang menawarkan ornamen hati, kolam renang Aurora berbentuk hati, playground, serta panorama city light Kota Bandung.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-149': {
            'description': "Taman Wisata Alam Cimanggu adalah kawasan pemandian air panas alami di ketinggian 1.100-1.500 mdpl dari sumber Gunung Patuha yang dipercaya berkhasiat mengandung mineral kalsium dan litium.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-150': {
            'description': "Southland Camp Ciwidey adalah area perkemahan alam di hutan pinus Rancabali yang menyediakan fasilitas camping keluarga, api unggun, serta aneka wahana petualangan alam.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-151': {
            'description': "Ecopark Curug Tilu adalah taman wisata keluarga ramah lingkungan di kebun teh Rancabali yang menampilkan tiga air terjun buatan estetik, Rainbow Slide, playground anak, dan penginapan Rumah Hobbit.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '19:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-152': {
            'description': "Kebun Teh Rancabali merupakan perkebunan teh luas di ketinggian 1.650 mdpl yang menawarkan hamparan hijau fotogenik, wisata edukasi pabrik teh Walini, serta jalur tea walk di udara sejuk pegunungan.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-153': {
            'description': "Perkebunan Teh Malabar di Pangalengan adalah salah satu perkebunan teh tertua di Indonesia seluas 2.022 hektar yang didirikan K.A.R. Bosscha pada 1896 dan menyimpan situs sejarah kolonial.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-154': {
            'description': "Kampung Singkur di Hutan Pinus Rahong, Pangalengan adalah destinasi wisata alam dan petualangan sungai yang menyuguhkan rafting di Sungai Palayangan, offroad, serta area camping hutan pinus.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '19:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '19:00'
        },
        'LOC-155': {
            'description': "Curug Panganten adalah air terjun kembar alami di Pangalengan yang namanya berarti 'pengantin' dalam bahasa Sunda karena dua alirannya yang berdampingan seperti sepasang pengantin.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
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
    print("Batch 7 applied successfully.")

if __name__ == '__main__':
    main()
