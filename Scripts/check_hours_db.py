import pandas as pd

def main():
    df = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    locs = ['LOC-083', 'LOC-086', 'LOC-095', 'LOC-096', 'LOC-098', 'LOC-102', 'LOC-105', 'LOC-110', 'LOC-111', 'LOC-050', 'LOC-073']
    for l in locs:
        r = df[df['location_id'] == l]
        if len(r) > 0:
            row = r.iloc[0]
            print(f"{l} ({row['location_name']}):")
            print(f"  WD: {row['jam_buka_weekday']} - {row['jam_tutup_weekday']}")
            print(f"  WE: {row['jam_buka_weekend']} - {row['jam_tutup_weekend']}")
            print(f"  Desc: {row['description']}")
            
if __name__ == '__main__':
    main()
