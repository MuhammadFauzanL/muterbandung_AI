import pandas as pd

def main():
    df_db = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    df_raw = pd.read_csv('Dataset/apify_jam_buka_semua_lokasi_raw.csv')
    
    missing_desc = df_db[df_db['description'].isna()]
    missing_hours = df_db[df_db['jam_buka_weekday'].isna()]
    
    raw_titles = df_raw['title'].dropna().unique()
    
    print("--- SEARCHING UNMATCHED IN RAW ---")
    matched_count = 0
    matches = {}
    for idx, row in missing_hours.iterrows():
        name = str(row['location_name']).lower().strip()
        # Find raw title that contains the name or vice versa
        found = []
        for rt in raw_titles:
            rt_lower = str(rt).lower().strip()
            if name in rt_lower or rt_lower in name:
                found.append(rt)
        if found:
            matched_count += 1
            matches[row['location_name']] = found
            print(f"  {row['location_id']}: '{row['location_name']}' -> Possible raw titles: {found}")
            
    print(f"Total missing hours: {len(missing_hours)}")
    print(f"Found partial matches for: {matched_count} locations")

if __name__ == '__main__':
    main()
