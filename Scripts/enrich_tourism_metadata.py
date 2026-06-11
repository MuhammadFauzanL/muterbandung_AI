import pandas as pd
import re
import os

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
    # Find which index (0-6) matches the day_name
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
    excel_path = 'DATABASE_WISATA_VERIFIKASI_INTERNET_BATCH1.xlsx'
    
    df_db = pd.read_csv(db_path)
    df_raw = pd.read_csv(raw_path)
    df_excel = pd.read_excel(excel_path, sheet_name='Wisata_Verifikasi')
    
    # Ensure new columns exist in df_db
    new_cols = ['description', 'jam_buka_weekday', 'jam_tutup_weekday', 'jam_buka_weekend', 'jam_tutup_weekend']
    for col in new_cols:
        if col not in df_db.columns:
            df_db[col] = None
            
    # Create maps from raw scrape
    raw_desc_map = {}
    raw_hours_map = {}
    for idx, row in df_raw.iterrows():
        title = str(row['title']).lower().strip()
        if pd.notna(row['description']):
            raw_desc_map[title] = row['description']
        
        # Collect hours for each day
        day_hours = {}
        for day in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']:
            val = get_day_hours(row, day)
            if val:
                day_hours[day] = val
        if day_hours:
            raw_hours_map[title] = day_hours
            
    # Create maps from Excel verified
    excel_map = {}
    for idx, row in df_excel.iterrows():
        loc_id = row['location_id']
        excel_map[loc_id] = row

    # Enrich df_db
    for idx, row in df_db.iterrows():
        name = str(row['location_name']).lower().strip()
        loc_id = row['location_id']
        
        # 1. Fill Description
        if name in raw_desc_map:
            df_db.loc[idx, 'description'] = raw_desc_map[name]
            
        # 2. Fill Operating Hours
        # If in raw scrape, parse and map
        if name in raw_hours_map:
            hours = raw_hours_map[name]
            # Weekday (using Monday / Senin as representative)
            weekday_val = hours.get('Senin') or hours.get('Selasa') or hours.get('Rabu') or hours.get('Kamis') or hours.get('Jumat')
            # Weekend (using Saturday / Sabtu as representative)
            weekend_val = hours.get('Sabtu') or hours.get('Minggu')
            
            b_wd, t_wd = parse_time_str(weekday_val)
            b_we, t_we = parse_time_str(weekend_val)
            
            # Apply hour rules (if only one pattern is available, mirror them)
            if b_wd and not b_we:
                b_we, t_we = b_wd, t_wd
            elif b_we and not b_wd:
                b_wd, t_wd = b_we, t_we
                
            if b_wd:
                df_db.loc[idx, 'jam_buka_weekday'] = b_wd
                df_db.loc[idx, 'jam_tutup_weekday'] = t_wd
            if b_we:
                df_db.loc[idx, 'jam_buka_weekend'] = b_we
                df_db.loc[idx, 'jam_tutup_weekend'] = t_we
                
        # Override with Excel verified if present and verified
        if loc_id in excel_map:
            exc_row = excel_map[loc_id]
            # Jam Buka/Tutup
            if exc_row.get('status_jam_internet') in ['Terverifikasi', 'Terverifikasi - menggunakan jam weekend', 'Terverifikasi - jam kunjungan wisata']:
                b_val = str(exc_row['jam_buka']).strip()
                t_val = str(exc_row['jam_tutup']).strip()
                
                # Check for format HH:MM
                if ':' in b_val and ':' in t_val:
                    # Excel verifikasi might not distinguish weekday/weekend unless specified.
                    # We will update both weekday and weekend with these verified hours.
                    df_db.loc[idx, 'jam_buka_weekday'] = b_val
                    df_db.loc[idx, 'jam_tutup_weekday'] = t_val
                    df_db.loc[idx, 'jam_buka_weekend'] = b_val
                    df_db.loc[idx, 'jam_tutup_weekend'] = t_val
            # Prices
            if exc_row.get('status_harga_internet') == 'Terverifikasi':
                df_db.loc[idx, 'price_min'] = exc_row['price_min']
                df_db.loc[idx, 'price_max'] = exc_row['price_max']
                df_db.loc[idx, 'price_type'] = exc_row['price_type']

    # Progress tracking
    total_rows = len(df_db)
    desc_filled = df_db['description'].notna().sum()
    hours_filled = (df_db['jam_buka_weekday'].notna() & df_db['jam_buka_weekend'].notna()).sum()
    unresolved = total_rows - hours_filled
    
    print("\n=== ENRICHMENT PROGRESS REPORT ===")
    print(f"Total Rows: {total_rows}")
    print(f"Descriptions Filled: {desc_filled} ({desc_filled/total_rows*100:.1f}%)")
    print(f"Operating Hours Filled: {hours_filled} ({hours_filled/total_rows*100:.1f}%)")
    print(f"Rows Still Unresolved (Missing Hours): {unresolved}")
    
    # Save the enriched dataset
    output_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df_db.to_csv(output_path, index=False)
    print(f"Enriched database saved to {output_path}")

if __name__ == '__main__':
    main()
