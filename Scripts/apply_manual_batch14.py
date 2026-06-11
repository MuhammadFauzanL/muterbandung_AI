import pandas as pd

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db = pd.read_csv(db_path)
    
    updates = {
        'LOC-193': {
            'description': "Gua purba eksotis di kawasan karst PLTA Saguling Cipatat dengan stalaktit dan stalakmit indah di pinggir aliran Sungai Citarum Purba."
        },
        'LOC-194': {
            'description': "Gua dan sungai bawah tanah misterius di Cipatat tempat 'ditelannya' aliran Sungai Citarum yang dipercaya sebagai titik bobolnya Danau Bandung Purba."
        },
        'LOC-195': {
            'description': "Destinasi ngarai eksotis dengan aliran sungai kehijauan jernih diapit tebing batu menjulang tinggi mirip Green Canyon."
        },
        'LOC-196': {
            'description': "Air terjun unik berketinggian 20 meter di Citatah Cipatat yang aliran airnya keluar dari mulut terowongan air tua peninggalan kolonial Belanda."
        },
        'LOC-203': {
            'description': "Masjid terapung megah di Gedebage Bandung yang didesain modern-futuristik tanpa kubah konvensional serta dikelilingi danau retensi luas."
        },
        'LOC-205': {
            'description': "Ruang publik ikonik di pusat Kota Bandung seberang Gedung Sate yang dilengkapi fasilitas jogging track modern, taman asri, dan perpustakaan umum."
        },
        'LOC-207': {
            'description': "Monumen bersejarah setinggi 45 meter di Lapangan Tegallega yang memiliki puncak menyerupai kobaran api emas untuk mengenang peristiwa Bandung Lautan Api 1946."
        },
        'LOC-208': {
            'description': "Museum edukatif di Jalan Aceh yang menempati bangunan kolonial klasik tahun 1920 dan menyajikan sejarah serta perkembangan Kota Bandung secara visual menarik."
        },
        'LOC-210': {
            'description': "Taman kota bertema edukasi sejarah di Balai Kota Bandung yang menampilkan informasi para pemimpin Bandung dari masa ke masa dan kolam air anak."
        },
        'LOC-211': {
            'description': "Taman kota berbentuk segitiga estetik di Jalan Merdeka Bandung yang memiliki atraksi air mancur menyala warna-warni yang indah di malam hari."
        },
        'LOC-214': {
            'description': "Ruang terbuka hijau rindang asri di Kota Bandung yang dilengkapi area bermain anak, jogging track, gazebo, dan perpustakaan mini."
        },
        'LOC-222': {
            'description': "Wisata perkebunan teh yang sejuk di Pangalengan dengan jembatan kayu sky walk sepanjang 400 meter membelah kebun teh yang indah."
        },
        'LOC-231': {
            'description': "Titik pandang perbukitan terbaik di pesisir Waduk Jatigede Sumedang yang menawarkan panorama bendungan indah dengan pulau-pulau kecil eksotis."
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
    print("Batch 14 applied successfully.")

if __name__ == '__main__':
    main()
