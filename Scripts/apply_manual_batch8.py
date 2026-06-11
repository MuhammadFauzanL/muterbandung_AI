import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-158': {
            'description': "Situ Ninah (Situ Datar) adalah danau alami eksotis di tengah perkebunan teh Pasir Malang Pangalengan yang dikelilingi hutan pinus rindang dan populer sebagai area berkemah 24 jam.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-159': {
            'description': "Penangkaran Rusa Kertamanah adalah destinasi wisata edukasi keluarga di Margamukti Pangalengan tempat pengunjung dapat memberi makan dan berfoto dengan kawanan rusa jinak di alam terbuka.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-162': {
            'description': "Rumah Putih Cukul (Villa Jerman) adalah bangunan cagar budaya bergaya arsitektur klasik Eropa peninggalan kolonial Belanda yang berdiri megah di tengah hamparan kebun teh Cukul Pangalengan.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-163': {
            'description': "Kampung Adat Cikondang di kaki Gunung Tilu Pangalengan adalah permukiman adat Sunda kuno yang melestarikan rumah kayu tradisional Bumi Adat dan kawasan Hutan Larangan yang sakral.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-164': {
            'description': "Java Preanger Gunung Tilu merupakan sentra edukasi perkebunan dan pengolahan kopi Arabika legendaris Priangan di Margamulya Pangalengan yang menawarkan cita rasa aroma rempah dan jeruk.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-165': {
            'description': "Malabar Mountain Coffee Shop & Eatery adalah kedai kopi specialty di kaki Gunung Malabar Pangalengan yang menawarkan seduhan kopi Arabika lokal hasil kebun sendiri berlatar panorama alam pegunungan.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-166': {
            'description': "Muara Rahong Hills adalah kawasan glamping tepi sungai di tengah hutan pinus Rahong Pangalengan yang dilengkapi dengan area petualangan outbound seperti rafting dan off-road.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-170': {
            'description': "Tafso Barn adalah restoran tematik bernuansa taman lereng bukit di kawasan Punclut yang menawarkan tempat duduk unik mirip sangkar burung, spot foto estetik, dan panorama alam sejuk.",
            'jam_buka_weekday': '12:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '20:30'
        },
        'LOC-171': {
            'description': "D'Dieuland adalah destinasi wisata terpadu di lereng Punclut Bandung yang menyajikan sky walk setinggi 10 meter, wahana playground anak, giant swing, serta restoran berpemandangan indah.",
            'jam_buka_weekday': '11:00',
            'jam_tutup_weekday': '19:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-178': {
            'description': "De'Ranch Lembang merupakan tempat rekreasi keluarga bertema peternakan ala koboi Amerika Barat yang menawarkan aktivitas naik kuda berhias kostum koboi dan aneka wahana luar ruangan.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '18:00'
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
    print("Batch 8 applied successfully.")

if __name__ == '__main__':
    main()
