import os
import zipfile
import pandas as pd
from difflib import SequenceMatcher

WORKSPACE_DIR = r"D:\File\file\Fauzan Lubada\PIJAK\Penginapan_Workspace"
CURATED_DIR = os.path.join(WORKSPACE_DIR, "02_Curated")
ZIP_PATH = r"D:\File\file\Fauzan Lubada\PIJAK\drive-download-20260613T233342Z-3-001.zip"

PRIMARY_DATASET_PATH = os.path.join(CURATED_DIR, "PENGINAPAN_PRIMARY_DATA_FOCUS_CANDIDATE_SENTIMENT_UPDATED_2026-06-14.csv")

OUT_ACCEPTED = os.path.join(CURATED_DIR, "PENGINAPAN_RAW_ZIP_AUDIT_ACCEPTED_2026-06-14.csv")
OUT_HELD = os.path.join(CURATED_DIR, "PENGINAPAN_RAW_ZIP_AUDIT_HELD_2026-06-14.csv")

def normalize(text):
    if pd.isna(text):
        return ""
    return str(text).strip().lower()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def main():
    print("=== AUDIT RAW REVIEWS FROM ZIP ===")
    
    # 1. Load Primary Dataset for Matching
    print("Loading Primary Dataset...")
    df_primary = pd.read_csv(PRIMARY_DATASET_PATH, low_memory=False)
    
    # Create a quick dictionary for fast lookup
    primary_dict = {}
    for idx, row in df_primary.iterrows():
        p_id = row['penginapan_id']
        name_norm = normalize(row['name'])
        sentiment_missing = pd.isna(row.get('hotel_adjusted_sentiment_score'))
        
        # We store the ID, Original Name, and whether it urgently needs sentiment
        primary_dict[name_norm] = {
            'id': p_id,
            'name': row['name'],
            'needs_sentiment': sentiment_missing,
            'type': row.get('property_type_final_after_p3', 'unknown')
        }
        
    print(f"Loaded {len(primary_dict)} unique properties from Primary.")
    
    # 2. Read Raw CSVs from ZIP
    print("\nExtracting and Reading ZIP...")
    raw_dfs = []
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        for filename in z.namelist():
            if filename.endswith('.csv'):
                with z.open(filename) as f:
                    df_temp = pd.read_csv(f, low_memory=False)
                    raw_dfs.append(df_temp)
                    print(f"  Read {filename}: {len(df_temp)} rows")
                    
    if not raw_dfs:
        print("No CSV files found in ZIP.")
        return
        
    df_raw = pd.concat(raw_dfs, ignore_index=True)
    print(f"\nTotal Raw Reviews: {len(df_raw)}")
    
    # 3. Matching Logic
    print("Starting Matching Process (Fuzzy >= 90%)... This may take a moment.")
    
    accepted_rows = []
    held_rows = []
    
    # Get unique titles from raw to minimize fuzzy matching calls
    unique_titles = df_raw['title'].dropna().unique()
    title_mapping = {} # raw_title -> match result
    
    for title in unique_titles:
        title_norm = normalize(title)
        
        # Fast exact match
        if title_norm in primary_dict:
            title_mapping[title] = {
                'status': 'ACCEPTED',
                'target': primary_dict[title_norm],
                'match_score': 1.0
            }
            continue
            
        # Fuzzy match >= 90%
        best_match = None
        best_score = 0
        for p_name_norm, p_data in primary_dict.items():
            score = similarity(title_norm, p_name_norm)
            if score > best_score:
                best_score = score
                best_match = p_data
                
        if best_score >= 0.90:
            title_mapping[title] = {
                'status': 'ACCEPTED',
                'target': best_match,
                'match_score': best_score
            }
        else:
            title_mapping[title] = {
                'status': 'HELD',
                'target': None,
                'match_score': best_score
            }
            
    # Apply mapping to dataframe
    print("Applying match results to raw data...")
    for idx, row in df_raw.iterrows():
        title = row.get('title')
        match_info = title_mapping.get(title)
        
        row_dict = row.to_dict()
        if match_info and match_info['status'] == 'ACCEPTED':
            row_dict['audit_status'] = 'ACCEPTED'
            row_dict['target_penginapan_id'] = match_info['target']['id']
            row_dict['target_name'] = match_info['target']['name']
            row_dict['target_type'] = match_info['target']['type']
            row_dict['target_needs_sentiment'] = match_info['target']['needs_sentiment']
            row_dict['match_score'] = match_info['match_score']
            accepted_rows.append(row_dict)
        else:
            row_dict['audit_status'] = 'HELD'
            row_dict['match_score'] = match_info['match_score'] if match_info else 0
            held_rows.append(row_dict)
            
    df_accepted = pd.DataFrame(accepted_rows)
    df_held = pd.DataFrame(held_rows)
    
    print(f"\n=== AUDIT RESULTS ===")
    print(f"Total ACCEPTED: {len(df_accepted)}")
    print(f"Total HELD: {len(df_held)}")
    
    if len(df_accepted) > 0:
        needs_sentiment_count = df_accepted['target_needs_sentiment'].sum()
        print(f"  -> Reviews for targets MISSING sentiment: {needs_sentiment_count}")
        unique_targets = df_accepted['target_penginapan_id'].nunique()
        print(f"  -> Unique properties matched: {unique_targets}")
        
    df_accepted.to_csv(OUT_ACCEPTED, index=False)
    df_held.to_csv(OUT_HELD, index=False)
    
    print(f"\nSaved ACCEPTED to: {os.path.basename(OUT_ACCEPTED)}")
    print(f"Saved HELD to: {os.path.basename(OUT_HELD)}")

if __name__ == "__main__":
    main()
