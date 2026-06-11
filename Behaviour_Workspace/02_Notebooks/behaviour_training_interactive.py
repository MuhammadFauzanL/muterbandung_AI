import pandas as pd
import numpy as np
import warnings
from pathlib import Path
import time
import sys
import io

# Force UTF-8 for printing
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
warnings.filterwarnings('ignore')

def print_header(text):
    print("\n" + "="*60)
    print(f" {text}")
    print("="*60 + "\n")

def print_markdown(text):
    print(f"\n{text}\n")

# --- MUKADIMAH ---
print_header("Behaviour Model Training (MuterBandung)")
print_markdown("Program ini mendokumentasikan proses pelatihan Behaviour Model.\n"
               "Berbeda dengan sistem rekomendasi awal, model ini memprediksi niat wisatawan:\n"
               "'Jika turis baru saja ke wisata X, ke manakah mereka selanjutnya?'")

# --- TAHAP 1 ---
print_header("TAHAP 1: Memuat Data Mentah")
dataset_path = Path(r'D:\File\file\Fauzan Lubada\PIJAK\Wisata_Workspace\01_Dataset\Massive-STEPS\data\bandung\bandung_checkins_train.csv')

print("Memuat dataset Massive-STEPS...")
df_raw = pd.read_csv(dataset_path)
print(f"Total Data Mentah: {df_raw.shape[0]} Baris, {df_raw.shape[1]} Kolom.")
print("\n5 Baris Pertama Data:")
print(df_raw.head().to_string())

# --- TAHAP 2 ---
print_header("TAHAP 2: Audit & Kualitas Data")
print("Cek kelengkapan data (Missing Values):")
print(df_raw.isnull().sum())

duplicates = df_raw.duplicated().sum()
print(f"\nCek Duplikasi: Terdapat {duplicates} baris data duplikat persis.")

# --- TAHAP 3 ---
print_header("TAHAP 3: Audit Kategori Foursquare Mentah")
unique_categories = df_raw['venue_category'].nunique()
print(f"Terdapat {unique_categories} kategori unik Foursquare.\n")

print("--- TOP 40 KATEGORI PALING BANYAK DIKUNJUNGI ---")
top_categories = df_raw['venue_category'].value_counts().head(40)
print(top_categories.to_string())

print_header("TAHAP 4: Observasi Manual & Diskusi")
print_markdown("Berdasarkan daftar distribusi di atas, terlihat banyak kategori 'noise'\n"
               "atau aktivitas harian bukan wisata (misal: College Academic Building, High School, Office).")

print_markdown(">>> PROGRAM DIHENTIKAN SEMENTARA (PAUSE) <<<")
print("Silakan pelajari output distribusi data kategori di atas.")
input("Tekan tombol ENTER pada keyboard Anda di terminal ini jika sudah siap untuk melakukan mapping kategori...")

print_header("TAHAP 5: Proses Filtering & Mapping")
print("Memulai proses pemetaan (Mapping) ke Kategori MuterBandung...")
# Proses mapping dan training akan ditaruh di sini nantinya!
print("--- Selesai untuk sesi tahap awal ini ---")
sys.exit(0)
