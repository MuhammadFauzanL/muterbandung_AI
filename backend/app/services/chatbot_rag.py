"""
Chatbot RAG MuterBandung — Service Module
Menggabungkan MiniLM Retriever + Cloudflare Llama-3.1 Generator
untuk menjawab pertanyaan wisata Bandung secara natural.
"""
import os
import re
import math
import json
import requests


# Cloudflare Workers AI Configuration
CF_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CF_API_TOKEN", "")
CF_MODEL = os.getenv("CF_MODEL", "@cf/meta/llama-3.1-8b-instruct")

# Kata kunci untuk deteksi tipe pertanyaan
COMPLEX_KEYWORDS = [
    "itinerary", "rencana perjalanan", "jadwal", "3 hari", "2 hari",
    "planning", "schedule", "rute perjalanan"
]

DISTANCE_KEYWORDS = [
    "berapa jauh", "jarak", "seberapa jauh", "dari.*ke",
    "how far", "distance"
]

BUDGET_KEYWORDS = [
    "habis berapa", "budget", "biaya", "total harga", "estimasi biaya",
    "berapa totalnya", "kalau mau ke.*berapa"
]

# Blacklist kata kunci untuk menolak pertanyaan di luar konteks
BLACKLIST_KEYWORDS = [
    "buatkan code", "coding", "html", "java", "python", "c++", "php", "javascript",
    "politik", "presiden", "pemilu", "agama", "siapa tuhan", "ganjil genap",
    "matematika", "rumus", "sains", "fisika", "kimia", "sejarah dunia"
]

SYSTEM_PROMPT = """Anda adalah Asisten Wisata MuterBandung — chatbot cerdas yang HANYA membantu wisatawan menjelajahi Bandung.

ATURAN SANGAT KETAT (WAJIB DIIKUTI):
1. JIKA PERTANYAAN TIDAK BERHUBUNGAN DENGAN WISATA BANDUNG, ANDA WAJIB MENJAWAB TEPAT SEPERTI INI: "Maaf, saya hanya Asisten Wisata MuterBandung. Saya tidak bisa menjawab pertanyaan di luar topik wisata Bandung Raya."
2. JANGAN PERNAH membuat kode pemrograman (Java, Python, dll), menjawab soal matematika, atau membahas topik sensitif.
3. Jawab HANYA berdasarkan data konteks yang diberikan di bawah ini. JANGAN mengarang informasi atau berhalusinasi.
4. Jika konteks kosong, patuhi Aturan #1 atau jawab secara umum tentang wisata Bandung.
5. Estimasi budget HANYA untuk 1 orang (selalu ingatkan pengguna).
6. Untuk jarak, jelaskan bahwa ini adalah jarak garis lurus (bukan rute jalan).
7. Jawab secara singkat dan padat (maksimal 3 paragraf).
"""


class ChatbotRAG:
    """Chatbot RAG yang menghubungkan MiniLM Retriever dengan Cloudflare Llama-3.1."""

    def __init__(self, recommender):
        """
        Args:
            recommender: Instance MuterBandungRecommender yang sudah terinisialisasi.
        """
        self.recommender = recommender
        self.cf_url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/{CF_MODEL}"
        self.cf_headers = {
            "Authorization": f"Bearer {CF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        print("[ChatbotRAG] Initialized with Cloudflare Llama-3.1")

    def _call_cloudflare_llm(self, system_prompt, user_message):
        """Mengirim prompt ke Cloudflare Workers AI dan mengembalikan (teks_jawaban, is_success)."""
        if not CF_ACCOUNT_ID or not CF_API_TOKEN:
            return "Cloudflare credentials are not configured.", False
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 512,
                "temperature": 0.7
            }
            response = requests.post(self.cf_url, headers=self.cf_headers, json=payload, timeout=30)
            data = response.json()

            if response.status_code == 200 and data.get("success"):
                return data["result"]["response"], True
            else:
                error_msg = data.get("errors", [{}])[0].get("message", "Unknown error")
                return f"Error API: {error_msg}", False
        except requests.exceptions.Timeout:
            return "Timeout", False
        except Exception as e:
            return str(e), False

    def _haversine_km(self, lat1, lon1, lat2, lon2):
        """Menghitung jarak antara dua titik GPS dalam kilometer."""
        radius_km = 6371.0088
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = (math.sin(dlat / 2) ** 2
             + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
        return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _search_destination(self, name_query):
        """Mencari destinasi berdasarkan nama (exact/fuzzy) di database."""
        df = self.recommender.df
        name_lower = name_query.strip().lower()
        
        # Exact match
        exact = df[df['location_name'].str.lower() == name_lower]
        if not exact.empty:
            return exact.iloc[0]
        
        # Contains match
        contains = df[df['location_name'].str.lower().str.contains(name_lower, na=False)]
        if not contains.empty:
            return contains.iloc[0]
        
        return None

    def _build_rag_context(self, query, top_k=3):
        """Mengambil data wisata relevan dari database menggunakan MiniLM."""
        try:
            result = self.recommender.recommend(query=query, top_k=top_k)
            recommendations = result.get("recommendations", [])

            if not recommendations:
                return None, []

            # LAPIS KEDUA: Cek Threshold Similarity dari MiniLM
            top_rec = recommendations[0]
            similarity = top_rec.get("score_breakdown", {}).get("similarity", 0.0)
            if similarity < 0.3:
                print(f"[ChatbotRAG] Pertanyaan ditolak karena skor relevansi terlalu rendah ({similarity:.2f} < 0.3)")
                return None, []

            context_parts = []
            for i, rec in enumerate(recommendations, 1):
                info = rec.get("info_praktis", {})
                row = rec
                
                name = row.get("location_name", "Tidak diketahui")
                category = row.get("category", "-")
                price = info.get("harga", "Tidak ada info")
                jam_weekday = info.get("jam_buka_weekday", "Tidak ada info")
                jam_weekend = info.get("jam_buka_weekend", "Tidak ada info")
                durasi = info.get("estimasi_durasi", "Tidak ada info")
                rating = row.get("avg_rating", "-")
                total_ulasan = row.get("total_ulasan", 0)
                deskripsi = row.get("deskripsi_google", "")
                labels = row.get("multi_labels", [])
                zona = row.get("zona_wisata", "-")
                lat = row.get("latitude", None)
                lon = row.get("longitude", None)

                # Fasilitas
                fasilitas = []
                if row.get("parking_verified"): fasilitas.append("Parkir")
                if row.get("toilet_verified"): fasilitas.append("Toilet")
                if row.get("mushola_verified"): fasilitas.append("Mushola")
                if row.get("child_friendly_verified"): fasilitas.append("Ramah Anak")

                ctx = f"""--- Destinasi #{i}: {name} ---
Kategori: {category}
Label: {', '.join(labels) if isinstance(labels, list) else labels}
Harga: {price}
Jam Buka Weekday: {jam_weekday}
Jam Buka Weekend: {jam_weekend}
Estimasi Durasi: {durasi}
Rating: {rating}/5 ({total_ulasan} ulasan)
Zona: {zona}
Koordinat: {lat}, {lon}
Fasilitas: {', '.join(fasilitas) if fasilitas else 'Belum terverifikasi'}
Deskripsi: {deskripsi[:200] if deskripsi else 'Tidak tersedia'}
"""
                context_parts.append(ctx)

            return "\n".join(context_parts), recommendations

        except Exception as e:
            print(f"[ChatbotRAG] Error in _build_rag_context: {e}")
            return None, []

    def _detect_complex_query(self, query):
        """Deteksi pertanyaan yang terlalu kompleks untuk chatbot."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in COMPLEX_KEYWORDS)

    def _detect_distance_query(self, query):
        """Deteksi pertanyaan tentang jarak antar tempat."""
        query_lower = query.lower()
        return any(re.search(kw, query_lower) for kw in DISTANCE_KEYWORDS)

    def _detect_budget_query(self, query):
        """Deteksi pertanyaan tentang estimasi budget."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in BUDGET_KEYWORDS)

    def _detect_blacklist_query(self, query):
        """Deteksi apakah pertanyaan mengandung kata kunci blacklist (di luar topik)."""
        query_lower = query.lower()
        return any(kw in query_lower for kw in BLACKLIST_KEYWORDS)

    def _handle_distance_query(self, query):
        """Menangani pertanyaan estimasi jarak A → B."""
        # Coba ekstrak dua nama tempat
        pattern = r"(?:dari|from)\s+(.+?)\s+(?:ke|to|menuju|sampai)\s+(.+?)(?:\?|$|\.)"
        match = re.search(pattern, query, re.IGNORECASE)
        
        if not match:
            # Coba pola alternatif: "jarak X dan Y" atau "jarak X ke Y"
            pattern2 = r"(?:jarak|distance)\s+(.+?)\s+(?:dan|ke|dengan|to)\s+(.+?)(?:\?|$|\.)"
            match = re.search(pattern2, query, re.IGNORECASE)

        if not match:
            return None

        place_a_name = match.group(1).strip()
        place_b_name = match.group(2).strip()

        place_a = self._search_destination(place_a_name)
        place_b = self._search_destination(place_b_name)

        if place_a is None or place_b is None:
            not_found = []
            if place_a is None: not_found.append(place_a_name)
            if place_b is None: not_found.append(place_b_name)
            return f"Maaf, saya tidak menemukan destinasi berikut di database: {', '.join(not_found)}. Pastikan nama tempat sudah benar."

        lat_a = float(place_a.get("latitude", 0))
        lon_a = float(place_a.get("longitude", 0))
        lat_b = float(place_b.get("latitude", 0))
        lon_b = float(place_b.get("longitude", 0))

        distance = self._haversine_km(lat_a, lon_a, lat_b, lon_b)
        
        name_a = place_a.get("location_name", place_a_name)
        name_b = place_b.get("location_name", place_b_name)

        return (
            f"📍 Estimasi jarak dari **{name_a}** ke **{name_b}** adalah sekitar "
            f"**{distance:.1f} km** (garis lurus).\n\n"
            f"⚠️ *Catatan: Ini adalah jarak garis lurus. Jarak tempuh di jalan raya bisa lebih jauh "
            f"tergantung rute yang dilalui.*"
        )

    def chat(self, user_message):
        """Fungsi utama chatbot — menerima pesan dan mengembalikan jawaban."""
        if not user_message or not user_message.strip():
            return {
                "response": "Silakan ketik pertanyaan Anda tentang wisata Bandung! 😊",
                "type": "empty"
            }

        query = user_message.strip()

        # 1. LAPIS PERTAMA: Filter Blacklist
        if self._detect_blacklist_query(query):
            return {
                "response": "Maaf, saya hanya Asisten Wisata MuterBandung. Saya tidak bisa menjawab pertanyaan tentang pemrograman, matematika, politik, atau hal lain di luar topik wisata Bandung.",
                "type": "redirect"
            }

        # 2. Deteksi pertanyaan kompleks → redirect
        if self._detect_complex_query(query):
            return {
                "response": (
                    "Pertanyaan Anda membutuhkan perencanaan yang lebih detail! 🗺️\n\n"
                    "Untuk pembuatan **itinerary** dan **rencana perjalanan** lengkap, "
                    "silakan gunakan fitur **Explore & Planner** di halaman utama MuterBandung.\n\n"
                    "Di sana, Anda bisa memilih destinasi, mengatur jadwal, dan melihat peta interaktif!"
                ),
                "type": "redirect"
            }

        # 2. Deteksi pertanyaan jarak
        if self._detect_distance_query(query):
            distance_result = self._handle_distance_query(query)
            if distance_result:
                return {
                    "response": distance_result,
                    "type": "distance"
                }

        # 4. RAG: Ambil data relevan dari database (termasuk filter Lapis 2)
        context, recommendations = self._build_rag_context(query, top_k=3)

        if not context:
            # Fallback: tanya LLM tanpa konteks tapi dengan batasan
            fallback_prompt = SYSTEM_PROMPT + "\n\nTidak ada data spesifik dari database. Jawab secara umum tentang wisata Bandung jika relevan, atau tolak jika di luar topik."
            response_text, is_success = self._call_cloudflare_llm(fallback_prompt, query)
            if not is_success:
                return {
                    "response": "Maaf, fitur AI percakapan sedang gangguan koneksi dan tidak ada data rekomendasi spesifik yang bisa ditampilkan saat ini.",
                    "type": "error"
                }
            return {
                "response": response_text,
                "type": "general"
            }

        # 5. Bangun prompt RAG (Context + Question)
        rag_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== DATA WISATA DARI DATABASE (GUNAKAN DATA INI UNTUK MENJAWAB) ===\n"
            f"{context}\n"
            f"=== AKHIR DATA ===\n\n"
            f"Berdasarkan data di atas, jawab pertanyaan pengguna berikut dengan natural dan informatif.\n"
            f"Jika pertanyaan tentang budget, hitung total dan ingatkan bahwa estimasi untuk 1 orang saja.\n"
            f"Jika data yang diminta tidak ada di konteks, katakan bahwa data belum tersedia."
        )

        # 5. Kirim ke Cloudflare Llama-3.1
        response_text, is_success = self._call_cloudflare_llm(rag_prompt, query)

        # 6. FAILOVER MECHANISM (Graceful Degradation)
        if not is_success:
            print(f"[ChatbotRAG] Failover aktif! Cloudflare error: {response_text}")
            fallback_text = (
                "⚠️ *Maaf, fitur AI percakapan kami sedang mengalami gangguan koneksi ke server pusat.* \n\n"
                "Namun jangan khawatir, berikut adalah rekomendasi terbaik dari sistem lokal kami berdasarkan pencarian Anda:\n\n"
            )
            for i, rec in enumerate(recommendations, 1):
                name = rec.get("location_name", "Destinasi")
                info = rec.get("info_praktis", {})
                harga = info.get("harga", "-")
                jam = info.get("jam_buka_weekday", "-")
                fallback_text += f"{i}. **{name}**\n   💰 Harga: {harga}\n   🕒 Jam: {jam}\n\n"

            return {
                "response": fallback_text,
                "type": "failover",
                "sources": [r.get("location_name", "") for r in recommendations],
                "raw_data": [r.get("location_name", "") for r in recommendations]
            }

        return {
            "response": response_text,
            "type": "rag",
            "sources": [r.get("location_name", "") for r in recommendations]
        }
