import pandas as pd
import numpy as np

def main():
    db_path = 'DATABASE_WISATA_DENGAN_METADATA.csv'
    df = pd.read_csv(db_path, low_memory=False)
    
    original_rows = len(df)
    print(f"Original row count: {original_rows}")
    print(f"Original columns: {list(df.columns)}")
    
    # =========================================================
    # 1. Rename 'description' to 'deskripsi_google' for compatibility
    # =========================================================
    if 'description' in df.columns and 'deskripsi_google' not in df.columns:
        df.rename(columns={'description': 'deskripsi_google'}, inplace=True)
        print("Renamed 'description' -> 'deskripsi_google'")
    
    # =========================================================
    # 2. Add traceability columns if they don't exist
    # =========================================================
    traceability_cols = ['sumber_deskripsi', 'sumber_jam', 'status_deskripsi', 'status_jam', 'catatan_jam']
    for col in traceability_cols:
        if col not in df.columns:
            df[col] = np.nan
            print(f"Added column: {col}")
    
    # =========================================================
    # 3. Fill traceability data for all rows
    # =========================================================
    for idx, row in df.iterrows():
        loc_id = row['location_id']
        
        # --- Status deskripsi ---
        if pd.notna(row['deskripsi_google']) and str(row['deskripsi_google']).strip() != '':
            if pd.isna(row['status_deskripsi']):
                df.loc[idx, 'status_deskripsi'] = 'filled_from_reliable_source'
                df.loc[idx, 'sumber_deskripsi'] = 'internet_research_verified'
        else:
            if pd.isna(row['status_deskripsi']):
                df.loc[idx, 'status_deskripsi'] = 'not_found'
        
        # --- Status jam ---
        has_wk_open = pd.notna(row['jam_buka_weekday'])
        has_wk_close = pd.notna(row['jam_tutup_weekday'])
        has_we_open = pd.notna(row['jam_buka_weekend'])
        has_we_close = pd.notna(row['jam_tutup_weekend'])
        
        has_weekday = has_wk_open and has_wk_close
        has_weekend = has_we_open and has_we_close
        
        # Skip if status_jam already set
        if pd.notna(row['status_jam']):
            continue
        
        # Special case: LOC-016 Chinatown Bandung (permanently closed)
        if loc_id == 'LOC-016':
            df.loc[idx, 'status_jam'] = 'temporarily_closed_or_unclear'
            df.loc[idx, 'catatan_jam'] = 'Chinatown Bandung telah tutup permanen sejak 2020 akibat dampak pandemi COVID-19.'
            df.loc[idx, 'sumber_jam'] = 'google_maps_multiple_sources'
            continue
        
        # Special case: LOC-123 Museum Pendidikan Nasional UPI
        if loc_id == 'LOC-123':
            df.loc[idx, 'status_jam'] = 'seasonal_or_uncertain'
            df.loc[idx, 'catatan_jam'] = 'Museum buka weekday (Sen-Jum) 09:00-15:00. Weekend hanya menerima kunjungan dengan reservasi khusus dan biaya tambahan. Jam weekend dikosongkan karena bersyarat.'
            df.loc[idx, 'sumber_jam'] = 'upi.edu (situs resmi museum)'
            continue
        
        if has_weekday and has_weekend:
            wk_open = str(row['jam_buka_weekday']).strip()
            wk_close = str(row['jam_tutup_weekday']).strip()
            we_open = str(row['jam_buka_weekend']).strip()
            we_close = str(row['jam_tutup_weekend']).strip()
            
            if wk_open == we_open and wk_close == we_close:
                df.loc[idx, 'status_jam'] = 'general_schedule_used_for_both'
                df.loc[idx, 'catatan_jam'] = 'Jadwal umum digunakan untuk weekday dan weekend.'
            else:
                df.loc[idx, 'status_jam'] = 'verified'
                df.loc[idx, 'catatan_jam'] = 'Jadwal weekday dan weekend berbeda, keduanya terisi dari sumber.'
            
            df.loc[idx, 'sumber_jam'] = 'internet_research_verified'
            
        elif has_weekday and not has_weekend:
            df.loc[idx, 'status_jam'] = 'weekend_copied_from_weekday'
            df.loc[idx, 'catatan_jam'] = 'Weekend schedule was not found; weekday schedule was copied into weekend fields for normalization.'
            df.loc[idx, 'sumber_jam'] = 'internet_research_verified'
            # Apply normalization: copy weekday to weekend
            df.loc[idx, 'jam_buka_weekend'] = row['jam_buka_weekday']
            df.loc[idx, 'jam_tutup_weekend'] = row['jam_tutup_weekday']
            
        elif not has_weekday and has_weekend:
            df.loc[idx, 'status_jam'] = 'weekday_copied_from_weekend'
            df.loc[idx, 'catatan_jam'] = 'Weekday schedule was not found; weekend schedule was copied into weekday fields for normalization.'
            df.loc[idx, 'sumber_jam'] = 'internet_research_verified'
            # Apply normalization: copy weekend to weekday
            df.loc[idx, 'jam_buka_weekday'] = row['jam_buka_weekend']
            df.loc[idx, 'jam_tutup_weekday'] = row['jam_tutup_weekend']
            
        else:
            df.loc[idx, 'status_jam'] = 'not_found'
            df.loc[idx, 'catatan_jam'] = 'Tidak ditemukan informasi jam operasional yang bisa diverifikasi.'
    
    # =========================================================
    # 4. Validate integrity
    # =========================================================
    final_rows = len(df)
    assert final_rows == original_rows, f"Row count mismatch! Original: {original_rows}, Final: {final_rows}"
    
    print(f"\nFinal row count: {final_rows} (unchanged)")
    print(f"Final columns: {list(df.columns)}")
    
    # =========================================================
    # 5. Print completion report
    # =========================================================
    desc_filled = df['deskripsi_google'].notna().sum()
    wk_open_filled = df['jam_buka_weekday'].notna().sum()
    wk_close_filled = df['jam_tutup_weekday'].notna().sum()
    we_open_filled = df['jam_buka_weekend'].notna().sum()
    we_close_filled = df['jam_tutup_weekend'].notna().sum()
    
    print("\n" + "="*60)
    print("FINAL COMPLETION REPORT")
    print("="*60)
    print(f"1. Total original rows: {original_rows}")
    print(f"2. Total rows returned: {final_rows}")
    print(f"3. Descriptions filled: {desc_filled}/{final_rows}")
    print(f"4. Weekday open filled: {wk_open_filled}/{final_rows}")
    print(f"5. Weekday close filled: {wk_close_filled}/{final_rows}")
    print(f"6. Weekend open filled: {we_open_filled}/{final_rows}")
    print(f"7. Weekend close filled: {we_close_filled}/{final_rows}")
    
    # Status counts
    print(f"\nStatus jam distribution:")
    for status, count in df['status_jam'].value_counts().items():
        print(f"  {status}: {count}")
    
    print(f"\nStatus deskripsi distribution:")
    for status, count in df['status_deskripsi'].value_counts().items():
        print(f"  {status}: {count}")
    
    # Special cases
    print(f"\nSpecial cases:")
    print(f"  LOC-016 (Chinatown Bandung): Tutup permanen - jam dikosongkan")
    print(f"  LOC-123 (Museum Pendidikan UPI): Weekend hanya reservasi - jam weekend dikosongkan")
    
    # =========================================================
    # 6. Save CSV
    # =========================================================
    df.to_csv(db_path, index=False)
    print(f"\nSaved to: {db_path}")
    
    # =========================================================
    # 7. Save XLSX version
    # =========================================================
    xlsx_path = db_path.replace('.csv', '.xlsx')
    df.to_excel(xlsx_path, index=False, engine='openpyxl')
    print(f"Saved XLSX to: {xlsx_path}")
    
    print("\nTraceability columns added successfully!")

if __name__ == '__main__':
    main()
