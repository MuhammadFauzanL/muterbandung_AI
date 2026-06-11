import nbformat as nbf

notebook_path = r'd:\File\file\Fauzan Lubada\PIJAK\wisata_traning.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

# ============================================================
# MARKDOWN HEADER FASE 4
# ============================================================
md_fase4 = """## [FASE 4] Advanced NLP Preprocessing & Aspect Extraction

Pada fase ini, teks ulasan yang sudah bersih dari Fase 2 diproses lebih lanjut menjadi representasi yang dapat dipahami oleh mesin AI. Pipeline dijalankan dalam dua langkah besar:

**Langkah 1 — Advanced NLP Preprocessing:**
- **Slang Normalization**: Menerjemahkan singkatan & kata gaul menggunakan kamus kustom (>60 kata)
- **Stopword Removal**: Menggunakan Sastrawi + daftar stopword kustom konteks wisata
- **Stemming**: Menggunakan PySastrawi untuk mereduksi kata ke bentuk dasarnya

**Langkah 2 — Aspect Extraction (ABSA):**  
Mendeteksi aspek wisata dalam setiap ulasan menggunakan pendekatan *Lexicon-Based Matching* pada 5 aspek kunci yang ditemukan saat EDA:
- 🏞️ **Pemandangan** (view, indah, foto, panorama, ...)
- 💰 **Harga** (tiket, mahal, murah, gratis, ...)
- 🚻 **Fasilitas** (parkir, toilet, mushola, jalan, ...)
- 🤝 **Pelayanan** (petugas, ramah, staff, responsif, ...)
- 👨‍👩‍👧 **Keluarga** (anak, cocok, bermain, edukasi, ...)"""

nb.cells.append(nbf.v4.new_markdown_cell(md_fase4))

# ============================================================
# CODE CELL: INSTALL & SETUP
# ============================================================
kode_install = """# Install PySastrawi (hanya perlu dijalankan sekali)
# !pip install PySastrawi

import pandas as pd
import re
import time
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

print("Library berhasil dimuat!")"""
nb.cells.append(nbf.v4.new_code_cell(kode_install))

# ============================================================
# CODE CELL: KAMUS SLANG + FUNGSI PREPROCESSING
# ============================================================
kode_preprocessing = """# Kamus Slang Normalization (Konteks Wisata Bandung)
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
    "mantep": "mantap", "asik": "asyik", "rame": "ramai",
    "view": "pemandangan", "spot foto": "lokasi foto",
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

# Inisialisasi Sastrawi
factory_stem = StemmerFactory()
factory_stop = StopWordRemoverFactory()
stemmer = factory_stem.create_stemmer()
stopword_rem = factory_stop.create_stop_word_remover()

def basic_clean(text):
    text = str(text).lower()
    text = re.sub(r'[^\\x00-\\x7F\\u00C0-\\u024F]', '', text)
    text = re.sub(r'http\\S+|www\\.\\S+', '', text)
    text = re.sub(r'@\\w+', '', text)
    text = re.sub(r'[^\\w\\s]', ' ', text)
    text = re.sub(r'\\b\\d+\\b', '', text)
    text = re.sub(r'\\s+', ' ', text).strip()
    return text

def slang_normalize(text):
    text = str(text).lower().strip()
    for slang, baku in SLANG_DICT.items():
        text = re.sub(r'\\b' + re.escape(slang) + r'\\b', baku, text)
    return text

def remove_stopwords(text):
    text = stopword_rem.remove(text)
    words = text.split()
    words = [w for w in words if w not in CUSTOM_STOPWORDS and len(w) > 2]
    return ' '.join(words)

def stem_text(text):
    return stemmer.stem(text)

def preprocess_full(text):
    \"\"\"Pipeline utama: Clean → Slang Norm → Stopword Removal → Stemming\"\"\"
    text = basic_clean(text)
    text = slang_normalize(text)
    text = remove_stopwords(text)
    text = stem_text(text)
    return text

print("Pipeline NLP siap digunakan!")"""
nb.cells.append(nbf.v4.new_code_cell(kode_preprocessing))

# ============================================================
# CODE CELL: ASPECT EXTRACTION LEXICON
# ============================================================
kode_aspek = """# Kamus Aspek Wisata (Aspect-Based Sentiment Analysis - ABSA)
ASPECT_KEYWORDS = {
    'pemandangan': [
        'pemandangan', 'view', 'indah', 'cantik', 'bagus', 'foto', 'spot',
        'landscape', 'panorama', 'asri', 'hijau', 'alam', 'sejuk', 'udara',
        'sunrise', 'sunset', 'danau', 'air', 'curug', 'gunung', 'bukit', 'sawah'
    ],
    'harga': [
        'tiket', 'harga', 'mahal', 'murah', 'biaya', 'bayar', 'gratis',
        'htm', 'masuk', 'tarif', 'terjangkau', 'ekonomis', 'kantong',
        'sebanding', 'worth', 'free', 'charge', 'cost'
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
        'happy', 'kids', 'family', 'rekreasi'
    ]
}

def extract_aspects(text_original: str, text_processed: str) -> dict:
    \"\"\"Mendeteksi aspek wisata menggunakan lexicon matching (dual-text matching).\"\"\"
    combined = (str(text_original) + ' ' + str(text_processed)).lower()
    result = {}
    for aspect, keywords in ASPECT_KEYWORDS.items():
        result[f'aspek_{aspect}'] = any(kw in combined for kw in keywords)
    return result

def count_aspects(row):
    return sum([row[f'aspek_{a}'] for a in ASPECT_KEYWORDS.keys()])

print("Kamus Aspek berhasil didefinisikan!")
print(f"Total Aspek: {len(ASPECT_KEYWORDS)} aspek")
for aspek, keywords in ASPECT_KEYWORDS.items():
    print(f"  - {aspek.title()}: {len(keywords)} kata kunci")"""
nb.cells.append(nbf.v4.new_code_cell(kode_aspek))

# ============================================================
# CODE CELL: EKSEKUSI + OUTPUT LAPORAN
# ============================================================
kode_eksekusi = """# Eksekusi Pipeline ke Seluruh Data
print("Memuat dataset bersih...")
df = pd.read_csv('Dataset/MASTER_REVIEWS_CLEANED.csv')
print(f"Total data: {len(df)} baris")

# Langkah 1: NLP Preprocessing
print("\\nLangkah 1: NLP Preprocessing (Slang + Stopword + Stemming)...")
start = time.time()
df['review_nlp'] = df['review_text_clean'].apply(preprocess_full)
elapsed = time.time() - start
print(f"Selesai dalam {elapsed:.0f} detik!")

# Langkah 2: Aspect Extraction
print("\\nLangkah 2: Aspect Extraction...")
aspect_results = df.apply(
    lambda row: extract_aspects(row['review_text'], row['review_nlp']), axis=1)
df_aspects = pd.DataFrame(list(aspect_results))
df = pd.concat([df, df_aspects], axis=1)
df['jumlah_aspek_terdeteksi'] = df.apply(count_aspects, axis=1)

# Simpan hasil
df.to_csv('Dataset/MASTER_REVIEWS_NLP.csv', index=False, encoding='utf-8')

# === LAPORAN HASIL ===
print("\\n" + "="*55)
print("LAPORAN HASIL PREPROCESSING & ASPECT EXTRACTION")
print("="*55)
print(f"Total data terproses: {len(df)}")
print(f"Kolom baru: review_nlp, 5 aspek, jumlah_aspek_terdeteksi")

print("\\n[Distribusi Aspek Terdeteksi]")
for aspek in ASPECT_KEYWORDS.keys():
    col = f'aspek_{aspek}'
    jml = df[col].sum()
    pct = jml / len(df) * 100
    print(f"  - {aspek.title()}: {int(jml)} ulasan ({pct:.1f}%)")

print("\\n[Contoh Hasil Preprocessing - 3 Sampel]")
sample_cols = ['review_text', 'review_nlp', 'aspek_pemandangan', 'aspek_harga', 'aspek_keluarga']
display(df[sample_cols].sample(3, random_state=42))"""
nb.cells.append(nbf.v4.new_code_cell(kode_eksekusi))

# Save notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print("FASE 4 berhasil didokumentasikan ke wisata_traning.ipynb!")
