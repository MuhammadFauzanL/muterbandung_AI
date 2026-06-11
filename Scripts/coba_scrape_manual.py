import requests
from bs4 import BeautifulSoup
import time
import urllib.parse
import sys

# Memastikan output terminal tidak error karena emoji
sys.stdout.reconfigure(encoding='utf-8')

# Header agar kita pura-pura menjadi Browser Chrome biasa (bukan bot)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
}

# Kita coba 3 lokasi saja dulu
lokasi_test = [
    "23 Paskal Shopping Center Bandung",
    "Alam Wisata Cimahi Bandung",
    "Gunung Tangkuban Parahu Bandung"
]

print("=== MEMULAI TEST PYTHON WEB SCRAPING GOOGLE ===")

for lokasi in lokasi_test:
    query = urllib.parse.quote_plus(f"jam buka {lokasi}")
    url = f"https://www.google.co.id/search?q={query}"
    
    print(f"\n[Scraping] Mencari: {lokasi}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(">> Berhasil masuk ke halaman Google.")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Google sering menyembunyikan jam buka di dalam class acak yang terus berubah (misal: "BNeawe", "vk_sh", dll)
            # Ini membuat scraping manual sangat rapuh
            teks_halaman = soup.get_text()
            
            if "Buka" in teks_halaman or "Tutup" in teks_halaman or "Open" in teks_halaman:
                print("   -> Kata kunci 'Buka/Tutup' ditemukan di HTML mentah.")
                print("   -> TETAPI: Mengekstrak jam persisnya sangat sulit karena Google mengacak nama Class HTML-nya setiap hari.")
            else:
                print("   -> Data jam buka tidak ditemukan secara gamblang di halaman.")
                
        elif response.status_code == 429:
            print(">> ERROR 429: TERBLOKIR! Google mendeteksi kita sebagai Bot/Scraper dan meminta CAPTCHA.")
            break
        else:
            print(f">> Gagal dengan kode status: {response.status_code}")
            
    except Exception as e:
        print(f">> Error saat scraping: {e}")
        
    # Jeda agar tidak langsung diblokir detik itu juga
    time.sleep(3)

print("\n=== TEST SELESAI ===")
