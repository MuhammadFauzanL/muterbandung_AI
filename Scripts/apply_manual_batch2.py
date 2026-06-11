import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-016': {
            'description': "Chinatown Bandung merupakan kawasan wisata kuliner dan budaya Tionghoa di Jalan Kelenteng yang telah tutup secara permanen sejak tahun 2020 akibat dampak pandemi COVID-19.",
            'jam_buka_weekday': '',
            'jam_tutup_weekday': '',
            'jam_buka_weekend': '',
            'jam_tutup_weekend': ''
        },
        'LOC-023': {
            'description': "Curug Malela merupakan air terjun setinggi 60 meter di Rongga yang dikenal sebagai 'Niagara Mini' Bandung Barat karena bentuk alirannya yang melebar dan menyajikan pemandangan alam yang megah.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-029': {
            'description': "Dusun Bambu adalah destinasi wisata keluarga berkonsep ramah lingkungan di Cisarua, Bandung Barat yang memadukan keindahan alam kaki Gunung Burangrang dengan wisata edukasi, kuliner, dan penginapan.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '21:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-032': {
            'description': "Gantole dan Paralayang Singajaya merupakan area wisata alam ketinggian di perbukitan Singajaya, Cihampelas yang menjadi lokasi olahraga paralayang dengan panorama Waduk Saguling.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-036': {
            'description': "Glamping Lakeside Rancabali menawarkan pengalaman berkemah mewah di tepi Situ Patenggang, Ciwidey, dikelilingi kebun teh yang indah dan dilengkapi restoran ikonik berbentuk perahu Pinisi.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-037': {
            'description': "Gunung Tampomas merupakan gunung berapi di Sumedang setinggi 1.684 mdpl dengan puncak Sanghiyang Taraje yang populer sebagai area pendakian alam bebas dan situs ziarah sejarah.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-038': {
            'description': "Gunung Tangkuban Parahu merupakan gunung berapi aktif ikonik di utara Bandung yang terkenal dengan kawah gas belerang raksasa seperti Kawah Ratu serta legenda Sangkuriang.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-041': {
            'description': "Gunung Puntang di Cimaung, Bandung Selatan merupakan kawasan wisata alam bersejarah yang menyajikan reruntuhan Stasiun Radio Malabar kolonial Belanda, bumi perkemahan, dan jalur pendakian.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-042': {
            'description': "Gunung Putri Lembang adalah bukit perkemahan setinggi 1.587 mdpl yang menyuguhkan pemandangan matahari terbit, pemandangan lampu kota Bandung, dan jalur pendakian ramah pemula di kelilingi hutan pinus.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-043': {
            'description': "Happy Farm Ciwidey adalah destinasi wisata keluarga bertema peternakan edukatif di Ciwidey, menampilkan kebun binatang mini kelinci dan domba, wahana berkuda, serta Candy House yang ceria.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-048': {
            'description': "Kampung Karuhun Eco Green Park di Citengah, Sumedang memadukan konsep wisata alam pegunungan dengan wahana petualangan luar ruangan seperti river tubing, kolam renang, dan panggung seni budaya.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        }
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            df_db.loc[idx, 'description'] = u['description']
            # Only set hours if not empty strings
            df_db.loc[idx, 'jam_buka_weekday'] = u['jam_buka_weekday'] if u['jam_buka_weekday'] else None
            df_db.loc[idx, 'jam_tutup_weekday'] = u['jam_tutup_weekday'] if u['jam_tutup_weekday'] else None
            df_db.loc[idx, 'jam_buka_weekend'] = u['jam_buka_weekend'] if u['jam_buka_weekend'] else None
            df_db.loc[idx, 'jam_tutup_weekend'] = u['jam_tutup_weekend'] if u['jam_tutup_weekend'] else None
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 2 applied successfully.")

if __name__ == '__main__':
    main()
