import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-173': {
            'description': "Cakrawala Sparkling Nature Restaurant adalah restoran tematik instagramable di Punclut dengan beberapa area konsep unik (seperti Galaxy dan Pelangi) serta jembatan kaca Skywalk setinggi 20 meter.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '21:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '22:00'
        },
        'LOC-174': {
            'description': "Lereng Anteng Panoramic Coffee adalah kafe santai populer di lereng bukit Punclut dengan tempat duduk saung tenda transparan estetik yang menyajikan pemandangan alam pegunungan Lembang.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '23:00'
        },
        'LOC-175': {
            'description': "Taman Kupu-Kupu Cihanjuang adalah taman edukasi keluarga seluas 1,8 hektar di Parongpong habitat bagi puluhan spesies kupu-kupu yang menyuguhkan rumah kepompong dan insectarium.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-176': {
            'description': "Padepokan Dayang Sumbi adalah destinasi edukasi serikultur (budidaya ulat sutra) di Cimenyan yang memperagakan seluruh siklus hidup ulat sutra serta proses pemintalan dan penenunan kain sutra.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-179': {
            'description': "Mini Mania Lembang adalah taman rekreasi keluarga di Lembang yang menampilkan puluhan miniatur bangunan ikonik dunia, taman sakura, dan beragam wahana permainan anak.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-180': {
            'description': "Cimory Dairyland Lembang adalah kompleks rekreasi keluarga dan pusat belanja produk olahan susu khas Cimory di Lembang yang terintegrasi dengan area rekreasi Mini Mania.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-181': {
            'description': "Noah's Park Lembang adalah taman petualangan luar ruangan dan outbound di Pagerwangi Lembang yang menawarkan berbagai wahana olahraga berbasis gravitasi seperti Luge Kart.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-182': {
            'description': "Pine Forest Camp Lembang adalah area perkemahan eksklusif di Lembang di ketinggian 1.200 mdpl yang dikelilingi hutan pinus rimbun dan difavoritkan untuk camping, outbound, serta gathering.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-183': {
            'description': "Imah Seniman Lembang adalah resor dan destinasi wisata alam berkonsep tradisional di Lembang yang menawarkan pengalaman menginap di kabin jerami tepi danau serta restoran khas Sunda.",
            'jam_buka_weekday': '10:00',
            'jam_tutup_weekday': '21:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-185': {
            'description': "Ciwangun Indah Camp adalah pelopor area outbound di Parongpong di ketinggian 1.100 mdpl yang menyuguhkan hutan pinus, air terjun Curug Tilu, flying fox, serta bumi perkemahan luas.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '07:00',
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
    print("Batch 9 applied successfully.")

if __name__ == '__main__':
    main()
