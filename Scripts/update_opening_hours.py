import pandas as pd
import re
import os

def parse_hours(row):
    # Check each day of the week (0 to 6)
    for i in range(7):
        val = row.get(f'openingHours/{i}/hours')
        if pd.isna(val):
            continue
        val_str = str(val).strip()
        if val_str.lower() in ['tutup', 'closed']:
            continue
        if '24' in val_str.lower():
            return '00:00', '23:59'
        
        # Find all time matches in HH.MM format
        times = re.findall(r'\d{2}\.\d{2}', val_str)
        if len(times) >= 2:
            jam_buka = times[0].replace('.', ':')
            jam_tutup = times[-1].replace('.', ':')
            return jam_buka, jam_tutup
            
    return None

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    scraped_path = 'dataset_crawler-google-places_2026-05-20_10-44-12-536 (1).csv'
    
    if not os.path.exists(db_path):
        print(f"Error: {db_path} tidak ditemukan!")
        return
        
    if not os.path.exists(scraped_path):
        print(f"Error: {scraped_path} tidak ditemukan!")
        return
        
    print(f"Membaca database: {db_path}...")
    df_db = pd.read_csv(db_path)
    
    print(f"Membaca data scraped: {scraped_path}...")
    df_scraped = pd.read_csv(scraped_path)
    
    # Sort database names by length in descending order to match longer strings first
    db_names = sorted(df_db['location_name'].tolist(), key=len, reverse=True)
    
    # Map scraped rows to database location names
    matches = []
    for idx, row in df_scraped.iterrows():
        search_str = row.get('searchString')
        matched_name = None
        if isinstance(search_str, str):
            for name in db_names:
                if name.lower() in search_str.lower():
                    matched_name = name
                    break
        matches.append(matched_name)
        
    df_scraped['db_match'] = matches
    
    # Filter out scraped rows that didn't match any database name
    df_matched = df_scraped[df_scraped['db_match'].notna()].copy()
    
    # Track statistics
    total_matched = len(df_matched)
    updated_count = 0
    skipped_tutup_or_nan = 0
    
    # Update jam_buka and jam_tutup in database
    for idx, row in df_matched.iterrows():
        db_name = row['db_match']
        parsed = parse_hours(row)
        
        if parsed:
            jam_buka, jam_tutup = parsed
            # Update df_db where location_name matches db_name
            df_db.loc[df_db['location_name'] == db_name, 'jam_buka'] = jam_buka
            df_db.loc[df_db['location_name'] == db_name, 'jam_tutup'] = jam_tutup
            updated_count += 1
        else:
            skipped_tutup_or_nan += 1
            
    # Save the updated database
    df_db.to_csv(db_path, index=False)
    
    print("\n=== Ringkasan Pembaruan Jam Buka ===")
    print(f"Total baris scraped: {len(df_scraped)}")
    print(f"Berhasil dicocokkan ke database: {total_matched} lokasi")
    print(f"Pembaruan jam buka/tutup berhasil diterapkan: {updated_count} lokasi")
    print(f"Dilewati (karena tutup terus atau data kosong): {skipped_tutup_or_nan} lokasi")
    
    # Find missing locations
    missing_in_scraped = set(df_db['location_name']) - set(df_scraped['db_match'].dropna())
    print(f"Lokasi database yang tidak ditemukan di hasil scraping ({len(missing_in_scraped)}):")
    for name in missing_in_scraped:
        print(f"  - {name}")

if __name__ == '__main__':
    main()
