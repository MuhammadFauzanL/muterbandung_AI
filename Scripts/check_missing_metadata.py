import pandas as pd

def main():
    df = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    missing_desc = df[df['description'].isna()]
    missing_hours = df[df['jam_buka_weekday'].isna()]
    print('Total rows:', len(df))
    print('Missing description:', len(missing_desc))
    print('Missing hours:', len(missing_hours))
    print('\nFirst 20 missing description:')
    for idx, r in missing_desc.head(20).iterrows():
        print(f"  {r['location_id']}: {r['location_name']}")
    print('\nFirst 20 missing hours:')
    for idx, r in missing_hours.head(20).iterrows():
        print(f"  {r['location_id']}: {r['location_name']}")

if __name__ == '__main__':
    main()
