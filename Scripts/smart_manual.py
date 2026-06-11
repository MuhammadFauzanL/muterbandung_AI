import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

print("Mencari data aktual via Google Search Scraping...")

# Load the file we just corrupted with ArcGIS and fix it.
# We will identify the generic or wrong coordinates.
df = pd.read_csv('DATABASE_WISATA_FINAL_LENGKAP.csv')

# The generic bandung coordinate from ArcGIS
generic_lat = -6.92222
generic_lon = 107.60694

def is_wrong_coord(lat, lon):
    if pd.isnull(lat) or pd.isnull(lon): return True
    if abs(lat - generic_lat) < 0.001 and abs(lon - generic_lon) < 0.001: return True
    # Out of West Java (roughly -5.5 to -8.0, 106.0 to 109.0)
    if not (-8.5 < lat < -5.5): return True
    if not (106.0 < lon < 109.0): return True
    return False

# Find all that need fixing
needs_fix = []
for idx, row in df.iterrows():
    if is_wrong_coord(row['latitude'], row['longitude']) or row['location_name'] in [
        'Taman Alun-Alun Kota Cimahi', 'Taman Lalu Lintas Ade Irma Suryani Nasution'
    ]: # Just to be safe, we'll re-check some of the suspicious ones.
        # Actually, let's just use the original missing list from `wisata_perlu_manual_final.csv`
        pass

sukses = 0
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
for idx, row in df.iterrows():
    if is_wrong_coord(row['latitude'], row['longitude']) or row['location_name'] in ['Taman Alun-Alun Kota Cimahi', 'Taman Lalu Lintas Ade Irma Suryani Nasution']:
        nama = row['location_name']
        print(f"Mencari Google: {nama} ...", end=" ")
        
        q = f"koordinat {nama} Bandung Jawa Barat"
        url = f"https://www.google.com/search?q={q.replace(' ', '+')}"
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Google often displays coordinates in the format: 6°55'18.6"S 107°36'25.0"E
            # Or as decimal: -6.921833, 107.606944
            text = soup.get_text()
            
            # Look for decimal coords in text
            matches = re.findall(r'(-[678]\.\d{3,8})[\s,]+(10[678]\.\d{3,8})', text)
            if matches:
                lat, lon = float(matches[0][0]), float(matches[0][1])
                # Ensure it's not the generic center of Bandung
                if abs(lat - generic_lat) > 0.001 or abs(lon - generic_lon) > 0.001:
                    df.loc[idx, 'latitude'] = lat
                    df.loc[idx, 'longitude'] = lon
                    print(f"[OK] {lat}, {lon}")
                    sukses += 1
                    time.sleep(2)
                    continue
            
            # If not found, try to find a map link
            map_links = soup.find_all('a', href=re.compile(r'maps/place'))
            found = False
            for link in map_links:
                href = link.get('href')
                m = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', href)
                if m:
                    lat, lon = float(m.group(1)), float(m.group(2))
                    df.loc[idx, 'latitude'] = lat
                    df.loc[idx, 'longitude'] = lon
                    print(f"[OK] (Map) {lat}, {lon}")
                    found = True
                    sukses += 1
                    break
            
            if not found:
                print("[FAIL] Gagal")
                
        except Exception as e:
            print(f"[ERROR] {e}")
            
        time.sleep(2)

df.to_csv('DATABASE_WISATA_FINAL_LENGKAP.csv', index=False)
print(f"\nBerhasil memperbaiki {sukses} data secara akurat!")
