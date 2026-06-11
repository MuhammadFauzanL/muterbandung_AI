import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-109': {
            'description': "Salah satu pusat perbelanjaan terbesar dan paling ikonik di Kota Bandung yang terintegrasi dengan taman bermain dalam ruangan Trans Studio Bandung."
        },
        'LOC-112': {
            'description': "Vihara tertua bersejarah di Kota Bandung yang didirikan tahun 1855, memiliki ornamen khas Tionghoa yang indah, dan berstatus cagar budaya."
        },
        'LOC-114': {
            'description': "Destinasi waterpark populer keluarga di Sumedang yang menawarkan kolam renang anak-anak, ember tumpah, dan seluncuran air lebar."
        },
        'LOC-116': {
            'description': "Destinasi wisata luar ruangan asri di Tanjungsari Sumedang dengan suasana hutan pinus sejuk, kolam renang alami berundak, dan camping ground."
        },
        'LOC-119': {
            'description': "Ruang terbuka hijau rindang bersejarah di kompleks Balai Kota Bandung yang dinamai dari pahlawan nasional perintis pendidikan perempuan."
        },
        'LOC-120': {
            'description': "Destinasi rekreasi unik dan ramah anak di Bandung yang menjadi surga para pencinta anjing untuk berinteraksi dengan puluhan ras anjing lucu."
        },
        'LOC-136': {
            'description': "Danau buatan estetik bekas galian pasir di Kota Baru Parahyangan Padalarang yang menawarkan rekreasi perahu air, mini zoo, dan bersantai kuliner."
        },
        'LOC-138': {
            'description': "Perkebunan teh peninggalan kolonial di Parongpong Bandung Barat yang menawarkan panorama asri Gunung Burangrang dan sensasi tea walk menyegarkan."
        },
        'LOC-140': {
            'description': "Jembatan gantung spektakuler sepanjang 370 meter di Ciwidey yang menghubungkan area parkir ke destinasi pemandian air panas alami Kawah Rengganis."
        },
        'LOC-147': {
            'description': "Taman bermain air keluarga di Soreang yang memiliki fasilitas kolam renang luas, kolam ombak, mandi busa, dan berbagai seluncuran seru."
        },
        'LOC-156': {
            'description': "Gunung tidak aktif setinggi 2.194 mdpl di Kertasari Kabupaten Bandung yang memiliki area puncak Sulibra yang luas dan dikenal ramah pendaki pemula."
        },
        'LOC-160': {
            'description': "Destinasi geowisata di lereng Gunung Wayang Pangalengan yang menyajikan keindahan kepulan asap belerang putih di antara bebatuan dan pemandian air panas alami."
        },
        'LOC-169': {
            'description': "Restoran kuliner bergaya kastil Eropa klasik di Lembang yang menyajikan aneka roti dan hidangan lezat dengan panorama perbukitan yang menawan."
        },
        'LOC-177': {
            'description': "Waterpark megah seluas 10 hektar di Kota Baru Parahyangan Padalarang yang memiliki wahana air seluncuran ekstrem RocketBLAST tercepat di Asia Tenggara."
        },
        'LOC-184': {
            'description': "Bukit batu andesit bagian dari sesar aktif patahan Lembang yang terbentuk dari lava Gunung Sunda purba dan menyajikan pemandangan alam 360 derajat."
        },
        'LOC-186': {
            'description': "Area berkemah unik di kawasan tebing kapur Gunung Masigit Cipatat yang mengusung tema suku Indian dengan wahana ekstrim hammocking di ketinggian."
        },
        'LOC-187': {
            'description': "Air terjun berundak alami di kaki Gunung Tangkuban Perahu Cisarua yang dikelilingi hutan pinus rindang dan memiliki camping ground luas."
        },
        'LOC-188': {
            'description': "Air terjun eksotis berketinggian 50 meter yang tersembunyi di dalam lembah asri Cisarua Bandung Barat dengan kolam air alami yang segar."
        },
        'LOC-189': {
            'description': "Air terjun indah berketinggian 20 meter di kawasan Curug Tilu Leuwi Opat Parongpong yang memiliki tebing batu berlumut eksotis menyerupai kerucut pengukus nasi."
        },
        'LOC-191': {
            'description': "Air terjun berketinggian 10 meter yang asri di Sindangkerta Bandung Barat, dikenal pula sebagai Curug Orok karena cerita sejarah penemuan bayi setempat."
        },
    }
    
    for loc_id, u in updates.items():
        idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(idx_list) > 0:
            idx = idx_list[0]
            if u.get('description') is not None:
                df_db.loc[idx, 'description'] = u['description']
            print(f"Updated {loc_id}: {df_db.loc[idx, 'location_name']}")
            
    df_db.to_csv(db_path, index=False)
    print("Batch 13 applied successfully.")

if __name__ == '__main__':
    main()
