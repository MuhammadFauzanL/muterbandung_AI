import os
import json
import re
import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct"
ENABLE_ONLINE_LLM_VALUES = {"1", "true", "yes", "on"}

def _clean_env(value):
    if value is None:
        return ""
    return str(value).strip().strip('"').strip("'")

def parse_intent_with_llm(query):
    """
    Mengubah query natural user menjadi JSON parameter menggunakan LLM (Zero-shot, fast).
    Bypass untuk query yang sangat pendek (<= 3 kata).
    """
    if not query or len(query.split()) <= 2:
        return None
        
    online_llm_enabled = _clean_env(os.getenv("MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM")).lower()
    if online_llm_enabled not in ENABLE_ONLINE_LLM_VALUES:
        return None

    api_key = _clean_env(os.getenv("OPENROUTER_API_KEY"))
    if not api_key:
        return None

    # Gunakan model haiku atau 8B-instruct yang cepat
    model = _clean_env(os.getenv("OPENROUTER_MODEL")) or DEFAULT_OPENROUTER_MODEL
    
    system_prompt = """Kamu adalah sistem Intent Parser untuk MuterBandung. 
Tugasmu adalah membaca query user dan mengekstrak parameternya menjadi strict JSON.
Aturan:
- kategori: Ekstrak semua kata kunci tujuan/vibe wisata. Pilih dari ["Alam", "Budaya", "Edukasi", "Kuliner", "Petualangan", "Belanja", "Religi", "Sejarah", "Hiburan", "Seni", "Keluarga"]. (Jika ada kata keluarga, masukkan "Keluarga"). Jika tidak ada, kosongkan [].
- harga_maks: Integer nilai uang (misal 50000) atau null jika tidak ada batasan angka.
- lokasi: String wilayah, daerah, atau landmark (misal "dago", "lembang", "kawah putih") atau null.
- ramah_anak: Boolean true jika untuk keluarga/anak, false, atau null.
- gratis: Boolean true jika teks meminta gratis/tanpa tiket, false, atau null.

CONTOH: 
User: "wisata alam murah di dago buat anak gratis"
Output: {"kategori": ["Alam"], "harga_maks": null, "lokasi": "dago", "ramah_anak": true, "gratis": true}

User: "cari hotel dekat gasibu"
Output: {"kategori": [], "harga_maks": null, "lokasi": "gasibu", "ramah_anak": null, "gratis": null}

KEMBALIKAN JSON SAJA. TANPA TEKS LAIN."""

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User: \"{query}\"\nOutput:"}
        ],
        "temperature": 0.0, 
        "max_tokens": 150
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://muterbandung.id",
        "X-Title": "MuterBandung-LLMExtractor",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()
        
        content = result["choices"][0]["message"]["content"].strip()
        
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
            
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"[LLM Extractor] Failed: {e}")
        return None
