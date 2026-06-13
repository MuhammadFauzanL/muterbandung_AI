# IMPORTANT: Keep torch and SentenceTransformer at the top to reduce Windows DLL collision risk.
import torch
from sentence_transformers import SentenceTransformer, util
import os
import re
import ast
import math
import datetime
import pandas as pd
import numpy as np

# Category mapping for frontend/checkbox values to actual database columns/labels
CATEGORY_MAPPING = {
    "alam": ["alam", "wisata alam", "rekreasi alam", "tempat camping"],
    "keluarga": ["keluarga", "rekreasi keluarga", "ramah anak"],
    "budaya": ["budaya", "tempat budaya", "desa wisata", "tempat seni"],
    "sejarah": ["sejarah", "tempat sejarah"],
    "edukasi": ["edukasi", "tempat belajar"],
    "kuliner": ["kuliner", "tempat kuliner"],
    "belanja": ["belanja", "tempat belanja"],
    "satwa": ["satwa", "wisata satwa", "kebun binatang", "taman burung", "interaksi hewan"],
    "santai/healing": ["santai/healing", "healing", "santai"],
    "spot foto": ["spot foto", "instagramable", "pemandangan"],
    "petualangan": ["petualangan", "wisata petualangan", "wahana ekstrem", "outbound", "rafting"],
    "wahana ekstrem": ["wahana ekstrem", "petualangan", "outbound"],
    "religi": ["religi", "tempat ibadah", "masjid", "gereja"],
    "ramah anak": ["ramah anak", "anak", "keluarga", "playground", "area bermain"],
    "indoor": ["indoor", "dalam ruangan", "museum", "mall", "galeri"],
    "outdoor": ["outdoor", "luar ruangan", "alam terbuka", "taman", "camping"],
    "malam": ["malam", "night", "city light", "lampu kota", "buka malam"],
    "gratis": ["gratis", "free", "tanpa bayar", "tiket gratis"]
}

INTENT_ABSOLUTE_THRESHOLD = 0.45
INTENT_RELATIVE_MARGIN = 0.22
DEFAULT_CHEAP_MAX_PRICE = 50000
DISTANCE_SCORE_SCALE_KM = 10.0
EMBEDDING_MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
SENTIMENT_MODEL_SOURCE = "tfidf_linearsvc"
SENTIMENT_MODEL_VERSION = "run_nlp_pipeline_v2"
SENTIMENT_UNAVAILABLE_SOURCE = "unavailable"
SENTIMENT_SHRINKAGE_K = 50.0
REVIEW_CONFIDENCE_LOW_MAX = 0.50
REVIEW_CONFIDENCE_HIGH_MIN = 0.75
REVIEWED_DB_PATH = os.path.join(
    "Wisata_Workspace",
    "01_Dataset",
    "3_Curated",
    "DATABASE_WISATA_LABELED_V2_REVIEWED.csv",
)
RUNTIME_CANDIDATE_DB_PATH = os.path.join(
    "Wisata_Workspace",
    "01_Dataset",
    "3_Curated",
    "DATABASE_WISATA_LABELED_V2_REVIEWED_MEDIA_SENTIMENT_RUNTIME_CANDIDATE_2026-06-09.csv",
)
LANDMARK_ALIAS_PATH = os.path.join(
    "Wisata_Workspace",
    "01_Dataset",
    "3_Curated",
    "landmark_aliases.csv",
)
ACTIVE_DISPLAY_STATUS = {"active_candidate"}
EXCLUDED_CURATION_ACTIONS = {"remove"}
VALID_SORT_MODES = {"relevance", "balanced", "nearest"}
NEARBY_QUERY_KEYWORDS = [
    "terdekat", "dekat saya", "sekitar saya", "di sekitar saya",
    "paling dekat", "dekat", "sekitar", "near me", "nearby"
]
WATERFALL_QUERY_KEYWORDS = ["curug", "air terjun", "waterfall"]
SHOPPING_QUERY_KEYWORDS = [
    "belanja", "shopping", "mall", "mal", "citywalk", "plaza",
    "factory outlet", "outlet", "oleh-oleh", "oleh oleh", "souvenir",
    "buah tangan", "pasar"
]
LOW_CROWD_QUERY_KEYWORDS = [
    "tidak ramai", "tidak terlalu ramai", "nggak ramai", "gak ramai",
    "ga ramai", "sepi", "anti ramai", "jauh dari keramaian", "tenang"
]
MALL_NON_SHOPPING_PENALTY = 0.88
MALL_NEARBY_GENERIC_PENALTY = 0.93
DISPLAY_LABEL_ALIASES = {
    "Wahana Ekstrem": "Petualangan"
}

LEXICAL_INTENT_KEYWORDS = {
    "Alam": [
        "alam", "outdoor", "sejuk", "adem", "ngadem", "gunung", "hutan",
        "danau", "situ", "curug", "air terjun", "kebun teh", "pemandangan"
    ],
    "Keluarga": [
        "keluarga", "anak", "anak-anak", "balita", "bocah", "family",
        "ramah anak", "bawa anak"
    ],
    "Budaya": [
        "budaya", "seni", "adat", "tradisional", "angklung", "kesenian",
        "desa adat", "kampung adat"
    ],
    "Sejarah": [
        "sejarah", "historis", "heritage", "gedung tua", "monumen",
        "museum sejarah", "situs"
    ],
    "Edukasi": [
        "edukasi", "edukatif", "belajar", "museum", "sains", "science",
        "interaktif", "pengetahuan"
    ],
    "Kuliner": [
        "makan", "makannya", "makanan", "kuliner", "restoran", "warung",
        "cafe", "kafe", "nyemil", "jajan", "food", "eatery", "ngopi",
        "nongkrong"
    ],
    "Belanja": [
        "belanja", "mall", "mal", "shopping", "shopping center",
        "factory outlet", "outlet", "oleh-oleh", "buah tangan"
    ],
    "Satwa": [
        "satwa", "hewan", "binatang", "zoo", "kebun binatang",
        "taman burung", "burung", "rusa", "kelinci", "petting zoo",
        "interaksi hewan", "feeding"
    ],
    "Santai/Healing": [
        "healing", "santai", "tenang", "rileks", "refreshing", "ngobrol",
        "nongkrong"
    ],
    "Spot Foto": [
        "spot foto", "foto", "instagramable", "view", "pemandangan",
        "sunrise", "sunset"
    ],
    "Petualangan": [
        "petualangan", "adventure", "ekstrem", "outbound", "rafting",
        "camping", "glamping"
    ],
    "Religi": [
        "religi", "ibadah", "masjid", "gereja", "ziarah", "spiritual",
        "tempat ibadah"
    ],
    "Ramah Anak": [
        "ramah anak", "anak kecil", "balita", "playground", "area bermain",
        "tempat anak", "bawa anak"
    ],
    "Indoor": [
        "indoor", "dalam ruangan", "tidak panas", "tidak hujan",
        "museum indoor", "mall indoor", "galeri indoor"
    ],
    "Outdoor": [
        "outdoor", "luar ruangan", "alam terbuka", "taman terbuka",
        "camping", "hutan", "kebun"
    ],
    "Malam": [
        "malam", "wisata malam", "buka malam", "night view", "city light",
        "lampu kota", "nongkrong malam", "kuliner malam", "cafe malam",
        "kafe malam", "resto malam", "makan malam", "jam malam"
    ],
    "Gratis": [
        "gratis", "free", "tanpa bayar", "tiket gratis", "masuk gratis",
        "gratis masuk"
    ]
}

UNSUPPORTED_QUERY_PATTERNS = [
    {
        "label": "curug malam",
        "pattern": r"(?=.*\b(curug|air terjun)\b)(?=.*\b(malam|night)\b)",
        "reason": "Sistem belum punya bukti kuat curug di Bandung Raya yang aman dan memang direkomendasikan untuk kunjungan malam."
    },
    {
        "label": "glamping gratis",
        "pattern": r"(?=.*\b(glamping|resort glamping)\b)(?=.*\b(gratis|free|tanpa bayar|tidak bayar)\b)",
        "reason": "Glamping umumnya berbayar, dan dataset tidak memiliki glamping gratis yang terverifikasi."
    },
    {
        "label": "wisata salju atau ski",
        "pattern": r"\b(ski|salju|snow)\b",
        "reason": "Bandung Raya tidak memiliki destinasi ski atau wisata salju alami di dataset ini."
    },
    {
        "label": "pantai",
        "pattern": r"\bpantai\b",
        "reason": "Bandung Raya bukan wilayah pantai, sehingga sistem tidak memaksakan hasil pantai."
    },
    {
        "label": "gurun pasir",
        "pattern": r"\b(gurun|desert)\b",
        "reason": "Dataset MuterBandung tidak memiliki destinasi gurun pasir yang valid."
    },
    {
        "label": "aurora",
        "pattern": r"\baurora\b",
        "reason": "Aurora bukan atraksi realistis untuk Bandung Raya, sehingga tidak ada rekomendasi kuat."
    }
]

# Slang dictionary for normalization
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
    "dmn": "dimana", "dr mana": "dari mana",
    "aja": "saja", "aj": "saja",
    "ke sini": "kesini", "ke sana": "kesana",
    "cpt": "cepat", "cepet": "cepat",
    "ancur": "hancur", "bnyk": "banyak",
    "pgn": "ingin", "pengen": "ingin", "pengin": "ingin",
    "msh": "masih", "nih": "ini", "itu sih": "itu",
    "keren": "keren", "mantep": "mantap", "mantap": "mantap",
    "asik": "asyik", "seru": "menyenangkan",
    "jelek": "buruk", "rusak bgt": "sangat rusak",
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
    
    # Penambahan slang dan typo untuk konteks Kuliner / Makanan
    "maka n": "makan", "makannya": "makan", "makan makannya": "makan kuliner",
    "maka n makannya": "makan kuliner", "makanan": "makan kuliner",
    "makan": "makan kuliner", "jajan": "jajan kuliner", "jajanan": "jajanan kuliner",
    "nyemil": "camilan kuliner", "ngopi": "kopi cafe kuliner",
    "healing": "tenang alam", "refreshing": "segar alam",

    "masuk gratis": "gratis", "gratis masuk": "gratis",
    "tiket mahal": "harga tiket mahal", "parkir susah": "parkir sulit",
    "parkiran penuh": "parkir penuh", "macet": "macet",
    "toilet kotor": "fasilitas toilet kotor",
    "mushola ada": "tersedia mushola",
    "ramah anak": "cocok untuk anak",
    "anak anak": "anak-anak", "bawa anak": "membawa anak",
}

class MuterBandungRecommender:
    """Core Recommender Engine untuk MuterBandung v1.0."""

    def __init__(self, db_path='DATABASE_WISATA_FINAL_PARIPURNA.csv'):
        """Load database, parse multi_labels, handle null avg_rating, initialize SentenceTransformer, and build dense vector corpus."""
        # Handle path resolution if running from different directories
        if db_path == 'DATABASE_WISATA_FINAL_PARIPURNA.csv':
            env_db_path = os.getenv("MUTERBANDUNG_DATASET_PATH") or os.getenv("MUTERBANDUNG_DB_PATH")
            if env_db_path:
                db_path = env_db_path

        if db_path == 'DATABASE_WISATA_FINAL_PARIPURNA.csv':
            reviewed_candidates = [
                RUNTIME_CANDIDATE_DB_PATH,
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), RUNTIME_CANDIDATE_DB_PATH),
                REVIEWED_DB_PATH,
                os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), REVIEWED_DB_PATH)
            ]
            for candidate in reviewed_candidates:
                if os.path.exists(candidate):
                    db_path = candidate
                    break

        resolved_path = db_path
        if not os.path.exists(resolved_path):
            # Check relative to file's directory
            file_dir = os.path.dirname(os.path.abspath(__file__))
            alt_path1 = os.path.join(file_dir, db_path)
            alt_path2 = os.path.join(os.path.dirname(file_dir), db_path)
            
            if os.path.exists(alt_path1):
                resolved_path = alt_path1
            elif os.path.exists(alt_path2):
                resolved_path = alt_path2
                
        if not os.path.exists(resolved_path):
            raise FileNotFoundError(f"Database file tidak ditemukan di {db_path} maupun lokasi alternatif.")
            
        # Load dataset
        self.df = pd.read_csv(resolved_path)
        self.source_db_path = resolved_path
        
        # Parse multi_labels safely
        self.df['multi_labels_parsed'] = self.df['multi_labels'].apply(self._parse_multi_labels)
        self._prepare_label_v2_columns()
        self._prepare_sentiment_metadata_columns()
        self.total_rows_before_status_filter = len(self.df)
        self.df = self._filter_active_candidates(self.df).copy().reset_index(drop=True)
        self._prepare_adjusted_sentiment_columns()
        
        # Fill missing avg_rating using the dataset median
        self.num_filled_ratings = self.df['avg_rating'].isnull().sum()
        self.median_rating = self.df['avg_rating'].median()
        if pd.isna(self.median_rating):
            self.median_rating = 4.0 # safe fallback
        self.df['avg_rating'] = self.df['avg_rating'].fillna(self.median_rating)
        
        # Setup Slang Dict
        self.slang_dict = SLANG_DICT
        self.landmarks = self._load_landmarks()
        
        # Initialize SentenceTransformer
        self.model_name_or_path = self._resolve_embedding_model_path()
        print(f"[INFO] Loading SentenceTransformer model: {self.model_name_or_path}")
        self.model = SentenceTransformer(self.model_name_or_path)
        
        # Precompute Intent Embeddings for Zero-Shot Classification (Refined Phrase-based)
        self.intent_phrases = {
            "Alam": ["wisata alam terbuka", "pegunungan", "hutan", "rekreasi alam sejuk", "danau", "air terjun", "camping", "ngadem"],
            "Keluarga": ["rekreasi keluarga", "ramah anak", "bermain anak-anak", "wahana keluarga", "bawa bocah", "tempat liburan keluarga"],
            "Budaya": ["tempat seni dan budaya", "pertunjukan tradisional", "desa adat", "kerajinan tangan", "kesenian bandung"],
            "Sejarah": ["situs bersejarah", "gedung tua", "museum sejarah", "monumen bersejarah", "warisan purbakala"],
            "Edukasi": ["tempat belajar anak", "edukasi sains interaktif", "museum edukatif", "kebun binatang edukasi", "outbound edukatif"],
            "Kuliner": ["tempat kuliner", "makanan khas", "jajanan kuliner", "cafe tempat nongkrong", "warung kopi", "makan malam"],
            "Belanja": ["tempat belanja", "mall", "pasar tradisional", "pusat perbelanjaan", "fashion outlet", "factory outlet", "toko oleh-oleh", "belanja buah tangan"],
            "Satwa": ["wisata satwa", "kebun binatang", "taman burung", "interaksi hewan", "memberi makan rusa", "edukasi hewan", "petting zoo"],
            "Santai/Healing": ["tempat healing", "tempat santai", "suasana tenang", "tempat rileks", "ngobrol santai", "refreshing sejuk"],
            "Spot Foto": ["spot foto", "tempat instagramable", "pemandangan bagus", "view bagus", "foto sunrise", "foto sunset"],
            "Petualangan": ["wisata petualangan", "wahana ekstrem", "outbound", "rafting", "camping", "glamping"],
            "Religi": ["wisata religi", "tempat ibadah", "masjid", "gereja", "ziarah", "tempat spiritual"],
            "Ramah Anak": ["ramah anak", "tempat anak", "playground", "area bermain anak", "bawa balita"],
            "Indoor": ["indoor", "dalam ruangan", "museum indoor", "mall indoor", "galeri indoor"],
            "Outdoor": ["outdoor", "luar ruangan", "alam terbuka", "taman terbuka", "camping outdoor"],
            "Malam": ["wisata malam", "buka malam", "city light", "lampu kota", "nongkrong malam", "kuliner malam", "cafe malam", "jam 8 malam"],
            "Gratis": ["wisata gratis", "masuk gratis", "tiket gratis", "tanpa bayar", "free entry"]
        }
        self.intent_names = list(self.intent_phrases.keys())
        print("[INFO] Encoding intent labels...")
        self.intent_embeddings = {}
        for category, phrases in self.intent_phrases.items():
            self.intent_embeddings[category] = self.model.encode(phrases, convert_to_tensor=True)
        
        # Build Corpus for similarity matching (narrative paragraphs)
        self.corpus = self._build_corpus()
        
        # Encode corpus embeddings
        print("[INFO] Encoding corpus embeddings...")
        self.corpus_embeddings = self.model.encode(self.corpus, convert_to_tensor=True)
        
        print(f"[INFO] MuterBandung Recommender loaded: {len(self.df)} destinasi aktif dari {self.total_rows_before_status_filter} baris.")
        print(f"[INFO] Database source: {self.source_db_path}")
        print(f"[INFO] Landmark aliases loaded: {len(self.landmarks)}")
        if self.num_filled_ratings > 0:
            print(f"[INFO] Mengisi {self.num_filled_ratings} nilai avg_rating kosong dengan median: {self.median_rating:.2f}")

    def _load_landmarks(self):
        """Load small landmark alias table for location-aware queries like 'dekat Stasiun Bandung'."""
        candidates = [
            LANDMARK_ALIAS_PATH,
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), LANDMARK_ALIAS_PATH)
        ]
        path = next((candidate for candidate in candidates if os.path.exists(candidate)), None)
        if not path:
            return []

        df = pd.read_csv(path).fillna("")
        landmarks = []
        for _, row in df.iterrows():
            lat = self._coerce_float(row.get("latitude"))
            lon = self._coerce_float(row.get("longitude"))
            if not self._has_valid_coordinates(lat, lon):
                continue
            aliases = [str(row.get("landmark_name", "")).strip()]
            aliases.extend([item.strip() for item in str(row.get("aliases", "")).split(";") if item.strip()])
            landmarks.append({
                "name": str(row.get("landmark_name", "")).strip(),
                "aliases": list(dict.fromkeys(alias.lower() for alias in aliases if alias)),
                "latitude": lat,
                "longitude": lon,
                "type": str(row.get("landmark_type", "")).strip()
            })
        return landmarks

    def _resolve_embedding_model_path(self):
        """Prefer a baked/local model snapshot to avoid runtime downloads in hosting."""
        env_path = os.getenv('MUTERBANDUNG_MODEL_PATH')
        if env_path and os.path.exists(env_path):
            return env_path

        cache_dir_name = f"models--{EMBEDDING_MODEL_NAME.replace('/', '--')}"
        cache_roots = []
        hub_cache = os.getenv('HUGGINGFACE_HUB_CACHE')
        if hub_cache:
            cache_roots.append(hub_cache)
        hf_home = os.getenv('HF_HOME')
        if hf_home:
            cache_roots.append(os.path.join(hf_home, 'hub'))
        cache_roots.append(os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub'))

        for root in cache_roots:
            model_cache = os.path.join(root, cache_dir_name)
            snapshots_dir = os.path.join(model_cache, 'snapshots')
            if not os.path.isdir(snapshots_dir):
                continue
            snapshots = []
            for name in os.listdir(snapshots_dir):
                snapshot_path = os.path.join(snapshots_dir, name)
                modules_path = os.path.join(snapshot_path, 'modules.json')
                config_path = os.path.join(snapshot_path, 'config_sentence_transformers.json')
                if os.path.isdir(snapshot_path) and os.path.exists(modules_path) and os.path.exists(config_path):
                    snapshots.append(snapshot_path)
            if snapshots:
                snapshots.sort(key=lambda path: os.path.getmtime(path), reverse=True)
                return snapshots[0]

        offline_requested = os.getenv('HF_HUB_OFFLINE') or os.getenv('TRANSFORMERS_OFFLINE')
        if offline_requested:
            raise FileNotFoundError(
                "Model embedding lokal tidak ditemukan. Set MUTERBANDUNG_MODEL_PATH ke folder snapshot "
                f"{EMBEDDING_MODEL_NAME}, atau bake model ke cache deployment."
            )
        return EMBEDDING_MODEL_NAME

    def _parse_multi_labels(self, label_str):
        """Parse list-like string '["Alam", "Kuliner"]' to python list safely."""
        if not isinstance(label_str, str):
            return []
        label_str = label_str.strip()
        if not label_str:
            return []
        try:
            val = ast.literal_eval(label_str)
            if isinstance(val, list):
                return val
        except Exception:
            # Fallback if parsing fails (try regex or split) ONLY if it looks like a list representation
            if label_str.startswith('[') and label_str.endswith(']'):
                cleaned = re.sub(r"[\[\]\'\"]", "", label_str)
                if cleaned:
                    return [x.strip() for x in cleaned.split(',') if x.strip()]
        return []

    def _parse_semicolon_labels(self, value):
        """Parse semicolon-separated label columns from the reviewed taxonomy dataset."""
        if not isinstance(value, str):
            return []
        value = value.strip()
        if not value or value.lower() == "nan":
            return []
        return [item.strip() for item in value.split(';') if item.strip()]

    def _prepare_label_v2_columns(self):
        """Prepare final reviewed taxonomy columns, with safe fallback to legacy multi_labels."""
        if 'final_primary_intent' not in self.df.columns:
            self.df['final_primary_intent'] = self.df.get('primary_intent', '')
        if 'final_core_labels' not in self.df.columns:
            self.df['final_core_labels'] = self.df['multi_labels_parsed'].apply(lambda labels: ';'.join(labels[:3]))
        if 'final_secondary_labels' not in self.df.columns:
            self.df['final_secondary_labels'] = ''
        if 'final_avoid_labels' not in self.df.columns:
            self.df['final_avoid_labels'] = ''
        if 'display_status' not in self.df.columns:
            self.df['display_status'] = 'active_candidate'
        if 'curation_action' not in self.df.columns:
            self.df['curation_action'] = 'keep'
        if 'is_active_verified' not in self.df.columns:
            self.df['is_active_verified'] = True
        if 'night_verified' not in self.df.columns:
            self.df['night_verified'] = False
        if 'price_verified' not in self.df.columns:
            self.df['price_verified'] = True
        if 'indoor_verified' not in self.df.columns:
            self.df['indoor_verified'] = False
        if 'child_friendly_verified' not in self.df.columns:
            self.df['child_friendly_verified'] = False
        if 'coordinate_verified' not in self.df.columns:
            self.df['coordinate_verified'] = True
        if 'parking_verified' not in self.df.columns:
            self.df['parking_verified'] = False
        if 'wheelchair_accessible_verified' not in self.df.columns:
            self.df['wheelchair_accessible_verified'] = False
        if 'toilet_verified' not in self.df.columns:
            self.df['toilet_verified'] = False
        if 'mushola_verified' not in self.df.columns:
            self.df['mushola_verified'] = False
        if 'pet_friendly_verified' not in self.df.columns:
            self.df['pet_friendly_verified'] = False
        if 'safety_verified' not in self.df.columns:
            self.df['safety_verified'] = False
        if 'open_24h_verified' not in self.df.columns:
            self.df['open_24h_verified'] = False
        if 'crowd_level' not in self.df.columns:
            self.df['crowd_level'] = 'unknown'
        if 'shopping_subtype' not in self.df.columns:
            self.df['shopping_subtype'] = ''

        self.df['core_labels_parsed'] = self.df['final_core_labels'].apply(self._parse_semicolon_labels)
        self.df['secondary_labels_parsed'] = self.df['final_secondary_labels'].apply(self._parse_semicolon_labels)
        self.df['avoid_labels_parsed'] = self.df['final_avoid_labels'].apply(self._parse_semicolon_labels)
        self.df['primary_intent_final'] = self.df['final_primary_intent'].fillna('').astype(str).str.strip()

        # Backward-compatible display labels: core first, then secondary, then old labels.
        def merged_labels(row):
            labels = []
            for source in (
                row.get('core_labels_parsed', []),
                row.get('secondary_labels_parsed', []),
                row.get('multi_labels_parsed', [])
            ):
                for label in source:
                    label = DISPLAY_LABEL_ALIASES.get(label, label)
                    if label and label not in labels:
                        labels.append(label)
            return labels

        self.df['display_labels_parsed'] = self.df.apply(merged_labels, axis=1)

    def _prepare_sentiment_metadata_columns(self):
        """Attach honest raw sentiment provenance before ranking adjustment."""
        score_source = pd.to_numeric(
            self.df.get('avg_sentimen_skor', pd.Series(0.0, index=self.df.index)),
            errors='coerce'
        ).fillna(0.0)
        review_count = pd.to_numeric(
            self.df.get('total_ulasan', pd.Series(0, index=self.df.index)),
            errors='coerce'
        ).fillna(0)
        label_source = (
            self.df.get('sentimen_label_lokasi', pd.Series('', index=self.df.index))
            .fillna('')
            .astype(str)
            .str.strip()
        )
        available = (review_count > 0) & (label_source != '')

        if 'sentiment_score' not in self.df.columns:
            self.df['sentiment_score'] = score_source
        else:
            self.df['sentiment_score'] = pd.to_numeric(
                self.df['sentiment_score'],
                errors='coerce'
            ).fillna(score_source)

        self.df['sentiment_available'] = available

        source = (
            self.df.get('sentiment_model_source', pd.Series('', index=self.df.index))
            .fillna('')
            .astype(str)
            .str.strip()
        )
        version = (
            self.df.get('sentiment_model_version', pd.Series('', index=self.df.index))
            .fillna('')
            .astype(str)
            .str.strip()
        )
        self.df['sentiment_model_source'] = source.where(
            source != '',
            np.where(available, SENTIMENT_MODEL_SOURCE, SENTIMENT_UNAVAILABLE_SOURCE)
        )
        self.df['sentiment_model_version'] = version.where(
            version != '',
            np.where(available, SENTIMENT_MODEL_VERSION, '')
        )

    def _prepare_adjusted_sentiment_columns(self):
        """Build Bayesian-adjusted sentiment and p95-capped review confidence."""
        raw_scores = pd.to_numeric(
            self.df.get('sentiment_score', pd.Series(0.0, index=self.df.index)),
            errors='coerce'
        ).fillna(0.0).clip(-1.0, 1.0)
        review_counts = pd.to_numeric(
            self.df.get('total_ulasan', pd.Series(0, index=self.df.index)),
            errors='coerce'
        ).fillna(0.0).clip(lower=0.0)
        available = self.df.get(
            'sentiment_available',
            pd.Series(False, index=self.df.index)
        ).fillna(False).astype(bool)

        available_scores = raw_scores[available & (review_counts > 0)]
        if len(available_scores) > 0:
            global_average = float(available_scores.mean())
        else:
            global_average = float(raw_scores.mean()) if len(raw_scores) else 0.0
        if not math.isfinite(global_average):
            global_average = 0.0

        positive_counts = review_counts[review_counts > 0]
        p95_review_count = float(positive_counts.quantile(0.95)) if len(positive_counts) else 1.0
        if not math.isfinite(p95_review_count) or p95_review_count <= 0:
            p95_review_count = 1.0

        self.sentiment_global_average = global_average
        self.sentiment_review_count_p95 = p95_review_count
        self.sentiment_shrinkage_k = SENTIMENT_SHRINKAGE_K

        adjusted_scores = (
            (review_counts * raw_scores) + (self.sentiment_shrinkage_k * self.sentiment_global_average)
        ) / (review_counts + self.sentiment_shrinkage_k)

        review_confidence = review_counts.apply(self._review_confidence)

        self.df['sentiment_score'] = raw_scores
        self.df['adjusted_sentiment_score'] = adjusted_scores.clip(-1.0, 1.0)
        self.df['review_confidence'] = review_confidence
        self.df['review_confidence_label'] = review_confidence.apply(self._review_confidence_label)

    def _filter_active_candidates(self, df):
        """Remove reviewed records that should not be recommended by default."""
        status = df.get('display_status', pd.Series('active_candidate', index=df.index)).fillna('').astype(str).str.lower()
        action = df.get('curation_action', pd.Series('keep', index=df.index)).fillna('').astype(str).str.lower()
        active_mask = status.isin(ACTIVE_DISPLAY_STATUS) & ~action.isin(EXCLUDED_CURATION_ACTIONS)
        return df[active_mask]

    def _preprocess_text(self, text):
        """Clean and normalize text (lowercase, basic clean, slang normalization)."""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        
        # Basic clean
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Slang normalization
        for slang, baku in self.slang_dict.items():
            text = re.sub(r'\b' + re.escape(slang) + r'\b', baku, text)
            
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _query_has_keyword(self, query, keywords):
        """Case-insensitive phrase/keyword match on raw and normalized query text."""
        if not isinstance(query, str) or not query.strip():
            return False
        raw_query = query.lower()
        normalized_query = self._preprocess_text(query)
        haystacks = (raw_query, normalized_query)
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if any(re.search(pattern, text) for text in haystacks):
                return True
        return False

    def _detect_unsupported_query(self, query):
        """Detect impossible/out-of-scope tourism requests to avoid hallucinated recommendations."""
        if not isinstance(query, str) or not query.strip():
            return None
        raw_query = query.lower()
        normalized_query = self._preprocess_text(query)
        for item in UNSUPPORTED_QUERY_PATTERNS:
            pattern = item["pattern"]
            if re.search(pattern, raw_query) or re.search(pattern, normalized_query):
                return {
                    "label": item["label"],
                    "reason": item["reason"]
                }
        return None

    def _apply_lexical_intent_injection(self, query, detected_intents):
        """Force active intents when explicit user keywords are present in the query."""
        lexical_intents = []
        for intent, keywords in LEXICAL_INTENT_KEYWORDS.items():
            if intent in self.intent_embeddings and self._query_has_keyword(query, keywords):
                if intent not in detected_intents:
                    detected_intents.append(intent)
                lexical_intents.append(intent)
        return lexical_intents

    def _query_requests_free(self, query):
        """Infer a free-only filter from explicit natural-language budget terms."""
        return self._query_has_keyword(query, [
            "gratis", "free", "tanpa bayar", "tidak bayar", "tiket gratis",
            "masuk gratis", "gratis masuk"
        ])

    def _extract_price_limit(self, query):
        """Extract a simple max-price constraint from Indonesian natural language."""
        if not isinstance(query, str) or not query.strip():
            return None
        raw_query = query.lower().replace(".", "").replace(",", "")
        price_patterns = [
            r"(?:di bawah|dibawah|maksimal|maks|max|under|budget)\s*(?:rp|idr)?\s*(\d{4,8})",
            r"(?:di bawah|dibawah|maksimal|maks|max|under|budget)\s*(\d{1,3})\s*ribu",
            r"\b(\d{1,3})\s*ribu\b"
        ]
        for pattern in price_patterns:
            match = re.search(pattern, raw_query)
            if match:
                value = int(match.group(1))
                if value < 1000:
                    value *= 1000
                return value
        if self._query_has_keyword(query, ["murah", "hemat", "budget", "low budget"]):
            return DEFAULT_CHEAP_MAX_PRICE
        return None

    def _extract_open_time(self, query):
        """Infer opening-hour filter from phrases like 'jam 8 malam' or 'wisata malam'."""
        if not isinstance(query, str) or not query.strip():
            return None
        raw_query = query.lower()
        match = re.search(r"\b(?:jam|pukul)\s*(\d{1,2})(?::(\d{2}))?\s*(pagi|siang|sore|malam)?\b", raw_query)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2) or 0)
            meridiem = match.group(3)
            if meridiem == "malam" and hour < 12:
                hour += 12
            elif meridiem == "sore" and hour < 12:
                hour += 12
            elif meridiem == "siang" and hour < 11:
                hour += 12
            hour = max(0, min(hour, 23))
            minute = max(0, min(minute, 59))
            return f"{hour:02d}:{minute:02d}"
        if self._query_has_keyword(query, ["malam"]):
            return "20:00"
        return None

    def _coerce_float(self, value):
        """Parse numeric API values safely."""
        try:
            if value is None or value == "":
                return None
            parsed = float(value)
            if math.isnan(parsed) or math.isinf(parsed):
                return None
            return parsed
        except (TypeError, ValueError):
            return None

    def _coerce_positive_float(self, value):
        parsed = self._coerce_float(value)
        if parsed is None or parsed <= 0:
            return None
        return parsed

    def _has_valid_coordinates(self, latitude, longitude):
        if latitude is None or longitude is None:
            return False
        return -90 <= latitude <= 90 and -180 <= longitude <= 180

    def _query_requests_nearby(self, query):
        """Detect explicit nearby intent in natural language."""
        return self._query_has_keyword(query, NEARBY_QUERY_KEYWORDS)

    def _detect_landmark_location(self, query):
        """Resolve nearby/area queries to known landmark coordinates."""
        if not isinstance(query, str) or not query.strip() or not self.landmarks:
            return None

        raw_query = query.lower()
        normalized_query = self._preprocess_text(query)
        proximity_terms = ["dekat", "sekitar", "terdekat", "near", "dari", "di"]
        if not any(re.search(r"\b" + re.escape(term) + r"\b", raw_query) for term in proximity_terms):
            return None

        for landmark in self.landmarks:
            for alias in landmark["aliases"]:
                pattern = r"\b" + re.escape(alias) + r"\b"
                if re.search(pattern, raw_query) or re.search(pattern, normalized_query):
                    return landmark
        return None

    def _query_requests_night(self, query):
        """Detect queries where the night experience itself matters."""
        return self._query_has_keyword(query, [
            "malam", "night", "city light", "lampu kota", "night view",
            "wisata malam", "nongkrong malam"
        ])

    def _query_requests_waterfall(self, query):
        """Detect explicit curug/air-terjun intent."""
        return self._query_has_keyword(query, WATERFALL_QUERY_KEYWORDS)

    def _query_requests_shopping(self, query):
        """Detect explicit shopping/mall/oleh-oleh intent."""
        return self._query_has_keyword(query, SHOPPING_QUERY_KEYWORDS)

    def _query_requests_low_crowd(self, query):
        """Detect low-crowd preference without forcing a hard filter."""
        return self._query_has_keyword(query, LOW_CROWD_QUERY_KEYWORDS)

    def _row_blob(self, row):
        values = [
            row.get('location_name', ''),
            row.get('category', ''),
            row.get('final_primary_intent', ''),
            row.get('final_core_labels', ''),
            row.get('final_secondary_labels', ''),
            row.get('multi_labels', ''),
            row.get('tags_sintetis', ''),
            row.get('shopping_subtype', ''),
        ]
        return " ".join(str(value).lower() for value in values if pd.notna(value))

    def _matches_waterfall_destination(self, row):
        """Specific intent match for curug/air-terjun destinations."""
        blob = self._row_blob(row)
        return any(keyword in blob for keyword in WATERFALL_QUERY_KEYWORDS)

    def _is_mall_destination(self, row):
        subtype = str(row.get('shopping_subtype', '')).strip().lower()
        if subtype == "mall":
            return True
        blob = self._row_blob(row)
        return any(term in blob for term in ["mall", "citywalk", "shopping center", "plaza"])

    def _normalize_sort_mode(self, sort_by, has_user_location, nearby_requested):
        mode = str(sort_by or "balanced").strip().lower()
        if mode not in VALID_SORT_MODES:
            mode = "balanced"
        if not has_user_location:
            return "relevance"
        if nearby_requested and mode == "relevance":
            return "balanced"
        return mode

    def _haversine_km(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two lat/lon points in kilometers."""
        radius_km = 6371.0088
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _distance_score(self, distance_km):
        if distance_km is None or pd.isna(distance_km):
            return 0.0
        return 1.0 / (1.0 + max(0.0, float(distance_km)) / DISTANCE_SCORE_SCALE_KM)

    def _review_confidence(self, review_count):
        review_count = self._coerce_float(review_count) or 0.0
        review_count = max(0.0, review_count)
        p95_review_count = max(1.0, float(getattr(self, "sentiment_review_count_p95", 1.0)))
        return min(1.0, math.log1p(review_count) / math.log1p(p95_review_count))

    def _review_confidence_label(self, confidence):
        confidence = self._coerce_float(confidence)
        if confidence is None:
            confidence = 0.0
        if confidence < REVIEW_CONFIDENCE_LOW_MAX:
            return "low_review_confidence"
        if confidence < REVIEW_CONFIDENCE_HIGH_MIN:
            return "medium_review_confidence"
        return "high_review_confidence"

    def _compute_adjusted_sentiment_score(self, raw_score, review_count):
        raw_score = self._coerce_float(raw_score)
        if raw_score is None:
            raw_score = 0.0
        raw_score = max(-1.0, min(1.0, raw_score))
        review_count = self._coerce_float(review_count) or 0.0
        review_count = max(0.0, review_count)
        prior = float(getattr(self, "sentiment_global_average", 0.0))
        shrinkage_k = float(getattr(self, "sentiment_shrinkage_k", SENTIMENT_SHRINKAGE_K))
        adjusted = ((review_count * raw_score) + (shrinkage_k * prior)) / (review_count + shrinkage_k)
        return max(-1.0, min(1.0, adjusted))

    def _is_free_entry(self, row):
        """Strict free-entry check so paid resorts are not returned for free-only queries."""
        price_type = str(row.get('price_type', '')).strip().lower()
        price_min = self._coerce_float(row.get('price_min'))
        price_max = self._coerce_float(row.get('price_max'))
        avoid_labels = [str(lbl).strip().lower() for lbl in row.get('avoid_labels_parsed', [])]
        if "gratis" in avoid_labels:
            return False
        return price_type == "gratis" and price_min == 0 and price_max == 0

    def _coerce_bool_value(self, value, default=False):
        if isinstance(value, bool):
            return value
        if pd.isna(value):
            return default
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return True
        if normalized in {"false", "0", "no", "n"}:
            return False
        return default

    def _clean_scalar_text(self, value):
        if value is None or pd.isna(value):
            return ""
        return str(value).strip()

    def _clean_url_text(self, value):
        text = self._clean_scalar_text(value)
        if re.match(r"^https?://", text, flags=re.IGNORECASE):
            return text
        return ""

    def _first_url(self, row, columns):
        for column in columns:
            if column in row:
                url = self._clean_url_text(row.get(column))
                if url:
                    return url
        return ""

    def _get_media_metadata(self, row):
        """Expose curated media/link fields only when the active dataset has them."""
        image_url = self._first_url(row, ["media_image_url", "image_url", "imageUrl", "photo", "cover_photo"])
        destination_url = self._first_url(row, [
            "media_destination_url",
            "destination_url",
            "google_maps_url",
            "location_url",
            "url",
            "location_link",
        ])
        website = self._first_url(row, ["media_website", "website", "official_website"])
        available = self._coerce_bool_value(row.get("media_available"), default=bool(image_url or destination_url or website))
        return {
            "available": bool(available and (image_url or destination_url or website)),
            "image_url": image_url,
            "destination_url": destination_url,
            "website": website,
            "source": self._clean_scalar_text(row.get("media_source")) or ("curated_dataset" if available else "not_available_in_curated_dataset"),
            "match_title": self._clean_scalar_text(row.get("media_match_title")),
            "match_score": self._coerce_float(row.get("media_match_score")),
            "audit_status": self._clean_scalar_text(row.get("media_audit_status")),
        }

    def _get_sentiment_metadata(self, row):
        """Return neutral sentiment fields used by API responses and scoring."""
        score = self._coerce_float(row.get('sentiment_score'))
        if score is None:
            score = self._coerce_float(row.get('avg_sentimen_skor'))
        if score is None:
            score = 0.0

        review_count = self._coerce_float(row.get('total_ulasan')) or 0.0
        available_default = review_count > 0 and bool(self._clean_scalar_text(row.get('sentimen_label_lokasi')))
        available = self._coerce_bool_value(row.get('sentiment_available'), default=available_default)
        adjusted_score = self._coerce_float(row.get('adjusted_sentiment_score'))
        if adjusted_score is None:
            adjusted_score = self._compute_adjusted_sentiment_score(score, review_count)
        review_confidence = self._coerce_float(row.get('review_confidence'))
        if review_confidence is None:
            review_confidence = self._review_confidence(review_count)
        review_confidence = max(0.0, min(1.0, review_confidence))
        review_confidence_label = (
            self._clean_scalar_text(row.get('review_confidence_label'))
            or self._review_confidence_label(review_confidence)
        )

        source = self._clean_scalar_text(row.get('sentiment_model_source'))
        version = self._clean_scalar_text(row.get('sentiment_model_version'))
        if available:
            source = source or SENTIMENT_MODEL_SOURCE
            version = version or SENTIMENT_MODEL_VERSION
        else:
            source = source or SENTIMENT_UNAVAILABLE_SOURCE
            version = ""

        return {
            "sentiment_score": round(float(score), 4),
            "adjusted_sentiment_score": round(float(adjusted_score), 4),
            "sentiment_model_source": source,
            "sentiment_model_version": version,
            "sentiment_available": bool(available),
            "sentiment_label": self._clean_scalar_text(row.get('sentimen_label_lokasi')),
            "sentiment_review_count": int(review_count),
            "review_confidence": round(float(review_confidence), 4),
            "review_confidence_label": review_confidence_label,
            "sentiment_prior_score": round(float(getattr(self, "sentiment_global_average", 0.0)), 4),
            "sentiment_review_count_p95": round(float(getattr(self, "sentiment_review_count_p95", 1.0)), 2),
        }

    def _coordinate_is_verified(self, row):
        return self._coerce_bool_value(row.get("coordinate_verified", True), default=True)

    def _query_requested_shopping_subtype(self, query):
        if not isinstance(query, str) or not query.strip():
            return None
        if self._query_has_keyword(query, ["factory outlet", "outlet"]):
            return "Factory Outlet"
        if self._query_has_keyword(query, ["oleh-oleh", "oleh oleh", "souvenir", "buah tangan"]):
            return "Oleh-Oleh"
        if self._query_has_keyword(query, ["mall", "mal", "shopping center"]):
            return "Mall"
        if self._query_has_keyword(query, ["pasar wisata", "pasar"]):
            return "Pasar Wisata"
        return None

    def _query_facility_filters(self, query):
        if not isinstance(query, str) or not query.strip():
            return {}
        filters = {}
        if self._query_has_keyword(query, ["parkir", "parkiran", "parking"]):
            filters["parking_verified"] = True
        if self._query_has_keyword(query, ["ramah disabilitas", "disabilitas", "kursi roda", "wheelchair", "aksesibel"]):
            filters["wheelchair_accessible_verified"] = True
        if self._query_has_keyword(query, ["toilet", "wc", "kamar mandi"]):
            filters["toilet_verified"] = True
        if self._query_has_keyword(query, ["mushola", "musala", "musholla", "tempat sholat", "masjid"]):
            filters["mushola_verified"] = True
        if self._query_has_keyword(query, ["pet friendly", "hewan peliharaan", "bawa anjing", "bawa kucing"]):
            filters["pet_friendly_verified"] = True
        if re.search(r"\b24\s*jam\b", query.lower()):
            filters["open_24h_verified"] = True
            if self._query_has_keyword(query, ["aman", "keamanan"]):
                filters["safety_verified"] = True
        return filters

    def _facility_no_match_reason(self, filters):
        labels = {
            "parking_verified": "parkir terverifikasi",
            "wheelchair_accessible_verified": "akses disabilitas/kursi roda terverifikasi",
            "toilet_verified": "toilet terverifikasi",
            "mushola_verified": "mushola/tempat ibadah terverifikasi",
            "pet_friendly_verified": "pet friendly terverifikasi",
            "safety_verified": "keamanan/aman untuk keluarga terverifikasi",
            "open_24h_verified": "24 jam sekaligus aman untuk malam",
            "crowd_level": "tingkat keramaian rendah terverifikasi",
        }
        requested = [labels.get(key, key) for key in filters]
        return "Dataset belum punya kandidat kuat untuk filter fasilitas: " + ", ".join(requested) + "."

    def _matches_night_destination(self, row):
        """Strict night QA: open at night and actually offers a plausible night experience."""
        verified_value = row.get('night_verified', None)
        if pd.notna(verified_value):
            if isinstance(verified_value, bool):
                return verified_value
            if str(verified_value).strip().lower() in {"true", "1", "yes"}:
                return True
            if str(verified_value).strip().lower() in {"false", "0", "no"}:
                return False

        open_weekday = self._is_open(row.get('jam_buka_weekday'), row.get('jam_tutup_weekday'), "20:00")
        open_weekend = self._is_open(row.get('jam_buka_weekend'), row.get('jam_tutup_weekend'), "20:00")
        if not (open_weekday or open_weekend):
            return False

        core = [str(lbl).strip().lower() for lbl in row.get('core_labels_parsed', [])]
        secondary = [str(lbl).strip().lower() for lbl in row.get('secondary_labels_parsed', [])]
        has_night_label = "malam" in core or "malam" in secondary

        raw_text = " ".join([
            str(row.get('location_name', '')),
            str(row.get('category', '')),
            str(row.get('subcategory', '')),
            str(row.get('tags_sintetis', '')),
            str(row.get('deskripsi_google', '')),
        ]).lower()

        positive_terms = [
            "malam", "city light", "lampu kota", "night", "sunset",
            "matahari terbenam", "nongkrong", "cafe", "kafe", "kuliner",
            "restoran", "mall", "belanja", "alun-alun", "taman kota"
        ]
        has_positive_night_context = any(term in raw_text for term in positive_terms)

        category = str(row.get('category', '')).strip().lower()
        name = str(row.get('location_name', '')).strip().lower()
        subcategory = str(row.get('subcategory', '')).strip().lower()
        risky_nature = (
            "curug" in name
            or "air terjun" in raw_text
            or category in {"wisata alam", "rekreasi alam"}
            or "daya tarik alam" in subcategory
        )
        if risky_nature and not any(
            term in raw_text for term in ["city light", "lampu kota", "sunset", "matahari terbenam", "malam"]
        ):
            return False

        return has_night_label or has_positive_night_context

    def _attach_distance_columns(self, df, user_lat, user_lon, max_distance_km=None):
        """Attach distance metadata and optionally filter by radius."""
        enriched = df.copy()
        enriched['__distance_km'] = np.nan
        enriched['__distance_score'] = 0.0

        if not self._has_valid_coordinates(user_lat, user_lon):
            return enriched

        def calc_distance(row):
            if not self._coordinate_is_verified(row):
                return np.nan
            dest_lat = self._coerce_float(row.get('latitude'))
            dest_lon = self._coerce_float(row.get('longitude'))
            if not self._has_valid_coordinates(dest_lat, dest_lon):
                return np.nan
            return self._haversine_km(user_lat, user_lon, dest_lat, dest_lon)

        enriched['__distance_km'] = enriched.apply(calc_distance, axis=1)
        enriched['__distance_score'] = enriched['__distance_km'].apply(self._distance_score)

        radius = self._coerce_positive_float(max_distance_km)
        if radius is not None:
            enriched = enriched[
                enriched['__distance_km'].isna() | (enriched['__distance_km'] <= radius)
            ].copy()

        return enriched

    def _row_has_intent_label(self, row, intent):
        """Check whether a row has category or labels matching an intent."""
        row_cat = str(row.get('category', '')).strip().lower()
        row_primary = str(row.get('primary_intent_final', '')).strip().lower()
        row_core = [str(lbl).strip().lower() for lbl in row.get('core_labels_parsed', [])]
        row_secondary = [str(lbl).strip().lower() for lbl in row.get('secondary_labels_parsed', [])]
        row_labels = row_core + row_secondary
        intent_lower = str(intent).strip().lower()
        matching_terms = [intent_lower]
        if intent_lower in CATEGORY_MAPPING:
            matching_terms.extend(CATEGORY_MAPPING[intent_lower])
        return any(
            term == row_primary or term == row_cat or term in row_labels or term in row_cat
            for term in matching_terms
        )

    def _label_match_tier(self, row, intent):
        """Return match tier for an intent against reviewed final labels."""
        row_cat = str(row.get('category', '')).strip().lower()
        row_primary = str(row.get('primary_intent_final', '')).strip().lower()
        row_core = [str(lbl).strip().lower() for lbl in row.get('core_labels_parsed', [])]
        row_secondary = [str(lbl).strip().lower() for lbl in row.get('secondary_labels_parsed', [])]
        row_avoid = [str(lbl).strip().lower() for lbl in row.get('avoid_labels_parsed', [])]
        intent_lower = str(intent).strip().lower()
        matching_terms = [intent_lower]
        if intent_lower in CATEGORY_MAPPING:
            matching_terms.extend(CATEGORY_MAPPING[intent_lower])

        if any(term in row_avoid for term in matching_terms):
            return "avoid"
        if any(term == row_primary for term in matching_terms):
            return "primary"
        if any(term in row_core for term in matching_terms):
            return "core"
        if any(term in row_secondary for term in matching_terms):
            return "secondary"
        if any(term == row_cat or term in row_cat for term in matching_terms):
            return "category"
        return "none"

    def _build_corpus(self):
        """Build text corpus as a narrative paragraph to maximize Transformer context."""
        corpus = []
        for _, row in self.df.iterrows():
            name = str(row.get('location_name', ''))
            desc = str(row.get('deskripsi_google', '')) if pd.notna(row.get('deskripsi_google', '')) else ''
            tags = str(row.get('tags_sintetis', '')) if pd.notna(row.get('tags_sintetis', '')) else ''
            subcat = str(row.get('subcategory', '')) if pd.notna(row.get('subcategory', '')) else ''
            cat = str(row.get('category', '')) if pd.notna(row.get('category', '')) else ''
            
            primary_intent = str(row.get('primary_intent_final', '')) if pd.notna(row.get('primary_intent_final', '')) else ''
            core_labels = row.get('core_labels_parsed', [])
            secondary_labels = row.get('secondary_labels_parsed', [])
            avoid_labels = row.get('avoid_labels_parsed', [])
            labels_str = ", ".join(row.get('display_labels_parsed', []))
            
            # Narrative construction for Transformer contextual matching
            doc = (
                f"{name} adalah destinasi dengan kategori {cat} ({subcat}). "
                f"Primary intent: {primary_intent}. Core labels: {', '.join(core_labels)}. "
                f"Secondary labels: {', '.join(secondary_labels)}. Avoid labels: {', '.join(avoid_labels)}. "
                f"Fasilitas dan suasana: {tags}. Cocok untuk {labels_str}. Deskripsi: {desc}"
            )
            cleaned_doc = self._preprocess_text(doc)
            corpus.append(cleaned_doc)
        return corpus

    def _parse_time_to_minutes(self, time_str):
        """Helper to convert HH:MM string to minutes since midnight."""
        if not isinstance(time_str, str):
            return None
        time_str = time_str.strip().lower()
        if time_str in ('tutup', 'closed', 'nan', ''):
            return None
        try:
            parts = time_str.split(':')
            if len(parts) >= 2:
                return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            pass
        return None

    def _is_open(self, open_time_str, close_time_str, check_time_str):
        """Determine if a place is open at check_time_str given open/close hours."""
        open_mins = self._parse_time_to_minutes(open_time_str)
        close_mins = self._parse_time_to_minutes(close_time_str)
        check_mins = self._parse_time_to_minutes(check_time_str)
        
        if open_mins is None or close_mins is None or check_mins is None:
            return False
            
        if open_mins <= close_mins:
            # Normal case: e.g. 08:00 - 17:00
            return open_mins <= check_mins <= close_mins
        else:
            # Overnight case: e.g. 18:00 - 02:00
            return check_mins >= open_mins or check_mins <= close_mins

    def _matches_category(self, row, categories):
        """Check if row matches all filters in categories (case-insensitive, mapped)."""
        if not categories:
            return True
            
        row_cat = str(row.get('category', '')).strip().lower()
        row_primary = str(row.get('primary_intent_final', '')).strip().lower()
        row_core = [str(lbl).strip().lower() for lbl in row.get('core_labels_parsed', [])]
        row_secondary = [str(lbl).strip().lower() for lbl in row.get('secondary_labels_parsed', [])]
        row_avoid = [str(lbl).strip().lower() for lbl in row.get('avoid_labels_parsed', [])]
        attribute_filters = {"ramah anak", "indoor", "outdoor"}
        
        for req_cat in categories:
            req_cat_lower = str(req_cat).strip().lower()
            
            # Use CATEGORY_MAPPING keys for mapped checks
            matching_terms = [req_cat_lower]
            if req_cat_lower in CATEGORY_MAPPING:
                matching_terms = CATEGORY_MAPPING[req_cat_lower]

            if req_cat_lower == "belanja":
                if "belanja" in row_avoid:
                    return False
                if not any(term == row_primary or term in row_core or term == row_cat or term in row_cat for term in matching_terms):
                    return False
                continue

            if req_cat_lower == "gratis":
                if not self._is_free_entry(row):
                    return False
                continue

            if req_cat_lower == "malam":
                if not self._matches_night_destination(row):
                    return False
                continue

            if req_cat_lower in attribute_filters:
                if any(term in row_avoid for term in matching_terms):
                    return False
                if not any(
                    term == row_primary or term in row_core or term in row_secondary or term == row_cat or term in row_cat
                    for term in matching_terms
                ):
                    return False
                continue
                
            matched = False
            for term in matching_terms:
                if term in row_avoid:
                    continue
                if term == row_primary or term in row_core or term == row_cat or term in row_cat:
                    matched = True
                    break
            if not matched:
                return False
        return True

    def _apply_hard_filters(self, df, categories=None, max_price=None, min_rating=None, free_only=False,
                            day_type=None, open_at_hour=None, night_only=False,
                            shopping_subtype=None, facility_filters=None):
        """Langkah A: Filter destinations deterministically based on user constraints."""
        filtered_df = df.copy()
        
        # 1. Kategori (multi_labels + category match)
        if categories:
            mask = filtered_df.apply(lambda r: self._matches_category(r, categories), axis=1)
            filtered_df = filtered_df[mask]
            
        # 2. Harga Maksimum (price_max <= max_price)
        if max_price is not None:
            filtered_df = filtered_df[filtered_df['price_max'] <= max_price]
            
        # 3. Gratis Only (price_type is 'Gratis' or price_max == 0)
        if free_only:
            filtered_df = filtered_df[filtered_df.apply(self._is_free_entry, axis=1)]
            
        # 4. Rating Minimum (avg_rating >= min_rating)
        if min_rating is not None:
            filtered_df = filtered_df[filtered_df['avg_rating'] >= min_rating]
            
        # 5. Jam Operasional
        if open_at_hour is not None:
            dt = day_type if day_type in ('weekday', 'weekend') else 'weekday'
            buka_col = f'jam_buka_{dt}'
            tutup_col = f'jam_tutup_{dt}'
            
            mask = filtered_df.apply(lambda r: self._is_open(r[buka_col], r[tutup_col], open_at_hour), axis=1)
            filtered_df = filtered_df[mask]

        if night_only:
            filtered_df = filtered_df[filtered_df.apply(self._matches_night_destination, axis=1)]

        if shopping_subtype:
            requested_subtype = str(shopping_subtype).strip().lower()
            filtered_df = filtered_df[
                filtered_df.get('shopping_subtype', '').fillna('').astype(str).str.lower().eq(requested_subtype)
            ]

        if facility_filters:
            for col, expected in facility_filters.items():
                if col == "crowd_level":
                    filtered_df = filtered_df[
                        filtered_df.get('crowd_level', '').fillna('').astype(str).str.lower().eq(str(expected).lower())
                    ]
                else:
                    filtered_df = filtered_df[
                        filtered_df.get(col, False).apply(lambda value: self._coerce_bool_value(value, default=False)) == bool(expected)
                    ]
            
        return filtered_df

    def _compute_similarity(self, query, candidate_indices):
        """Langkah B: Compute Dense Cosine Similarity for candidates using SentenceTransformer."""
        cleaned_query = self._preprocess_text(query)
        if not cleaned_query:
            return {idx: 0.0 for idx in candidate_indices}
            
        if not candidate_indices:
            return {}
            
        query_embedding = self.model.encode(cleaned_query, convert_to_tensor=True)
        candidate_embeddings = self.corpus_embeddings[candidate_indices]
        
        sim_matrix = util.cos_sim(query_embedding, candidate_embeddings)
        
        sim_scores = {}
        for i, idx in enumerate(candidate_indices):
            sim_scores[idx] = float(sim_matrix[0][i].item())
            
        return sim_scores

    def _compute_final_score(self, df_filtered, similarity_scores, query=None, weights=None,
                             active_intents=None, sort_by="relevance", nearby_requested=False,
                             shopping_requested=False):
        """Langkah C: Compute final hybrid score and sort candidates."""
        if weights is None:
            if query and query.strip():
                # 35% similarity, 35% sentiment, 20% rating, 10% confidence
                weights = {'similarity': 0.35, 'sentiment': 0.35, 'rating': 0.20, 'confidence': 0.10}
            else:
                # 0% similarity, 55% sentiment, 30% rating, 15% confidence
                weights = {'similarity': 0.0, 'sentiment': 0.55, 'rating': 0.30, 'confidence': 0.15}
                
        results = []
        active_intents = active_intents or []
        for idx, row in df_filtered.iterrows():
            sim_score = similarity_scores.get(idx, 0.0)
            similarity_adjustment = 0.0
            matched_intents = []
            penalized_intents = []
            for intent in active_intents:
                tier = self._label_match_tier(row, intent)
                if tier == "primary":
                    similarity_adjustment += 0.08
                    matched_intents.append(intent)
                elif tier == "core":
                    similarity_adjustment += 0.06
                    matched_intents.append(intent)
                elif tier == "secondary":
                    similarity_adjustment += 0.025
                    matched_intents.append(intent)
                elif tier == "category":
                    similarity_adjustment += 0.02
                    matched_intents.append(intent)
                elif tier == "avoid":
                    similarity_adjustment -= 0.12
                    penalized_intents.append(intent)
                else:
                    similarity_adjustment -= 0.035
            if similarity_adjustment:
                sim_score = max(-1.0, min(1.0, sim_score + similarity_adjustment))

            sentiment_metadata = self._get_sentiment_metadata(row)
            raw_sent_score = sentiment_metadata["sentiment_score"]
            adjusted_sent_score = sentiment_metadata["adjusted_sentiment_score"]
            
            rating = float(row['avg_rating'])
            normalized_rating = rating / 5.0
            
            # Review confidence uses a p95 cap so one extreme review count does not dominate.
            confidence_bonus = sentiment_metadata["review_confidence"]
            
            # Weighted calculation
            weighted_score = (
                weights['similarity'] * sim_score +
                weights['sentiment'] * adjusted_sent_score +
                weights['rating'] * normalized_rating +
                weights['confidence'] * confidence_bonus
            )
            
            base_relevance_score = weighted_score * 100.0
            distance_km = row.get('__distance_km', np.nan)
            has_distance = pd.notna(distance_km)
            distance_score = float(row.get('__distance_score', 0.0)) if has_distance else 0.0
            ranking_mode = sort_by if has_distance or sort_by in {"balanced", "nearest"} else "relevance"
            relevance_weight = 1.0
            distance_weight = 0.0

            if ranking_mode == "balanced":
                relevance_weight, distance_weight = (0.55, 0.45) if nearby_requested else (0.75, 0.25)
            elif ranking_mode == "nearest":
                relevance_weight, distance_weight = 0.35, 0.65

            if distance_weight:
                final_score = (
                    (base_relevance_score / 100.0) * relevance_weight +
                    distance_score * distance_weight
                ) * 100.0
                if not has_distance:
                    final_score *= 0.35 if nearby_requested else 0.60
            else:
                final_score = base_relevance_score

            mall_penalty = 1.0
            if self._is_mall_destination(row) and not shopping_requested:
                mall_penalty = MALL_NEARBY_GENERIC_PENALTY if nearby_requested else MALL_NON_SHOPPING_PENALTY
                final_score *= mall_penalty
            
            results.append({
                'row': row,
                'final_score': round(final_score, 2),
                'score_breakdown': {
                    'base_relevance_score': round(base_relevance_score, 2),
                    'similarity': round(sim_score, 4),
                    'similarity_adjustment': round(similarity_adjustment, 4),
                    'matched_intents': matched_intents,
                    'penalized_intents': penalized_intents,
                    'sentiment_score': round(raw_sent_score, 4),
                    'adjusted_sentiment_score': round(adjusted_sent_score, 4),
                    'sentiment_used_for_ranking': round(adjusted_sent_score, 4),
                    'sentiment_model_source': sentiment_metadata["sentiment_model_source"],
                    'sentiment_model_version': sentiment_metadata["sentiment_model_version"],
                    'sentiment_available': sentiment_metadata["sentiment_available"],
                    'sentiment_label': sentiment_metadata["sentiment_label"],
                    'sentiment_review_count': sentiment_metadata["sentiment_review_count"],
                    'review_confidence': round(confidence_bonus, 4),
                    'review_confidence_label': sentiment_metadata["review_confidence_label"],
                    'sentiment_prior_score': sentiment_metadata["sentiment_prior_score"],
                    'sentiment_review_count_p95': sentiment_metadata["sentiment_review_count_p95"],
                    'google_rating': round(rating, 2),
                    'confidence': round(confidence_bonus, 4),
                    'distance_km': round(float(distance_km), 2) if has_distance else None,
                    'distance_score': round(distance_score, 4) if has_distance else None,
                    'ranking_mode': ranking_mode,
                    'relevance_weight': relevance_weight,
                    'distance_weight': distance_weight,
                    'mall_penalty': round(mall_penalty, 4)
                },
                'sentiment_metadata': sentiment_metadata
            })
            
        if sort_by == "nearest":
            results.sort(
                key=lambda x: (
                    x['score_breakdown'].get('distance_km') is None,
                    x['score_breakdown'].get('distance_km') if x['score_breakdown'].get('distance_km') is not None else float('inf'),
                    -x['score_breakdown'].get('base_relevance_score', 0)
                )
            )
        else:
            # Sort descending by final ranking score
            results.sort(key=lambda x: x['final_score'], reverse=True)
        return results

    def _generate_explanation(self, row, scores, query=None):
        """Generate human-readable explanation in Indonesian for recommendation."""
        parts = []
        name = row['location_name']
        
        # 1. Similarity aspect
        sim = scores.get('similarity', 0.0)
        if query and sim > 0.2:
            parts.append(f"Destinasi '{name}' sangat cocok dengan keinginan Anda mencari '{query}' (relevansi deskripsi {sim:.1%}).")
        elif query:
            parts.append(f"Cocok secara kontekstual dengan preferensi pencarian Anda.")
        else:
            parts.append(f"Direkomendasikan berdasarkan filter kriteria yang Anda tentukan.")
            
        # 2. Sentiment aspect
        sentiment_metadata = self._get_sentiment_metadata(row)
        sent_skor = sentiment_metadata["sentiment_score"]
        adjusted_sent_skor = sentiment_metadata["adjusted_sentiment_score"]
        sent_label = sentiment_metadata["sentiment_label"]
        if sentiment_metadata["sentiment_available"]:
            if not sent_label:
                sent_label = 'Positif' if sent_skor >= 0.5 else 'Netral'
            parts.append(f"Ulasan pengunjung didominasi respon {sent_label.lower()} dengan skor sentimen terkalibrasi {adjusted_sent_skor:.1%}.")
        else:
            parts.append("Skor sentimen ulasan belum tersedia, sehingga rekomendasi lebih bertumpu pada relevansi, rating, dan filter.")
        
        # 3. Google rating and review confidence
        rating = row.get('avg_rating', 0.0)
        ulasan = int(row.get('total_ulasan', 0))
        parts.append(f"Destinasi ini terpercaya dengan rating Google {rating:.2f}/5.0 dari total {ulasan} ulasan.")

        distance_km = scores.get('distance_km')
        if distance_km is not None:
            parts.append(f"Jaraknya sekitar {distance_km:.1f} km dari lokasi Anda.")
        
        return " ".join(parts)

    def recommend(self, query=None, categories=None, max_price=None,
                  min_rating=None, free_only=False, open_now=False,
                  day_type=None, open_at_hour=None, user_lat=None, user_lon=None,
                  max_distance_km=None, sort_by="balanced", top_k=5, explain=True):
        """
        Produce a list of K tourism destination recommendations based on query and filters.
        
        Returns:
            dict containing success status, applied filters, and top K recommendation items.
        """
        actual_day_type = day_type
        actual_open_at_hour = open_at_hour
        parsed_user_lat = self._coerce_float(user_lat)
        parsed_user_lon = self._coerce_float(user_lon)
        parsed_max_distance_km = self._coerce_positive_float(max_distance_km)
        landmark_context = self._detect_landmark_location(query)
        if not self._has_valid_coordinates(parsed_user_lat, parsed_user_lon) and landmark_context:
            parsed_user_lat = landmark_context["latitude"]
            parsed_user_lon = landmark_context["longitude"]
        has_user_location = self._has_valid_coordinates(parsed_user_lat, parsed_user_lon)
        nearby_requested = self._query_requests_nearby(query) or bool(landmark_context)
        night_requested = self._query_requests_night(query)
        ranking_mode = self._normalize_sort_mode(sort_by, has_user_location, nearby_requested)
        requested_shopping_subtype = self._query_requested_shopping_subtype(query)
        waterfall_requested = self._query_requests_waterfall(query)
        shopping_requested = self._query_requests_shopping(query) or bool(requested_shopping_subtype)
        low_crowd_requested = self._query_requests_low_crowd(query)
        facility_filters = self._query_facility_filters(query)
        location_context_payload = {
            "enabled": has_user_location,
            "user_lat": parsed_user_lat if has_user_location else None,
            "user_lon": parsed_user_lon if has_user_location else None,
            "sort_by": ranking_mode,
            "requested_sort_by": sort_by,
            "nearby_query": nearby_requested,
            "max_distance_km": parsed_max_distance_km,
            "source": "landmark" if landmark_context else ("user" if has_user_location else None),
            "landmark_name": landmark_context.get("name") if landmark_context else None
        }
        
        # Handle open_now option
        if open_now:
            now = datetime.datetime.now()
            actual_day_type = "weekend" if now.weekday() >= 5 else "weekday"
            actual_open_at_hour = now.strftime("%H:%M")

        implicit_free_only = False
        implicit_max_price = None
        implicit_open_at_hour = None
        if query and query.strip():
            unsupported_query = self._detect_unsupported_query(query)
            if unsupported_query:
                return {
                    "status": "success",
                    "query": query,
                    "ai_intents": {
                        "enabled": False,
                        "active_intents": [],
                        "scores": {},
                        "lexical_intents": [],
                        "filter_intents": []
                    },
                    "ai_badge": {
                        "enabled": False,
                        "label": "Pencarian Cerdas AI",
                        "active_intents": [],
                        "fallback_used": False
                    },
                    "fallback": {
                        "used": False,
                        "reason": None
                    },
                    "no_strong_match": {
                        "used": True,
                        "label": unsupported_query["label"],
                        "reason": unsupported_query["reason"]
                    },
                    "manual_filters": {
                        "categories": categories,
                        "max_price": max_price,
                        "min_rating": min_rating,
                        "free_only": free_only,
                        "open_now": open_now,
                        "day_type": actual_day_type,
                        "open_at_hour": actual_open_at_hour
                    },
                    "implicit_filters": {
                        "free_only": False,
                        "max_price": None,
                        "open_at_hour": None
                    },
                    "location_context": location_context_payload,
                    "realworld_filters": {
                        "night_only": night_requested,
                        "waterfall_only": waterfall_requested,
                        "waterfall_fallback_used": False,
                        "shopping_subtype": requested_shopping_subtype,
                        "low_crowd_preference": low_crowd_requested,
                        "low_crowd_hard_filter": False,
                        "facility_filters": facility_filters
                    },
                    "total_candidates": len(self.df),
                    "after_filtering": 0,
                    "recommendations": []
                }

            if nearby_requested and not has_user_location:
                return {
                    "status": "success",
                    "query": query,
                    "ai_intents": {
                        "enabled": False,
                        "active_intents": [],
                        "scores": {},
                        "lexical_intents": [],
                        "filter_intents": []
                    },
                    "ai_badge": {
                        "enabled": False,
                        "label": "Pencarian Cerdas AI",
                        "active_intents": [],
                        "fallback_used": False
                    },
                    "fallback": {
                        "used": False,
                        "reason": None
                    },
                    "no_strong_match": {
                        "used": True,
                        "label": "Lokasi diperlukan",
                        "reason": "Query meminta hasil terdekat, tetapi lokasi pengguna atau landmark tidak tersedia."
                    },
                    "manual_filters": {
                        "categories": categories,
                        "max_price": max_price,
                        "min_rating": min_rating,
                        "free_only": free_only,
                        "open_now": open_now,
                        "day_type": actual_day_type,
                        "open_at_hour": actual_open_at_hour
                    },
                    "implicit_filters": {
                        "free_only": False,
                        "max_price": None,
                        "open_at_hour": None
                    },
                    "location_context": location_context_payload,
                    "realworld_filters": {
                        "night_only": night_requested,
                        "waterfall_only": waterfall_requested,
                        "waterfall_fallback_used": False,
                        "shopping_subtype": requested_shopping_subtype,
                        "low_crowd_preference": low_crowd_requested,
                        "low_crowd_hard_filter": False,
                        "facility_filters": facility_filters
                    },
                    "total_candidates": len(self.df),
                    "after_filtering": 0,
                    "recommendations": []
                }

            implicit_free_only = self._query_requests_free(query)
            implicit_max_price = self._extract_price_limit(query)
            if not open_now and actual_open_at_hour is None:
                implicit_open_at_hour = self._extract_open_time(query)
                actual_open_at_hour = implicit_open_at_hour

        effective_free_only = free_only or implicit_free_only
        effective_max_price = max_price if max_price is not None else implicit_max_price
        if actual_open_at_hour is not None and actual_day_type not in ('weekday', 'weekend'):
            actual_day_type = 'weekday'
            
        # Detect implicit intents if there's a search query
        detected_intents = []
        intent_scores = {}
        lexical_intents = []
        if query and query.strip():
            # Get query embedding
            cleaned_query = self._preprocess_text(query)
            if cleaned_query:
                query_embedding = self.model.encode(cleaned_query, convert_to_tensor=True)
                
                for category, phrase_embs in self.intent_embeddings.items():
                    sims = util.cos_sim(query_embedding, phrase_embs)[0]
                    intent_scores[category] = float(sims.max().item())
                
                # Apply absolute threshold and relative margin filter
                max_score = max(intent_scores.values()) if intent_scores else 0.0
                for category, score in intent_scores.items():
                    if score >= INTENT_ABSOLUTE_THRESHOLD and score >= (max_score - INTENT_RELATIVE_MARGIN):
                        detected_intents.append(category)
                lexical_intents = self._apply_lexical_intent_injection(query, detected_intents)
                if lexical_intents:
                    # Explicit query words should dominate the active intent set.
                    # This keeps semantic neighbors like Satwa/Wahana Ekstrem from leaking into broad queries.
                    detected_intents = list(dict.fromkeys(lexical_intents))
                elif implicit_free_only or implicit_max_price is not None:
                    detected_intents = []
                elif implicit_open_at_hour is not None and self._query_has_keyword(query, ["malam"]):
                    detected_intents = []
                        
        # Step A: Hard Filtering (with implicit intents injected)
        injected_categories = list(categories) if categories else []
        filter_intents = list(detected_intents)
        if facility_filters and not lexical_intents:
            # Facility words such as "mushola" and "parkir" are explicit hard filters.
            # Avoid adding broad semantic intents that can force a fallback even when
            # valid facility-matching candidates exist.
            filter_intents = []
        elif lexical_intents:
            filter_intents = list(lexical_intents)
        elif implicit_free_only or implicit_max_price is not None or implicit_open_at_hour is not None:
            filter_intents = []

        for intent in filter_intents:
            if intent not in injected_categories:
                injected_categories.append(intent)
                
        filtered_df = self._apply_hard_filters(
            self.df,
            categories=injected_categories,
            max_price=effective_max_price,
            min_rating=min_rating,
            free_only=effective_free_only,
            day_type=actual_day_type,
            open_at_hour=actual_open_at_hour,
            night_only=night_requested,
            shopping_subtype=requested_shopping_subtype,
            facility_filters=facility_filters
        )

        waterfall_fallback_used = False
        if waterfall_requested:
            waterfall_df = filtered_df[filtered_df.apply(self._matches_waterfall_destination, axis=1)]
            if len(waterfall_df) > 0:
                filtered_df = waterfall_df
                waterfall_fallback_used = len(waterfall_df) < min(top_k, 5)
        
        # Fallback: if injected categories result in 0 candidates and we had auto-detected intents,
        # try filtering using ONLY the user's explicit filters
        using_fallback_filters = False
        can_relax_auto_filters = not (facility_filters and lexical_intents)
        if filtered_df.empty and filter_intents and injected_categories != (categories or []) and can_relax_auto_filters:
            using_fallback_filters = True
            filtered_df = self._apply_hard_filters(
                self.df,
                categories=categories,
                max_price=effective_max_price,
                min_rating=min_rating,
                free_only=effective_free_only,
                day_type=actual_day_type,
                open_at_hour=actual_open_at_hour,
                night_only=night_requested,
                shopping_subtype=requested_shopping_subtype,
                facility_filters=facility_filters
            )
            if waterfall_requested:
                waterfall_df = filtered_df[filtered_df.apply(self._matches_waterfall_destination, axis=1)]
                if len(waterfall_df) > 0:
                    filtered_df = waterfall_df
                    waterfall_fallback_used = len(waterfall_df) < min(top_k, 5)
            
        filtered_df = self._attach_distance_columns(
            filtered_df,
            parsed_user_lat,
            parsed_user_lon,
            parsed_max_distance_km
        )

        no_strong_specific_label = None
        no_strong_specific_reason = None
        if requested_shopping_subtype:
            no_strong_specific_label = f"Belanja {requested_shopping_subtype}"
            no_strong_specific_reason = (
                f"Dataset belum punya kandidat aktif yang terverifikasi sebagai {requested_shopping_subtype}. "
                "Sistem tidak mengganti query spesifik ini dengan belanja umum."
            )
        elif facility_filters:
            no_strong_specific_label = "Fasilitas spesifik"
            no_strong_specific_reason = self._facility_no_match_reason(facility_filters)

        if filtered_df.empty:
            return {
                "status": "success",
                "query": query,
                "ai_intents": {
                    "enabled": bool(detected_intents),
                    "active_intents": detected_intents,
                    "scores": intent_scores,
                    "lexical_intents": lexical_intents,
                    "filter_intents": filter_intents
                },
                "ai_badge": {
                    "enabled": bool(query and query.strip()),
                    "label": "Pencarian Cerdas AI",
                    "active_intents": detected_intents,
                    "fallback_used": using_fallback_filters
                },
                "fallback": {
                    "used": using_fallback_filters,
                    "reason": "AI-inferred intent filters returned no candidates, so the system relaxed automatic intent filters while preserving manual filters." if using_fallback_filters else None
                },
                "no_strong_match": {
                    "used": bool(no_strong_specific_label),
                    "label": no_strong_specific_label,
                    "reason": no_strong_specific_reason
                },
                "manual_filters": {
                    "categories": categories,
                    "max_price": max_price,
                    "min_rating": min_rating,
                    "free_only": free_only,
                    "open_now": open_now,
                    "day_type": actual_day_type,
                    "open_at_hour": actual_open_at_hour
                },
                "implicit_filters": {
                    "free_only": implicit_free_only,
                    "max_price": implicit_max_price,
                    "open_at_hour": implicit_open_at_hour
                },
                "location_context": location_context_payload,
                "realworld_filters": {
                    "night_only": night_requested,
                    "waterfall_only": waterfall_requested,
                    "waterfall_fallback_used": waterfall_fallback_used,
                    "shopping_subtype": requested_shopping_subtype,
                    "low_crowd_preference": low_crowd_requested,
                    "low_crowd_hard_filter": False,
                    "low_crowd_note": (
                        "Preferensi tidak terlalu ramai dipakai sebagai sinyal lembut karena data crowd belum lengkap."
                        if low_crowd_requested else None
                    ),
                    "facility_filters": facility_filters
                },
                "total_candidates": len(self.df),
                "after_filtering": 0,
                "recommendations": []
            }
            
        # Step B: Dense Semantic Matching
        candidate_indices = filtered_df.index.tolist()
        if query and query.strip():
            similarity_scores = self._compute_similarity(query, candidate_indices)
        else:
            similarity_scores = {idx: 0.0 for idx in candidate_indices}
            
        # Step C: Weighted Scoring and Ranking
        scored_results = self._compute_final_score(
            filtered_df,
            similarity_scores,
            query=query,
            active_intents=detected_intents,
            sort_by=ranking_mode,
            nearby_requested=nearby_requested,
            shopping_requested=shopping_requested
        )
        
        # Slice top_k
        top_results = scored_results[:top_k]
        
        recommendations = []
        for rank_idx, res in enumerate(top_results, 1):
            row = res['row']
            
            # Format practical info
            p_min = int(row['price_min'])
            p_max = int(row['price_max'])
            p_type = str(row['price_type'])
            
            if p_type.lower() == 'gratis' or p_max == 0:
                harga_str = "Gratis"
            elif p_min == p_max:
                harga_str = f"Rp {p_min:,}".replace(",", ".")
                if p_type and p_type.lower() != 'gratis' and p_type.lower() != 'nan':
                    harga_str += f" ({p_type})"
            else:
                harga_str = f"Rp {p_min:,} - Rp {p_max:,}".replace(",", ".")
                if p_type and p_type.lower() != 'gratis' and p_type.lower() != 'nan':
                    harga_str += f" ({p_type})"
                    
            # Opening hours formatting
            b_wd = str(row['jam_buka_weekday']) if pd.notna(row['jam_buka_weekday']) else 'Tutup'
            t_wd = str(row['jam_tutup_weekday']) if pd.notna(row['jam_tutup_weekday']) else 'Tutup'
            b_we = str(row['jam_buka_weekend']) if pd.notna(row['jam_buka_weekend']) else 'Tutup'
            t_we = str(row['jam_tutup_weekend']) if pd.notna(row['jam_tutup_weekend']) else 'Tutup'
            
            jam_weekday = f"{b_wd} - {t_wd}" if b_wd != 'Tutup' and t_wd != 'Tutup' else 'Tutup'
            jam_weekend = f"{b_we} - {t_we}" if b_we != 'Tutup' and t_we != 'Tutup' else 'Tutup'
            
            durasi = f"{int(row['estimasi_durasi_menit'])} menit" if pd.notna(row['estimasi_durasi_menit']) else "N/A"
            koordinat = [float(row['latitude']), float(row['longitude'])] if pd.notna(row['latitude']) and pd.notna(row['longitude']) else []
            distance_km = res['score_breakdown'].get('distance_km')
            distance_label = f"{distance_km:.1f} km dari lokasi Anda" if distance_km is not None else None
            sentiment_metadata = res.get('sentiment_metadata', {})
            
            rec_item = {
                "rank": rank_idx,
                "location_id": row.get('location_id', ''),
                "location_name": row['location_name'],
                "category": row['category'],
                "multi_labels": row.get('display_labels_parsed', row.get('multi_labels_parsed', [])),
                "label_taxonomy": {
                    "primary_intent": row.get('primary_intent_final', ''),
                    "core_labels": row.get('core_labels_parsed', []),
                    "secondary_labels": row.get('secondary_labels_parsed', []),
                    "avoid_labels": row.get('avoid_labels_parsed', []),
                    "shopping_subtype": row.get('shopping_subtype', '') if pd.notna(row.get('shopping_subtype', '')) else '',
                    "display_status": row.get('display_status', ''),
                    "curation_action": row.get('curation_action', '')
                },
                "realworld_flags": {
                    "is_active_verified": self._coerce_bool_value(row.get('is_active_verified', False), default=False),
                    "price_verified": self._coerce_bool_value(row.get('price_verified', False), default=False),
                    "coordinate_verified": self._coerce_bool_value(row.get('coordinate_verified', True), default=True),
                    "night_verified": self._coerce_bool_value(row.get('night_verified', False), default=False),
                    "indoor_verified": self._coerce_bool_value(row.get('indoor_verified', False), default=False),
                    "child_friendly_verified": self._coerce_bool_value(row.get('child_friendly_verified', False), default=False),
                    "parking_verified": self._coerce_bool_value(row.get('parking_verified', False), default=False),
                    "wheelchair_accessible_verified": self._coerce_bool_value(row.get('wheelchair_accessible_verified', False), default=False),
                    "toilet_verified": self._coerce_bool_value(row.get('toilet_verified', False), default=False),
                    "mushola_verified": self._coerce_bool_value(row.get('mushola_verified', False), default=False),
                    "pet_friendly_verified": self._coerce_bool_value(row.get('pet_friendly_verified', False), default=False),
                    "safety_verified": self._coerce_bool_value(row.get('safety_verified', False), default=False),
                    "open_24h_verified": self._coerce_bool_value(row.get('open_24h_verified', False), default=False),
                    "crowd_level": row.get('crowd_level', 'unknown')
                },
                "final_score": res['final_score'],
                "distance_km": distance_km,
                "distance_label": distance_label,
                "media": self._get_media_metadata(row),
                "score_breakdown": res['score_breakdown'],
                "sentiment_score": sentiment_metadata.get("sentiment_score"),
                "adjusted_sentiment_score": sentiment_metadata.get("adjusted_sentiment_score"),
                "sentiment_model_source": sentiment_metadata.get("sentiment_model_source"),
                "sentiment_model_version": sentiment_metadata.get("sentiment_model_version"),
                "sentiment_available": sentiment_metadata.get("sentiment_available"),
                "review_confidence": sentiment_metadata.get("review_confidence"),
                "review_confidence_label": sentiment_metadata.get("review_confidence_label"),
                "sentiment_metadata": sentiment_metadata,
                "info_praktis": {
                    "harga": harga_str,
                    "jam_buka_weekday": jam_weekday,
                    "jam_buka_weekend": jam_weekend,
                    "estimasi_durasi": durasi,
                    "koordinat": koordinat
                }
            }
            
            if explain:
                rec_item["alasan"] = self._generate_explanation(row, res['score_breakdown'], query)
                
            recommendations.append(rec_item)
            
        return {
            "status": "success",
            "query": query,
            "ai_intents": {
                "enabled": bool(detected_intents),
                "active_intents": detected_intents,
                "scores": intent_scores,
                "lexical_intents": lexical_intents,
                "filter_intents": filter_intents
            },
            "ai_badge": {
                "enabled": bool(query and query.strip()),
                "label": "Pencarian Cerdas AI",
                "active_intents": detected_intents,
                "fallback_used": using_fallback_filters
            },
            "fallback": {
                "used": using_fallback_filters,
                "reason": "AI-inferred intent filters returned no candidates, so the system relaxed automatic intent filters while preserving manual filters." if using_fallback_filters else None
            },
            "no_strong_match": {
                "used": False,
                "label": None,
                "reason": None
            },
            "manual_filters": {
                "categories": categories,
                "max_price": max_price,
                "min_rating": min_rating,
                "free_only": free_only,
                "open_now": open_now,
                "day_type": actual_day_type,
                "open_at_hour": actual_open_at_hour
            },
            "implicit_filters": {
                "free_only": implicit_free_only,
                "max_price": implicit_max_price,
                "open_at_hour": implicit_open_at_hour
            },
            "location_context": location_context_payload,
            "realworld_filters": {
                "night_only": night_requested,
                "waterfall_only": waterfall_requested,
                "waterfall_fallback_used": waterfall_fallback_used,
                "shopping_subtype": requested_shopping_subtype,
                "low_crowd_preference": low_crowd_requested,
                "low_crowd_hard_filter": False,
                "low_crowd_note": (
                    "Preferensi tidak terlalu ramai dipakai sebagai sinyal lembut karena data crowd belum lengkap."
                    if low_crowd_requested else None
                ),
                "facility_filters": facility_filters
            },
            "total_candidates": len(self.df),
            "total_rows_before_status_filter": self.total_rows_before_status_filter,
            "database_source": self.source_db_path,
            "after_filtering": len(filtered_df),
            "recommendations": recommendations
        }

    def print_recommendations(self, results):
        """Pretty-print hasil rekomendasi ke terminal (Windows safe, no emojis)."""
        if results.get("status") != "success":
            print("Gagal mengambil rekomendasi.")
            return
            
        query = results.get("query")
        ai_intents = results.get("ai_intents", {})
        detected = ai_intents.get("active_intents", [])
        fallback = results.get("fallback", {})
        filters = results.get("manual_filters", {})
        implicit_filters = results.get("implicit_filters", {})
        location_context = results.get("location_context", {})
        recs = results.get("recommendations", [])
        
        print("=" * 70)
        print("                 HASIL REKOMENDASI MUTERBANDUNG")
        print("=" * 70)
        if query:
            print(f"Pencarian   : '{query}'")
            if detected:
                status_str = "Diterapkan"
                if fallback.get("used"):
                    status_str = "Dideteksi, lalu filter otomatis dilonggarkan"
                print(f"Niat (AI)   : {', '.join(detected)} ({status_str})")
        else:
            print("Pencarian   : (Tanpa Pencarian Teks)")
            
        active_filters = []
        if filters.get("categories"):
            active_filters.append(f"Kategori={filters['categories']}")
        if filters.get("max_price") is not None:
            active_filters.append(f"Harga Maks=Rp {filters['max_price']:,}".replace(",", "."))
        if filters.get("min_rating") is not None:
            active_filters.append(f"Rating Min={filters['min_rating']}")
        if filters.get("free_only"):
            active_filters.append("Hanya Gratis")
        if implicit_filters.get("free_only"):
            active_filters.append("Gratis (dari teks)")
        if implicit_filters.get("max_price") is not None:
            active_filters.append(f"Harga Teks Maks=Rp {implicit_filters['max_price']:,}".replace(",", "."))
        if filters.get("open_now"):
            active_filters.append(f"Buka Sekarang ({filters['day_type']}, {filters['open_at_hour']})")
        elif filters.get("open_at_hour"):
            active_filters.append(f"Buka Jam {filters['open_at_hour']} ({filters['day_type']})")
            
        if active_filters:
            print(f"Filter Aktif: {', '.join(active_filters)}")
        else:
            print("Filter Aktif: (Tidak ada)")

        if location_context.get("enabled"):
            print(
                "Lokasi User  : "
                f"{location_context.get('user_lat')}, {location_context.get('user_lon')} "
                f"(mode {location_context.get('sort_by')})"
            )
            
        print(f"Kandidat    : {results.get('after_filtering')} dari {results.get('total_candidates')} destinasi")
        print("-" * 70)
        
        if not recs:
            print("Tidak ada destinasi yang cocok dengan kriteria filter Anda.")
            print("=" * 70)
            return
            
        for rec in recs:
            print(f"RANK #{rec['rank']}: {rec['location_name']} (Skor Akhir: {rec['final_score']})")
            print(f"  Kategori    : {rec['category']}")
            print(f"  Multi-labels: {rec['multi_labels']}")
            
            bd = rec['score_breakdown']
            print(f"  Scoring     : Sim={bd['similarity']:.4f} | SentimenAdj={bd['adjusted_sentiment_score']:.4f} | Rating={bd['google_rating']:.2f} | Conf={bd['confidence']:.4f}")
            
            info = rec['info_praktis']
            print(f"  Harga       : {info['harga']}")
            if rec.get('distance_label'):
                print(f"  Jarak       : {rec['distance_label']}")
            print(f"  Jam Buka    : Weekday ({info['jam_buka_weekday']}) | Weekend ({info['jam_buka_weekend']})")
            print(f"  Durasi      : {info['estimasi_durasi']}")
            if info.get('koordinat'):
                print(f"  Koordinat   : Lat={info['koordinat'][0]}, Lng={info['koordinat'][1]}")
                
            if "alasan" in rec:
                print(f"  Alasan      : {rec['alasan']}")
                
            print("-" * 70)
        print("=" * 70)
