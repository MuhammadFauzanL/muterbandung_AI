import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-028': {
            'description': "Danau alam tersembunyi di kaki Gunung Tampomas Sumedang yang terkenal dengan kejernihan air mata airnya yang berwarna kebiruan bak kristal."
        },
        'LOC-033': {
            'description': "Bangunan bersejarah bergaya art deco di Bandung yang menjadi saksi pelaksanaan Konferensi Asia Afrika (KAA) 1955 dan kini berfungsi sebagai museum KAA."
        },
        'LOC-040': {
            'description': "Bukit hijau setinggi 877 mdpl di Kota Cimahi yang menjadi jalur pendakian rekreasi keluarga yang dilengkapi tangga paving block dan pemandangan perkotaan yang indah."
        },
        'LOC-044': {
            'description': "Taman bunga florawisata terbesar di Sumedang yang mengusung konsep kastil ala negeri dongeng dengan rainbow slide, bianglala, serta pemandangan Gunung Manglayang."
        },
        'LOC-046': {
            'description': "Kampung wisata adat dan konservasi tanaman langka di Cimahi Utara yang menyajikan suasana asri kebudayaan Sunda tradisional, saung bambu, dan edukasi pertanian."
        },
        'LOC-047': {
            'description': "Kampung adat Sunda Wiwitan di Cimahi Selatan yang terkenal karena kemandirian pangan warganya dengan mengonsumsi beras singkong (rasi) serta pelestarian hutan larangan."
        },
        'LOC-057': {
            'description': "Masjid bersejarah yang didirikan tahun 1850 di pusat kota Sumedang dengan arsitektur unik perpaduan gaya tradisional Sunda, ornamen Tionghoa, dan kolonial Belanda."
        },
        'LOC-058': {
            'description': "Masjid unik di Kota Cimahi yang dirancang menyerupai kapal laut lengkap dengan jangkar, cerobong nakhoda, serta interior bernuansa geladak bahtera Nabi Nuh."
        },
        'LOC-059': {
            'description': "Destinasi pemandian alam asri di Sumedang dengan kolam mata air jernih dari Gunung Tampomas yang mengalir di antara hamparan persawahan hijau sejuk."
        },
        'LOC-064': {
            'description': "Kawasan wisata instagramable di Pangalengan dengan jembatan kaca U sepanjang 150 meter di atas kebun teh dan memiliki desain ikonik bertema kubah putih Santorini."
        },
        'LOC-068': {
            'description': "Pasar tradisional rakyat yang dikelola Pemerintah Kota Cimahi sebagai pusat ekonomi dan penyedia kebutuhan pokok harian masyarakat sekitar."
        },
        'LOC-069': {
            'description': "Pemandian air panas belerang alami di kaki Gunung Tampomas Sumedang yang populer untuk terapi kesehatan dan relaksasi keluarga."
        },
        'LOC-071': {
            'description': "Puncak area Gunung Bohong Cimahi yang dihiasi tugu Kujang Kembar dan menyajikan panorama lanskap perkotaan Bandung Raya dari ketinggian."
        },
        'LOC-074': {
            'description': "Restoran kuliner khas Sunda di jalur wisata Ciwidey yang menyajikan nasi liwet lezat di saung-saung asri di atas kolam ikan pedesaan."
        },
        'LOC-076': {
            'description': "Wisata alam tebing karst eksotis di aliran Citarum Purba Cipatat yang menawarkan keindahan tebing bebatuan purba, gua alam, dan aktivitas susur gua."
        },
        'LOC-087': {
            'description': "Taman ekowisata dan edukasi lingkungan di perbukitan Cimahi Utara yang menyediakan area kuliner tradisional Pasar Awi Campernik, camping ground, dan arena panahan."
        },
        'LOC-093': {
            'description': "Taman kota bersejarah peninggalan kolonial Belanda di Cimahi Tengah yang berfungsi sebagai ruang terbuka hijau rindang, ramah anak, dan tempat bersantai warga."
        },
        'LOC-104': {
            'description': "Pusat perbelanjaan legendaris di jantung Kota Bandung yang berdiri sejak 1983 dan kini tampil modern dengan fasilitas berbelanja, bioskop, serta pusat kuliner."
        },
        'LOC-106': {
            'description': "Taman rekreasi keluarga berkonsep edutainment di Cisarua Bandung Barat yang menggabungkan mini zoo interaktif, rainbow slide, playground anak, dan panorama perbukitan."
        },
        'LOC-107': {
            'description': "Destinasi wisata perbukitan di Sumedang Selatan yang populer sebagai salah satu spot olahraga paralayang terbaik dan dilengkapi restoran serta pemandangan kota dari ketinggian."
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
    print("Batch 12 applied successfully.")

if __name__ == '__main__':
    main()
