import pandas as pd
import re

def parse_time_str(time_str):
    if not isinstance(time_str, str):
        return None, None
    time_str = time_str.strip().lower()
    if '24 jam' in time_str or '24 hours' in time_str or 'open 24' in time_str:
        return '00:00', '23:59'
    if 'tutup' in time_str or 'closed' in time_str:
        return 'Tutup', 'Tutup'
    
    m = re.findall(r'(\d{2})[.:](\d{2})', time_str)
    if len(m) == 2:
        return f'{m[0][0]}:{m[0][1]}', f'{m[1][0]}:{m[1][1]}'
    return None, None

def get_day_hours(row, day_name):
    for i in range(7):
        day_col = f'openingHours/{i}/day'
        hours_col = f'openingHours/{i}/hours'
        if day_col in row and hours_col in row and pd.notna(row[day_col]) and pd.notna(row[hours_col]):
            if str(row[day_col]).strip().lower() == day_name.lower():
                return row[hours_col]
    return None

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    raw_path = 'Dataset/apify_jam_buka_semua_lokasi_raw.csv'
    
    df_db = pd.read_csv(db_path)
    df_raw = pd.read_csv(raw_path)
    
    # Mapping dict from location_id to the exact title in the raw scrape file
    raw_mappings = {
        'LOC-023': 'Curug Malela',
        'LOC-029': 'Dusun Bambu Lembang',
        'LOC-032': 'Gantolle Paralayang Singajaya Cihampelas',
        'LOC-036': 'Glamping Lakeside Rancabali',
        'LOC-037': 'Jl. Gn. Tampomas',
        'LOC-038': 'Gn. Tangkuban Parahu',
        'LOC-040': 'Puncak Bukit Kujang Gunung Bohong',
        'LOC-041': 'Gunung Puntang',
        'LOC-042': 'Gunung Putri Lembang',
        'LOC-048': 'Kampung Karuhun ECO Green Park Sumedang',
        'LOC-050': 'Kawah Putih',
        'LOC-052': 'Kebun Binatang Bandung',
        'LOC-055': 'MARIBAYA Natural Hotspring Resort',
        'LOC-072': 'Puncak Eurad',
        'LOC-073': 'Ranca Upas Ciwidey',
        'LOC-080': 'Situ Cisanti',
        'LOC-081': 'Situ Ciseupan Cibeber',
        'LOC-082': 'Situ Patenggang Ciwidey Bandung',
        'LOC-083': 'Stone Garden Citatah',
        'LOC-086': 'Taman Alun-Alun Kota Cimahi',
        'LOC-095': 'Taman Langit Pangalengan (Sunrise Point & Camping Ground)',
        'LOC-096': 'Taman Lansia',
        'LOC-098': 'Taman musik',
        'LOC-102': 'Terminal Wisata Grafika Cikole',
        'LOC-105': 'The Lodge Maribaya',
        'LOC-110': 'Upside Down World Bandung',
        'LOC-111': 'Venus Cimahi',
        'LOC-120': 'Rumah Guguk Petshop',
        'LOC-127': 'Sarae Hills',
        'LOC-128': 'Bosscha',
        'LOC-129': 'Curug Dago',
        'LOC-131': 'Cikole Jayagiri Resort',
        'LOC-137': 'Rumah Belanda',
        'LOC-141': 'Taman Wisata Bougenville',
        'LOC-142': 'Hejo Forest',
        'LOC-144': 'Barusen Hills',
        'LOC-146': 'Taman Love Soreang',
        'LOC-147': 'Victory Waterpark',
        'LOC-148': 'Pesona Nirwana Waterpark & Cottages / Resort',
        'LOC-150': 'Southland Camp',
        'LOC-154': 'Kampung Singkur',
        'LOC-155': 'Jl. Curug Panganten',
        'LOC-170': 'Tafso Barn',
        'LOC-175': 'Taman Kupu-Kupu Cihanjuang',
        'LOC-177': 'Wahoo Waterworld Bandung',
        'LOC-182': 'Pine Forest Camp',
        'LOC-183': 'Imah Seniman',
        'LOC-185': 'Ciwangun Indah Camp',
        'LOC-186': 'Indiana Camp',
        'LOC-187': 'Curug Layung & Camping Ground',
        'LOC-193': 'Sanghyang Poek Bandung purba',
        'LOC-195': 'Cikahuripan',
        'LOC-196': 'Curug Walanda',
        'LOC-197': 'curug nyalangkadar',
        'LOC-201': 'CURUG BATU TEMPLEK CISANGGARUNG',
        'LOC-204': 'Teras Sunda Cibiru',
        'LOC-215': 'Taman Pramuka',
        'LOC-221': 'Glamping Legok Kondang Lodge',
        'LOC-222': 'Nuansa Riung gunung Pangalengan',
        'LOC-223': 'Kebun Strawberry Emte Highland Resort',
        'LOC-226': 'Gunung Nini',
        'LOC-227': 'Gunung Puntang',
        'LOC-228': 'Wisata Tanjung Duriat'
    }
    
    # Put df_raw into a dictionary by title
    raw_dict = {}
    for idx, r in df_raw.iterrows():
        title = str(r['title']).strip()
        raw_dict[title] = r
        
    updated_desc = 0
    updated_hours = 0
    
    for loc_id, raw_title in raw_mappings.items():
        if raw_title not in raw_dict:
            continue
            
        r_raw = raw_dict[raw_title]
        db_idx_list = df_db[df_db['location_id'] == loc_id].index
        if len(db_idx_list) == 0:
            continue
        db_idx = db_idx_list[0]
        
        # 1. Update description if empty
        if pd.isna(df_db.loc[db_idx, 'description']) or str(df_db.loc[db_idx, 'description']).strip() == '':
            desc = r_raw.get('description')
            if pd.notna(desc) and str(desc).strip():
                df_db.loc[db_idx, 'description'] = str(desc).strip()
                updated_desc += 1
                
        # 2. Update hours if empty
        if pd.isna(df_db.loc[db_idx, 'jam_buka_weekday']) or str(df_db.loc[db_idx, 'jam_buka_weekday']).strip() == '':
            # Parse hours from raw
            day_hours = {}
            for day in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']:
                val = get_day_hours(r_raw, day)
                if val:
                    day_hours[day] = val
                    
            if day_hours:
                # weekday
                wd_val = day_hours.get('Senin') or day_hours.get('Selasa') or day_hours.get('Rabu') or day_hours.get('Kamis') or day_hours.get('Jumat')
                # weekend
                we_val = day_hours.get('Sabtu') or day_hours.get('Minggu')
                
                b_wd, t_wd = parse_time_str(wd_val)
                b_we, t_we = parse_time_str(we_val)
                
                if b_wd and not b_we:
                    b_we, t_we = b_wd, t_wd
                elif b_we and not b_wd:
                    b_wd, t_wd = b_we, t_we
                    
                if b_wd:
                    df_db.loc[db_idx, 'jam_buka_weekday'] = b_wd
                    df_db.loc[db_idx, 'jam_tutup_weekday'] = t_wd
                if b_we:
                    df_db.loc[db_idx, 'jam_buka_weekend'] = b_we
                    df_db.loc[db_idx, 'jam_tutup_weekend'] = t_we
                updated_hours += 1
                
    print("\n=== RAW RECOVERY RESULTS ===")
    print(f"Newly filled descriptions: {updated_desc}")
    print(f"Newly filled operating hours: {updated_hours}")
    
    # Progress check
    total_rows = len(df_db)
    desc_filled = df_db['description'].notna().sum()
    hours_filled = (df_db['jam_buka_weekday'].notna() & df_db['jam_buka_weekend'].notna()).sum()
    unresolved = total_rows - hours_filled
    
    print(f"\nOverall Progress:")
    print(f"Total Rows: {total_rows}")
    print(f"Descriptions Filled: {desc_filled} ({desc_filled/total_rows*100:.1f}%)")
    print(f"Operating Hours Filled: {hours_filled} ({hours_filled/total_rows*100:.1f}%)")
    print(f"Rows Still Unresolved (Missing Hours): {unresolved}")
    
    df_db.to_csv(db_path, index=False)
    print("Enriched database updated and saved.")

if __name__ == '__main__':
    main()
