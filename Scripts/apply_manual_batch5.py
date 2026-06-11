import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-110': {
            'description': None,  # already has description
            'jam_buka_weekday': '10:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '10:00',
            'jam_tutup_weekend': '20:00'
        },
        'LOC-111': {
            'description': "Venus Cimahi merupakan pusat wisata keluarga bertema Family Quality Time di Cimahi yang memadukan waterpark Rainbow, playground Rumah Pohon, foodcourt, dan pusat kebugaran dalam satu lokasi.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '20:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '20:00'
        },
        'LOC-118': {
            'description': "Forest Walk Babakan Siliwangi adalah hutan kota di Tamansari dengan jalur pejalan kaki dari kayu sepanjang 2 km yang merupakan salah satu forest walk terpanjang di Asia Tenggara.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-121': {
            'description': "NuArt Sculpture Park adalah kompleks seni dan galeri patung kontemporer seluas 3 hektar karya seniman Nyoman Nuarta (pencipta GWK Bali) yang menyajikan taman hijau asri dan studio kreatif.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-123': {
            'description': "Museum Pendidikan Nasional UPI adalah museum lima lantai di kampus UPI Bandung yang melestarikan sejarah pendidikan Indonesia dari masa prasejarah hingga reformasi, serta berfungsi sebagai pusat penelitian.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '15:00',
            'jam_buka_weekend': None,
            'jam_tutup_weekend': None
        },
        'LOC-127': {
            'description': "Sarae Hills di Lembang adalah destinasi wisata bertema keliling dunia yang menampilkan replika bangunan ikonik internasional seperti Menara Eiffel dan Sphinx dengan kafe panorama perbukitan.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-128': {
            'description': "Observatorium Bosscha adalah observatorium astronomi tertua dan terbesar di Indonesia yang dikelola ITB di Lembang, memiliki teleskop Zeiss ikonik dan berstatus cagar budaya nasional sejak 2004.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '14:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '14:00'
        },
        'LOC-129': {
            'description': "Curug Dago adalah air terjun setinggi 12 meter dari aliran Sungai Cikapundung di kawasan Tahura Djuanda yang menyimpan dua prasasti bersejarah peninggalan Raja Thailand abad ke-19.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-130': {
            'description': "Fairy Garden by The Lodge adalah taman bermain bertema negeri dongeng di Lembang yang memadukan wahana edukatif anak, pertunjukan peri, dan spot foto ikonik di tengah hutan pinus.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '20:00'
        },
        'LOC-131': {
            'description': "Cikole Jayagiri Resort adalah resor wisata alam di hutan pinus Lembang yang menawarkan penginapan kabin kayu, area camping, interaksi dengan rusa, serta beragam wahana outbound.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-132': {
            'description': "Bird & Bromelia Pavilion di Pramestha Resort Town Lembang adalah taman burung edukatif yang memelihara sekitar 600 ekor burung dari berbagai spesies serta koleksi tanaman bromelia hias.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-133': {
            'description': "Punclut (Puncak Ciumbuleuit) adalah kawasan wisata kuliner dan panorama di dataran tinggi Bandung yang menyajikan pemandangan city light malam hari dan spot foto instagramable perbukitan.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '00:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '00:00'
        },
        'LOC-134': {
            'description': "Bukit Bintang Bandung di kawasan Cimenyan menawarkan panorama hutan pinus, jalur hiking menuju Patahan Lembang, serta pesona city light gemerlap Kota Bandung dari ketinggian 1.442 mdpl.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            if u['description'] is not None:
                df_db.loc[idx, 'description'] = u['description']
            if u['jam_buka_weekday'] is not None:
                df_db.loc[idx, 'jam_buka_weekday'] = u['jam_buka_weekday']
                df_db.loc[idx, 'jam_tutup_weekday'] = u['jam_tutup_weekday']
            if u['jam_buka_weekend'] is not None:
                df_db.loc[idx, 'jam_buka_weekend'] = u['jam_buka_weekend']
                df_db.loc[idx, 'jam_tutup_weekend'] = u['jam_tutup_weekend']
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 5 applied successfully.")

if __name__ == '__main__':
    main()
