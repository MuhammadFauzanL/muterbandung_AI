import pandas as pd
import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

print("="*65)
print("FASE 4 - LANGKAH 1: Advanced NLP Preprocessing")
print("="*65)

# ============================================================
# 1A. KAMUS SLANG NORMALIZATION (Lengkap untuk konteks wisata)
# ============================================================
SLANG_DICT = {
    # Singkatan umum
    "yg": "yang", "dg": "dengan", "dgn": "dengan", "sy": "saya",
    "ga": "tidak", "gak": "tidak", "nggak": "tidak", "ngga": "tidak",
    "enggak": "tidak", "ndak": "tidak",
    "bgt": "banget", "bngt": "banget",
    "hrs": "harus", "sgt": "sangat",
    "bs": "bisa", "tdk": "tidak", "krn": "karena",
    "jg": "juga", "jgn": "jangan", "blm": "belum",
    "udah": "sudah", "udh": "sudah", "sdh": "sudah",
    "lg": "lagi", "lbh": "lebih", "skrg": "sekarang",
    "emg": "memang", "emang": "memang",
    "kl": "kalau", "klo": "kalau", "klu": "kalau",
    "tp": "tapi", "tpi": "tapi",
    "sm": "sama", "dr": "dari",
    "utk": "untuk", "u": "untuk",
    "mk": "maka", "dpt": "dapat",
    "dmn": "dimana", "dr mana": "dari mana",
    "aja": "saja", "aj": "saja",
    "ke sini": "kesini", "ke sana": "kesana",
    "cpt": "cepat", "cepet": "cepat",

    # Konteks Pariwisata Bandung
    "ancur": "hancur", "bnyk": "banyak",
    "pgn": "ingin", "pengen": "ingin", "pengin": "ingin",
    "msh": "masih", "nih": "ini", "itu sih": "itu",
    "keren": "keren", "mantep": "mantap", "mantap": "mantap",
    "asik": "asyik", "seru": "menyenangkan",
    "jelek": "buruk", "ancur": "hancur", "rusak bgt": "sangat rusak",
    "bagus bgt": "sangat bagus", "indah bgt": "sangat indah",
    "mahal bgt": "sangat mahal", "murah bgt": "sangat murah",
    "rame": "ramai", "sepi bgt": "sangat sepi",
    "kotor bgt": "sangat kotor", "bersih bgt": "sangat bersih",
    "panas bgt": "sangat panas", "dingin bgt": "sangat dingin",
    "view": "pemandangan", "spot foto": "lokasi foto",
    "worth it": "sebanding", "worth": "sebanding",
    "best": "terbaik", "must visit": "wajib dikunjungi",
    "recommended": "direkomendasikan", "overrated": "tidak sesuai ekspektasi",
    "underrated": "tersembunyi", "hidden gem": "permata tersembunyi",
    "masuk gratis": "gratis", "gratis masuk": "gratis",
    "tiket mahal": "harga tiket mahal", "parkir susah": "parkir sulit",
    "parkiran penuh": "parkir penuh", "macet": "macet",
    "toilet kotor": "fasilitas toilet kotor",
    "mushola ada": "tersedia mushola",
    "ramah anak": "cocok untuk anak",
    "anak anak": "anak-anak", "bawa anak": "membawa anak",
}

def slang_normalize(text: str) -> str:
    """Normalisasi kata slang dan singkatan menggunakan kamus kustom."""
    text = str(text).lower().strip()
    for slang, baku in SLANG_DICT.items():
        text = re.sub(r'\b' + re.escape(slang) + r'\b', baku, text)
    return text

# ============================================================
# 1B. FUNGSI PEMBERSIHAN TEKS DASAR
# ============================================================
def basic_clean(text: str) -> str:
    """Membersihkan karakter noise dari teks."""
    text = str(text).lower()
    # Hapus emoji dan karakter unicode non-ASCII
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u0400-\u04FF\u0600-\u06FF]', '', text)
    # Hapus URL
    text = re.sub(r'http\S+|www\.\S+', '', text)
    # Hapus mention (@username)
    text = re.sub(r'@\w+', '', text)
    # Hapus tanda baca berlebih (kecuali tanda yang membantu NLP)
    text = re.sub(r'[^\w\s]', ' ', text)
    # Hapus angka yang berdiri sendiri
    text = re.sub(r'\b\d+\b', '', text)
    # Hapus spasi ganda
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ============================================================
# 1C. INISIALISASI SASTRAWI (Stemmer & Stopword)
# ============================================================
print("Menginisialisasi Sastrawi Stemmer & Stopword Remover...")
factory_stem  = StemmerFactory()
factory_stop  = StopWordRemoverFactory()
stemmer       = factory_stem.create_stemmer()
stopword_rem  = factory_stop.create_stop_word_remover()

# Tambahkan stopwords kustom yang tidak relevan untuk NLP wisata
CUSTOM_STOPWORDS = {
    'dengan', 'dan', 'di', 'ke', 'dari', 'yang', 'untuk', 'pada', 'ini',
    'itu', 'atau', 'juga', 'sudah', 'saya', 'kami', 'kita', 'mereka',
    'bisa', 'ada', 'tidak', 'nya', 'lebih', 'satu', 'sangat', 'akan',
    'tapi', 'karena', 'kalau', 'lagi', 'sama', 'mau', 'jadi', 'sekali',
    'masih', 'belum', 'saja', 'hanya', 'apa', 'siapa', 'kapan', 'mana',
    'bagaimana', 'mengapa', 'oleh', 'jika', 'kali', 'orang',
    'memang', 'walaupun', 'meskipun', 'malah', 'bahkan', 'selain',
    'ya', 'yah', 'oh', 'ah', 'eh', 'hmm', 'ugh', 'wow',
    'bandung', 'tempat' # kata terlalu umum untuk konteks ini
}

def remove_stopwords(text: str) -> str:
    """Menghapus stopword menggunakan Sastrawi + daftar kustom."""
    # Sastrawi stopword remover
    text = stopword_rem.remove(text)
    # Tambahan custom stopwords
    words = text.split()
    words = [w for w in words if w not in CUSTOM_STOPWORDS and len(w) > 2]
    return ' '.join(words)

def stem_text(text: str) -> str:
    """Stemming menggunakan Sastrawi."""
    return stemmer.stem(text)

# ============================================================
# 1D. PIPELINE LENGKAP
# ============================================================
def preprocess_full(text: str) -> str:
    """Pipeline utama: Clean → Slang Norm → Stopword → Stem"""
    text = basic_clean(text)
    text = slang_normalize(text)
    text = remove_stopwords(text)
    text = stem_text(text)
    return text

# ============================================================
# VALIDASI: Cek 5 Sampel Teks Sebelum & Sesudah
# ============================================================
test_samples = [
    "Tempat ini bgt keren bgt, view-nya mantep, worth it banget!",
    "Parkiran penuh, toilet kotor bgt, tiket mahal tapi ga sebanding",
    "Bawa anak ke sini, cocok banget utk keluarga, anak2 seneng",
    "Pemandangannya indah bgt, tp jalan menuju sana macet parah",
    "Ga recommended, overrated, lebih baik ke tempat lain aja"
]

print("\n--- VALIDASI PIPELINE NLP (5 Sampel) ---")
for i, sample in enumerate(test_samples, 1):
    result = preprocess_full(sample)
    print(f"\n[{i}] ORIGINAL : {sample}")
    print(f"    PROCESSED: {result}")

print("\n✅ Validasi Pipeline selesai. Pipeline siap dijalankan ke 16.000 data!")
