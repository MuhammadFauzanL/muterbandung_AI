import pandas as pd

def main():
    df_raw = pd.read_csv('Dataset/apify_jam_buka_semua_lokasi_raw.csv')
    df_db = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    
    names_to_check = ['Dusun Bambu Lembang', 'Glamping Lakeside Rancabali', 'Kawah Putih', 'Ranca Upas Ciwidey']
    for n in names_to_check:
        print(f"\nChecking raw data for: '{n}'")
        subset = df_raw[df_raw['title'].str.lower().str.strip() == n.lower().strip()]
        if len(subset) == 0:
            print("  Not found in raw!")
            # Try partial
            subset = df_raw[df_raw['title'].str.contains(n, case=False, na=False)]
            print(f"  Found {len(subset)} partial matches:")
            for idx, r in subset.iterrows():
                print(f"    Title: {r['title']}")
                print(f"    Description: {r.get('description')}")
                # Print opening hours columns if present and not null
                hours_cols = [c for c in df_raw.columns if 'hours' in c and pd.notna(r[c])]
                print(f"    Hours columns: {[(c, r[c]) for c in hours_cols]}")
        else:
            for idx, r in subset.iterrows():
                print(f"    Description: {r.get('description')}")
                hours_cols = [c for c in df_raw.columns if 'hours' in c and pd.notna(r[c])]
                print(f"    Hours columns: {[(c, r[c]) for c in hours_cols]}")
                
if __name__ == '__main__':
    main()
