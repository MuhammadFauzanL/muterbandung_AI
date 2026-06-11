import pandas as pd
import re

df = pd.read_csv('DATABASE_WISATA_DENGAN_METADATA.csv', low_memory=False)

print('=== FINAL DATASET VERIFICATION ===')
print(f'Row count: {len(df)}')
print(f'Column count: {len(df.columns)}')
print(f'Columns: {list(df.columns)}')
print()

# Required enrichment columns
req_cols = ['deskripsi_google','jam_buka_weekday','jam_tutup_weekday','jam_buka_weekend','jam_tutup_weekend']
print('Required enrichment columns present:')
for c in req_cols:
    present = c in df.columns
    filled = df[c].notna().sum() if present else 0
    status = 'YES' if present else 'NO'
    print(f'  {c}: {status} ({filled}/{len(df)} filled)')

# Traceability columns
trace_cols = ['sumber_deskripsi','sumber_jam','status_deskripsi','status_jam','catatan_jam']
print()
print('Traceability columns present:')
for c in trace_cols:
    present = c in df.columns
    filled = df[c].notna().sum() if present else 0
    status = 'YES' if present else 'NO'
    print(f'  {c}: {status} ({filled}/{len(df)} filled)')

# Time format check
print()
print('=== TIME FORMAT VALIDATION ===')
time_cols = ['jam_buka_weekday','jam_tutup_weekday','jam_buka_weekend','jam_tutup_weekend']
for tc in time_cols:
    vals = df[tc].dropna().astype(str)
    bad = vals[~vals.str.match(r'^\d{2}:\d{2}$')]
    if len(bad) > 0:
        print(f'  {tc}: {len(bad)} INVALID values found')
        print(f'    Examples: {bad.head(3).tolist()}')
    else:
        print(f'  {tc}: All {len(vals)} values are valid HH:MM')

# Duplicate row check
print()
print('=== DUPLICATE CHECK ===')
dups = df.duplicated(subset=['location_id']).sum()
print(f'Duplicate location_id: {dups}')

# Sample
print()
print('=== SAMPLE ROWS (with traceability) ===')
sample_ids = ['LOC-001','LOC-002','LOC-016','LOC-123']
for sid in sample_ids:
    r = df[df['location_id']==sid].iloc[0]
    desc_preview = str(r['deskripsi_google'])[:80]
    print(f"{r['location_id']}: {r['location_name']}")
    print(f"  deskripsi: {desc_preview}...")
    print(f"  jam_weekday: {r['jam_buka_weekday']}-{r['jam_tutup_weekday']}")
    print(f"  jam_weekend: {r['jam_buka_weekend']}-{r['jam_tutup_weekend']}")
    print(f"  status_deskripsi: {r['status_deskripsi']}")
    print(f"  status_jam: {r['status_jam']}")
    print(f"  catatan_jam: {r['catatan_jam']}")
    print()
