import pandas as pd
import json
import difflib

def main():
    # Load datasets
    try:
        df_reviews = pd.read_csv('MASTER_REVIEWS_ENRICHED.csv', low_memory=False)
        review_file = 'MASTER_REVIEWS_ENRICHED.csv'
    except FileNotFoundError:
        try:
            df_reviews = pd.read_csv('MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv', low_memory=False)
            review_file = 'MuterBandung_Colab_Package/MASTER_REVIEWS_NLP.csv'
        except FileNotFoundError:
            print('Could not find review dataset.')
            return

    df_locs = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv', low_memory=False)

    review_locs = set(df_reviews['location_name'].unique())
    master_locs = set(df_locs['location_name'].unique())

    mismatched = sorted(list(review_locs - master_locs))
    master_locs_list = list(master_locs)

    mapping = {}
    unmapped = []

    print(f'Attempting to auto-map {len(mismatched)} locations...')

    for m in mismatched:
        # Try exact case-insensitive match first
        exact_match = next((loc for loc in master_locs_list if loc.lower() == m.lower()), None)
        if exact_match:
            mapping[m] = exact_match
            continue
            
        # Try fuzzy match
        matches = difflib.get_close_matches(m, master_locs_list, n=1, cutoff=0.5)
        if matches:
            mapping[m] = matches[0]
        else:
            unmapped.append(m)

    # Save the proposed mapping
    with open('proposed_location_mapping.json', 'w', encoding='utf-8') as f:
        json.dump({'mapping': mapping, 'unmapped': unmapped, 'review_file': review_file}, f, indent=4)

    print(f'Successfully auto-mapped: {len(mapping)}')
    print(f'Failed to map: {len(unmapped)}')

    print('\nSample mappings:')
    for k, v in list(mapping.items())[:10]:
        print(f'"{k}" -> "{v}"')

    if unmapped:
        print('\nUnmapped locations:')
        for u in unmapped[:10]:
            print(f' - {u}')

if __name__ == '__main__':
    main()
