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
    df_db = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    df_raw = pd.read_csv('Dataset/apify_jam_buka_semua_lokasi_raw.csv')
    
    missing_hours = df_db[df_db['jam_buka_weekday'].isna()]
    
    # Pre-parse raw hours
    raw_hours_data = {}
    for idx, row in df_raw.iterrows():
        title = str(row['title']).lower().strip()
        day_hours = {}
        for day in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']:
            val = get_day_hours(row, day)
            if val:
                day_hours[day] = val
        if day_hours:
            raw_hours_data[title] = (row['title'], day_hours)
            
    print(f"Total raw listings with hours: {len(raw_hours_data)}")
    
    found_count = 0
    for idx, r in missing_hours.iterrows():
        name = str(r['location_name']).lower().strip()
        
        # Check direct or partial match
        matched_title = None
        matched_hours = None
        
        if name in raw_hours_data:
            matched_title, matched_hours = raw_hours_data[name]
        else:
            # check partial
            for rt_lower, (rt_orig, h) in raw_hours_data.items():
                if name in rt_lower or rt_lower in name:
                    matched_title = rt_orig
                    matched_hours = h
                    break
        
        if matched_hours:
            found_count += 1
            print(f"Match: '{r['location_name']}' -> '{matched_title}'")
            print(f"  Hours: {matched_hours}")
            
    print(f"\nCan recover hours for {found_count} out of {len(missing_hours)} missing locations.")

if __name__ == '__main__':
    main()
