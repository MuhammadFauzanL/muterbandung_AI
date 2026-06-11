import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-049': {
            'description': "Kampung Toga Villa & Resto di Sukajaya, Sumedang Selatan, adalah kawasan agrowisata keluarga yang menyuguhkan pemandangan perbukitan asri, villa penginapan, kolam renang, serta arena olahraga paralayang.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '21:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-050': {
            'description': "Kawah Putih adalah danau kawah vulkanik eksotis yang terbentuk dari letusan Gunung Patuha di Ciwidey, terletak pada ketinggian 2.430 mdpl dengan air putih kehijauan yang menawan dan udara sejuk.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-052': {
            'description': "Kebun Binatang Bandung merupakan taman margasatwa seluas 14 hektar di Tamansari yang mengoleksi lebih dari 800 satwa dan berfungsi sebagai kawasan konservasi edukatif di tengah Kota Bandung.",
            'jam_buka_weekday': '10:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '10:00',
            'jam_tutup_weekend': '16:00'
        },
        'LOC-055': {
            'description': "Maribaya Natural Hotspring Resort di Lembang menyajikan pemandian air panas alami berkhasiat kesehatan yang dikelilingi hutan pinus rindang, air terjun Cigulung, serta area bermain keluarga.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-072': {
            'description': "Puncak Eurad adalah objek wisata perbukitan sejuk di perbatasan Lembang dan Subang, menawarkan panorama hutan pinus, hamparan kebun teh, gardu pandang foto ikonik, serta bumi perkemahan.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-073': {
            'description': "Ranca Upas adalah kawasan bumi perkemahan terpopuler di Rancabali, Ciwidey, yang terkenal dengan penangkaran rusa ramah interaksi, kolam pemandian air panas, serta panorama hutan pegunungan sejuk.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-080': {
            'description': "Situ Cisanti merupakan danau asri di kaki Gunung Wayang, Kertasari, yang terkenal sebagai titik nol kilometer hulu Sungai Citarum serta dikelilingi pemandangan hutan eucalyptus yang menenangkan.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-081': {
            'description': "Situ Ciseupan Cibeber di Cimahi Selatan menawarkan panorama danau tenang berlatar perbukitan hijau, dilengkapi restoran saung makan terapung, kolam pemancingan, serta fasilitas glamping.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '20:00'
        },
        'LOC-082': {
            'description': "Situ Patenggang adalah danau eksotis seluas 45.000 hektar di Rancabali, Ciwidey yang dikelilingi kebun teh asri dan memiliki legenda cinta legendaris di Pulau Asmara serta Batu Cinta.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-102': {
            'description': "Terminal Wisata Grafika Cikole adalah resor rekreasi bernuansa hutan pinus Lembang yang menawarkan berbagai wahana outbound menantang, penginapan kabin kayu, restoran Sunda, dan wahana Hutan Mycelia.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '22:00'
        }
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            df_db.loc[idx, 'description'] = u['description']
            df_db.loc[idx, 'jam_buka_weekday'] = u['jam_buka_weekday']
            df_db.loc[idx, 'jam_tutup_weekday'] = u['jam_tutup_weekday']
            df_db.loc[idx, 'jam_buka_weekend'] = u['jam_buka_weekend']
            df_db.loc[idx, 'jam_tutup_weekend'] = u['jam_tutup_weekend']
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 3 applied successfully.")

if __name__ == '__main__':
    main()
