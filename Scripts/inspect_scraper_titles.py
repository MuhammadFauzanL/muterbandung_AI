import pandas as pd

def main():
    df_db = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv')
    db_names = set(df_db['location_name'].str.lower().str.strip())

    files = [
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-29-27-671.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-33-45-408.csv',
        'dataset_Google-Maps-Reviews-Scraper_2026-05-20_14-58-36-471.csv'
    ]

    for f in files:
        df = pd.read_csv(f)
        print(f'\n--- Analysis for {f} ---')
        titles = df['title'].dropna().unique()
        for t in titles:
            t_clean = t.strip().lower()
            matched = False
            # Exact match
            if t_clean in db_names:
                db_name = df_db[df_db['location_name'].str.lower().str.strip() == t_clean]['location_name'].values[0]
                print(f'  Match: "{t}" -> "{db_name}"')
            else:
                # Check fuzzy / substring match
                possibles = [name for name in df_db['location_name'] if t_clean in name.lower() or name.lower() in t_clean]
                if possibles:
                    print(f'  Partial Match: "{t}" -> {possibles}')
                else:
                    print(f'  NO MATCH (Outlier?): "{t}"')

if __name__ == '__main__':
    main()
