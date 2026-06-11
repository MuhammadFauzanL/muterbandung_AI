import pandas as pd

def main():
    df_db = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    df_raw = pd.read_csv('Dataset/apify_jam_buka_semua_lokasi_raw.csv')
    
    missing_desc = df_db[df_db['description'].isna()]
    
    # Pre-parse raw descriptions
    raw_desc_data = {}
    for idx, row in df_raw.iterrows():
        title = str(row['title']).lower().strip()
        desc = row.get('description')
        if pd.notna(desc) and str(desc).strip():
            raw_desc_data[title] = (row['title'], str(desc).strip())
            
    print(f"Total raw listings with descriptions: {len(raw_desc_data)}")
    
    found_count = 0
    for idx, r in missing_desc.iterrows():
        name = str(r['location_name']).lower().strip()
        
        # Check direct or partial match
        matched_title = None
        matched_desc = None
        
        if name in raw_desc_data:
            matched_title, matched_desc = raw_desc_data[name]
        else:
            # check partial
            for rt_lower, (rt_orig, d) in raw_desc_data.items():
                if name in rt_lower or rt_lower in name:
                    matched_title = rt_orig
                    matched_desc = d
                    break
        
        if matched_desc:
            found_count += 1
            print(f"Match: '{r['location_name']}' -> '{matched_title}'")
            print(f"  Desc: {matched_desc[:80]}...")
            
    print(f"\nCan recover descriptions for {found_count} out of {len(missing_desc)} missing locations.")

if __name__ == '__main__':
    main()
