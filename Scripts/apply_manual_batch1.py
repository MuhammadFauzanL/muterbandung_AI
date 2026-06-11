import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df = pd.read_csv(db_path)
    
    updates = {
        'LOC-002': {
            'description': 'Destinasi eduwisata populer di Kota Cimahi yang memadukan rekreasi keluarga dengan edukasi pertanian, peternakan, kuliner, dan outbound.',
            'jam_buka_weekday': '08:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00', 'jam_tutup_weekend': '21:00'
        },
        'LOC-004': {
            'description': 'Ruang terbuka publik di pusat kota Sumedang dengan Monumen Lingga yang ikonik, ramah anak, dan memiliki taman bermain serta area duduk santai.',
            'jam_buka_weekday': '00:00', 'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00', 'jam_tutup_weekend': '23:59'
        },
        'LOC-006': {
            'description': 'Taman hiburan keluarga yang berlokasi dekat kolam renang Karang Setra Bandung, menawarkan berbagai wahana permainan terusan seperti Cinema 4D, Rumah Hantu, Sepeda Udara, dan Boom Boom Car.',
            'jam_buka_weekday': '11:00', 'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '11:00', 'jam_tutup_weekend': '23:00'
        },
        'LOC-008': {
            'description': 'Pusat edukasi sains interaktif di Sukasari Bandung dengan beragam alat peraga astronomi, robotik, fisika, dan kimia, menempati gedung bersejarah yang pernah dikunjungi Bung Karno.',
            'jam_buka_weekday': '09:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00', 'jam_tutup_weekend': '17:00'
        },
        'LOC-009': {
            'description': 'Bendungan terbesar kedua di Indonesia yang membendung Sungai Cimanuk Sumedang, menawarkan keindahan waduk berlatar perbukitan yang populer untuk memancing, susur air dengan perahu, dan foto rekreasi.',
            'jam_buka_weekday': '08:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00', 'jam_tutup_weekend': '17:00'
        },
        'LOC-010': {
            'description': 'Kawasan mixed-use ikonik di pusat Kota Bandung yang menggabungkan pusat perbelanjaan, apartemen, dan hotel dengan gaya arsitektur Art Deco khas kolonial.',
            'jam_buka_weekday': '10:00', 'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '10:00', 'jam_tutup_weekend': '22:00'
        },
        'LOC-013': {
            'description': 'Wisata alam perbukitan di Cikalong Wetan, Bandung Barat pada ketinggian 1.300 mdpl yang menyajikan panorama kebun teh, pohon pinus, dan area camping 24 jam.',
            'jam_buka_weekday': '08:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00', 'jam_tutup_weekend': '17:00'
        },
        'LOC-014': {
            'description': 'Kawasan wisata alam dan perkemahan di Ciwidey, Kabupaten Bandung (ketinggian 1.700 mdpl) dengan hutan lindung asri, penangkaran rusa interaktif, dan kolam renang air panas alami.',
            'jam_buka_weekday': '00:00', 'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00', 'jam_tutup_weekend': '23:59'
        },
        'LOC-015': {
            'description': 'Kawasan jalan raya nasional legendaris yang menghubungkan Bandung-Sumedang, dibangun pada era Daendels (1809) dengan medan curam yang diapit tebing batu cadas dan memiliki monumen bersejarah Pangeran Kornel.',
            'jam_buka_weekday': '00:00', 'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00', 'jam_tutup_weekend': '23:59'
        },
        'LOC-016': {
            'description': 'Tempat wisata bertema kebudayaan Tionghoa di Kota Bandung yang telah ditutup secara permanen sejak tahun 2020 akibat pandemi COVID-19.',
            'jam_buka_weekday': None, 'jam_tutup_weekday': None,
            'jam_buka_weekend': None, 'jam_tutup_weekend': None
        },
        'LOC-017': {
            'description': 'Pusat perbelanjaan (mall) populer di Jalan Cihampelas Bandung yang berkonsep outdoor asri dipadukan indoor, lengkap dengan aneka gerai mode, kuliner, dan bioskop.',
            'jam_buka_weekday': '10:00', 'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '10:00', 'jam_tutup_weekend': '22:00'
        },
        'LOC-018': {
            'description': 'Salah satu pusat perbelanjaan utama di Kota Cimahi yang menyediakan supermarket, gerai busana, area permainan anak, serta beragam pilihan tempat makan keluarga.',
            'jam_buka_weekday': '10:00', 'jam_tutup_weekday': '21:00',
            'jam_buka_weekend': '10:00', 'jam_tutup_weekend': '21:00'
        },
        'LOC-019': {
            'description': 'Pusat layanan teknologi dan inkubator industri kreatif digital Kota Cimahi yang menyelenggarakan pelatihan bisnis, co-working space, dan studio animasi.',
            'jam_buka_weekday': '08:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': 'Tutup', 'jam_tutup_weekend': 'Tutup'
        },
        'LOC-022': {
            'description': 'Air terjun bertingkat tiga di kawasan Desa Wisata Citengah, Sumedang Selatan, menyajikan keindahan alam di kaki Gunung Goong serta fasilitas outbound dan camping.',
            'jam_buka_weekday': '00:00', 'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00', 'jam_tutup_weekend': '23:59'
        },
        'LOC-025': {
            'description': 'Air terjun setinggi 87 meter di Cisarua, Bandung Barat yang dikelilingi hutan pinus asri, terkenal dengan fenomena pelangi akibat bias cahaya matahari.',
            'jam_buka_weekday': '08:00', 'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00', 'jam_tutup_weekend': '17:00'
        }
    }
    
    for loc_id, val in updates.items():
        idx = df[df['location_id'] == loc_id].index
        if len(idx) > 0:
            i = idx[0]
            df.loc[i, 'description'] = val['description']
            # We only overwrite if it is not none or if the place is closed (LOC-016)
            df.loc[i, 'jam_buka_weekday'] = val['jam_buka_weekday']
            df.loc[i, 'jam_tutup_weekday'] = val['jam_tutup_weekday']
            df.loc[i, 'jam_buka_weekend'] = val['jam_buka_weekend']
            df.loc[i, 'jam_tutup_weekend'] = val['jam_tutup_weekend']
            
    # Progress tracking
    total_rows = len(df)
    desc_filled = df['description'].notna().sum()
    hours_filled = (df['jam_buka_weekday'].notna() & df['jam_buka_weekend'].notna()).sum()
    unresolved = total_rows - hours_filled
    
    print("\n=== PROGRESS REPORT BATCH 1 MANUAL ===")
    print(f"Total Rows: {total_rows}")
    print(f"Descriptions Filled: {desc_filled} ({desc_filled/total_rows*100:.1f}%)")
    print(f"Operating Hours Filled: {hours_filled} ({hours_filled/total_rows*100:.1f}%)")
    print(f"Rows Still Unresolved (Missing Hours): {unresolved}")
    
    df.to_csv(db_path, index=False)
    print(f"Successfully applied batch 1 updates to {db_path}!")

if __name__ == '__main__':
    main()
