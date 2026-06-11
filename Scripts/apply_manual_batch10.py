import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-190': {
            'description': "Curug Anom adalah air terjun setinggi 30 meter di kawasan wisata Natural Hill Lembang yang berciri khas dinding tebing batu cadas vertikal datar berlatar pepohonan asri.",
            'jam_buka_weekday': '06:30',
            'jam_tutup_weekday': '16:30',
            'jam_buka_weekend': '06:30',
            'jam_tutup_weekend': '16:30'
        },
        'LOC-192': {
            'description': "Curug Ngebul Gununghalu adalah air terjun bertingkat yang asri di Sindangjaya Gununghalu yang dinamai karena jatuhan airnya memicu uap air mirip asap (ngebul) di atas kolam alami.",
            'jam_buka_weekday': '06:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '06:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-197': {
            'description': "Curug Nyalangkadar adalah destinasi air terjun tersembunyi yang alami dan asri di kawasan Rajamandala Cipatat dengan aliran air jernih serta jalur trekking yang menantang.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-198': {
            'description': "Tebing Gunung Hawu adalah kawasan karst tebing kapur purba di Padalarang yang populer untuk aktivitas ekstrem panjat tebing, hammocking di ketinggian, serta berburu sunrise.",
            'jam_buka_weekday': '05:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '05:00',
            'jam_tutup_weekend': '18:00'
        },
        'LOC-199': {
            'description': "Taman Buru Gunung Masigit Kareumbi adalah kawasan konservasi hutan seluas 12.420 hektar di perbatasan Bandung-Sumedang yang menawarkan bumi perkemahan, penangkaran rusa, dan jalur jungle trekking.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-201': {
            'description': "Curug Batu Templek adalah air terjun unik setinggi 50 meter di tebing cadas bekas area penambangan batu alam yang berbentuk lempengan batuan tipis yang tersusun rapi.",
            'jam_buka_weekday': '06:00',
            'jam_tutup_weekday': '18:00',
            'jam_buka_weekend': '06:00',
            'jam_tutup_weekend': '21:00'
        },
        'LOC-204': {
            'description': "Teras Sunda Cibiru adalah pusat pelestarian seni budaya Sunda seluas 5.600 meter persegi di Cibiru Bandung yang dilengkapi amphitheater bambu, galeri alat musik, dan ruang kreatif.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '22:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '22:00'
        },
        'LOC-213': {
            'description': "Taman Cibeunying adalah taman kota legendaris peninggalan kolonial Belanda di Bandung Wetan yang menawarkan ruang terbuka hijau asri dengan gazebo untuk berkumpul dan bersantai.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '09:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-215': {
            'description': "Taman Pramuka Bandung adalah taman publik di Cihapit Bandung yang dilengkapi fasilitas skate park modern, area kegiatan kepramukaan, dan pepohonan pelindung yang rindang.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-217': {
            'description': "Karang Setra Waterland adalah waterpark rekreasi keluarga legendaris seluas 6 hektar di Bandung sejak 1958 yang menyediakan kolam olympic, kolam arus, seluncuran air raksasa, dan kolam pantai.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '16:00'
        },
        'LOC-219': {
            'description': "Museum Inggit Garnasih adalah bangunan cagar budaya bersejarah di Kota Bandung yang melestarikan kediaman tokoh pejuang Inggit Garnasih dan merekam jejak perjuangan Bung Karno.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '16:00',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '00:00'
        },
        'LOC-220': {
            'description': "Nimo Jungle Hot Spring adalah kolam pemandian air panas alami estetik pertama di tengah hutan pinus Lebakmuncang Ciwidey yang menyajikan waterfall hangat dan private jacuzzi.",
            'jam_buka_weekday': '09:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '23:00'
        },
        'LOC-221': {
            'description': "Glamping Legok Kondang adalah resort perkemahan mewah di Ciwidey dengan konsep pondokan ala Ubud Bali yang menawarkan kenyamanan hotel berbintang di tengah sejuknya alam pegunungan.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-223': {
            'description': "Kebun Strawberry Emte Highland Resort adalah destinasi agrowisata petik buah strawberry segar secara langsung di kebun pegunungan yang terletak di area wisata alam Emte Highland Resort Ciwidey.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-224': {
            'description': "Sungai Palayangan Rafting adalah wisata petualangan arung jeram sepanjang 4,5-5 km di Sungai Palayangan Pangalengan dengan tingkat kesulitan Grade II-III yang dikelilingi hutan pinus.",
            'jam_buka_weekday': '08:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '08:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-225': {
            'description': "Curug Ceret Pangalengan adalah air terjun alami setinggi 5 meter di tepi jalan pedesaan Pangalengan yang airnya kerap memercik ke jalan dan memunculkan fenomena pelangi kecil.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-226': {
            'description': "Gunung Nini Pangalengan adalah puncak bukit bersejarah di kawasan perkebunan teh Malabar Pangalengan yang dahulunya menjadi tempat favorit K.A.R. Bosscha untuk memantau pemetik teh.",
            'jam_buka_weekday': '07:00',
            'jam_tutup_weekday': '17:00',
            'jam_buka_weekend': '07:00',
            'jam_tutup_weekend': '17:00'
        },
        'LOC-227': {
            'description': "Puncak Mega Gunung Puntang adalah puncak tertinggi berketinggian 2.224 mdpl di barisan Gunung Puntang yang populer untuk pendakian, berburu sunrise, dan berkemah di atas awan.",
            'jam_buka_weekday': '00:00',
            'jam_tutup_weekday': '23:59',
            'jam_buka_weekend': '00:00',
            'jam_tutup_weekend': '23:59'
        },
        'LOC-229': {
            'description': "Puncak Damar Jatigede adalah wana wisata alam di Sumedang yang menawarkan keindahan panorama Waduk Jatigede dari atas bukit pinus dengan dek pandang dan area outbound.",
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
    print("Batch 10 applied successfully.")

if __name__ == '__main__':
    main()
