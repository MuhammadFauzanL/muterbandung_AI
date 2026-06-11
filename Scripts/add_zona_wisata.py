import pandas as pd
import os

DB_PATH = os.path.join(
    "Wisata_Workspace",
    "01_Dataset",
    "3_Curated",
    "DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv"
)

def get_zone(lat, lon):
    if lon < 107.56:
        return "Barat"
    if lon > 107.68:
        return "Timur"
    if lat > -6.86:
        return "Utara"
    if lat < -6.96:
        return "Selatan"
    return "Tengah"

def main():
    print(f"Loading {DB_PATH}...")
    df = pd.read_csv(DB_PATH)
    
    print("Calculating zona_wisata...")
    df['zona_wisata'] = df.apply(lambda r: get_zone(r['latitude'], r['longitude']), axis=1)
    
    print("Zone distribution:")
    print(df['zona_wisata'].value_counts())
    
    df.to_csv(DB_PATH, index=False)
    print(f"Successfully saved updated database with zona_wisata column to {DB_PATH}")

if __name__ == "__main__":
    main()
