import pandas as pd
import re
import time
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# ============================================================
# FASE 4 - LANGKAH 1: Advanced NLP Preprocessing
# ============================================================

SLANG_DICT = {
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
    "dmn": "dimana", "aja": "saja", "aj": "saja",
    "cpt": "cepat", "cepet": "cepat",
    "bnyk": "banyak", "pgn": "ingin", "pengen": "ingin", "pengin": "ingin",
    "msh": "masih", "nih": "ini",
    "mantep": "mantap", "asik": "asyik",
    "rame": "ramai", "view": "pemandangan", "spot foto": "lokasi foto",
    "worth it": "sebanding", "worth": "sebanding",
    "best": "terbaik", "must visit": "wajib dikunjungi",
    "recommended": "direkomendasikan", "overrated": "tidak sesuai ekspektasi",
    "underrated": "tersembunyi", "hidden gem": "permata tersembunyi",
    "tiket mahal": "harga tiket mahal", "parkir susah": "parkir sulit",
    "parkiran penuh": "parkir penuh", "toilet kotor": "fasilitas toilet kotor",
    "ramah anak": "cocok untuk anak", "anak anak": "anak-anak",
}

CUSTOM_STOPWORDS = {
    'dengan', 'dan', 'di', 'ke', 'dari', 'yang', 'untuk', 'pada', 'ini',
    'itu', 'atau', 'juga', 'sudah', 'saya', 'kami', 'kita', 'mereka',
    'bisa', 'ada', 'tidak', 'nya', 'lebih', 'satu', 'sangat', 'akan',
    'tapi', 'karena', 'kalau', 'lagi', 'sama', 'mau', 'jadi', 'sekali',
    'masih', 'belum', 'saja', 'hanya', 'apa', 'siapa', 'kapan', 'mana',
    'bagaimana', 'mengapa', 'oleh', 'jika', 'kali', 'orang',
    'memang', 'walaupun', 'meskipun', 'malah', 'bahkan', 'selain',
    'ya', 'yah', 'oh', 'ah', 'eh', 'hmm', 'bandung', 'tempat'
}

factory_stem = StemmerFactory()
factory_stop = StopWordRemoverFactory()
stemmer = factory_stem.create_stemmer()
stopword_rem = factory_stop.create_stop_word_remover()

def basic_clean(text):
    text = str(text).lower()
    text = re.sub(r'[^\x00-\x7F\u00C0-\u024F]', '', text)
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def slang_normalize(text):
    text = str(text).lower().strip()
    for slang, baku in SLANG_DICT.items():
        text = re.sub(r'\b' + re.escape(slang) + r'\b', baku, text)
    return text

def remove_stopwords(text):
    text = stopword_rem.remove(text)
    words = text.split()
    words = [w for w in words if w not in CUSTOM_STOPWORDS and len(w) > 2]
    return ' '.join(words)

def stem_text(text):
    return stemmer.stem(text)

def preprocess_full(text):
    text = basic_clean(text)
    text = slang_normalize(text)
    text = remove_stopwords(text)
    text = stem_text(text)
    return text

# ============================================================
# FASE 4 - LANGKAH 2: Aspect Extraction
# ============================================================

# Kamus Aspek (Diperluas berdasarkan temuan EDA)
ASPECT_KEYWORDS = {
    'pemandangan': [
        'pemandangan', 'view', 'indah', 'cantik', 'bagus', 'foto', 'spot',
        'landscape', 'panorama', 'asri', 'hijau', 'alam', 'sejuk', 'udara',
        'sunrise', 'sunset', 'danau', 'air', 'curug', 'air terjun', 'gunung',
        'bukit', 'sawah'
    ],
    'harga': [
        'tiket', 'harga', 'mahal', 'murah', 'biaya', 'bayar', 'gratis',
        'htm', 'masuk', 'tarif', 'terjangkau', 'ekonomis', 'kantong',
        'sebanding', 'worth', 'preis', 'cost', 'free', 'charge'
    ],
    'fasilitas': [
        'parkir', 'toilet', 'kamar mandi', 'mushola', 'masjid', 'warung',
        'kantin', 'restoran', 'cafe', 'tempat duduk', 'bangku', 'gazebo',
        'bersih', 'kotor', 'terawat', 'rusak', 'fasilitas', 'wahana',
        'kebersihan', 'sampah', 'jalan', 'akses', 'macet', 'infrastruktur'
    ],
    'pelayanan': [
        'petugas', 'staff', 'pelayan', 'ramah', 'sopan', 'baik', 'buruk',
        'tidak ramah', 'cuek', 'responsif', 'cepat', 'lambat', 'pelayanan',
        'layanan', 'security', 'satpam', 'guide'
    ],
    'keluarga': [
        'anak', 'keluarga', 'cocok', 'anak-anak', 'balita', 'bermain',
        'playground', 'outbond', 'edukasi', 'belajar', 'seru', 'senang',
        'happy', 'kids', 'family', 'rekreasi', 'liburan keluarga'
    ]
}

def extract_aspects(text_original: str, text_processed: str) -> dict:
    """
    Mendeteksi aspek wisata dalam ulasan menggunakan lexicon matching.
    Mencocokkan pada KEDUA versi teks (original & processed) untuk cakupan maksimal.
    Mengembalikan dict aspek yang terdeteksi (True/False).
    """
    combined = (str(text_original) + ' ' + str(text_processed)).lower()
    result = {}
    for aspect, keywords in ASPECT_KEYWORDS.items():
        detected = any(kw in combined for kw in keywords)
        result[f'aspek_{aspect}'] = detected
    return result

def count_aspects(row):
    """Menghitung berapa banyak aspek yang terdeteksi dalam satu ulasan."""
    return sum([row[f'aspek_{a}'] for a in ASPECT_KEYWORDS.keys()])

# ============================================================
# EKSEKUSI KE SELURUH DATA (16.000 Baris)
# ============================================================
print("Memuat dataset yang sudah dibersihkan...")
df = pd.read_csv('Dataset/MASTER_REVIEWS_CLEANED.csv')
print(f"Total data dimuat: {len(df)} baris")

# Langkah 1: NLP Preprocessing
print("\nMenjalankan NLP Preprocessing (Slang Norm + Stopword + Stemming)...")
print("Estimasi waktu: 2-3 menit untuk 16.000 data...")
start = time.time()
df['review_nlp'] = df['review_text_clean'].apply(preprocess_full)
elapsed = time.time() - start
print(f"Preprocessing selesai dalam {elapsed:.0f} detik!")

# Langkah 2: Aspect Extraction
print("\nMenjalankan Aspect Extraction pada seluruh data...")
aspect_results = df.apply(
    lambda row: extract_aspects(row['review_text'], row['review_nlp']),
    axis=1
)
df_aspects = pd.DataFrame(list(aspect_results))
df = pd.concat([df, df_aspects], axis=1)
df['jumlah_aspek_terdeteksi'] = df.apply(count_aspects, axis=1)

# ============================================================
# SIMPAN HASIL
# ============================================================
df.to_csv('Dataset/MASTER_REVIEWS_NLP.csv', index=False, encoding='utf-8')
print("\nFile tersimpan: Dataset/MASTER_REVIEWS_NLP.csv")

# ============================================================
# LAPORAN VERIFIKASI OUTPUT
# ============================================================
print("\n" + "="*65)
print("LAPORAN VERIFIKASI OUTPUT")
print("="*65)

print(f"\nTotal Baris Diproses: {len(df)}")
print(f"Kolom baru ditambahkan: review_nlp + 5 kolom aspek + jumlah_aspek_terdeteksi")

print("\n--- DISTRIBUSI ASPEK TERDETEKSI ---")
for aspek in ASPECT_KEYWORDS.keys():
    col = f'aspek_{aspek}'
    jumlah = df[col].sum()
    persen = jumlah / len(df) * 100
    print(f"  Aspek '{aspek.title()}': {jumlah} ulasan ({persen:.1f}%)")

print("\n--- DISTRIBUSI JUMLAH ASPEK PER ULASAN ---")
print(df['jumlah_aspek_terdeteksi'].value_counts().sort_index().to_string())

print("\n--- CONTOH HASIL (5 Sampel) ---")
sample = df[['review_text', 'review_nlp', 'aspek_pemandangan', 'aspek_harga', 'aspek_fasilitas', 'aspek_keluarga']].sample(5, random_state=42)
print(sample.to_string())
