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

def _call_cloudflare_ai(system_prompt, user_query):
    """Layanan LLM Layer 1: Cloudflare Workers AI."""
    account_id = _clean_env(os.getenv("CLOUDFLARE_ACCOUNT_ID"))
    api_token = _clean_env(os.getenv("CLOUDFLARE_API_TOKEN"))
    
    if not account_id or not api_token:
        return None, "Cloudflare credentials not configured."
        
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-3.3-70b-instruct-fp8-fast"
    headers = {"Authorization": f"Bearer {api_token}"}
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User: \"{user_query}\"\nOutput:"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=4)
        if response.status_code == 200:
            result = response.json()
            # Cloudflare response format differs from OpenAI
            return result.get("result", {}).get("response", ""), None
        return None, f"Cloudflare returned {response.status_code}"
    except Exception as e:
        return None, str(e)

def _call_openrouter(system_prompt, user_query):
    """Layanan LLM Layer 2: OpenRouter (Backup)."""
    api_key = _clean_env(os.getenv("OPENROUTER_API_KEY"))
    if not api_key:
        return None, "OpenRouter API Key not configured."
        
    model = _clean_env(os.getenv("OPENROUTER_MODEL")) or DEFAULT_OPENROUTER_MODEL
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User: \"{user_query}\"\nOutput:"}
        ],
        "temperature": 0.0,
        "max_tokens": 150
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://muterbandung.id",
        "X-Title": "MuterBandung-Failover",
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"], None
        return None, f"OpenRouter returned {response.status_code}"
    except Exception as e:
        return None, str(e)

def parse_intent_with_llm(query):
    """
    Mengubah query natural user menjadi JSON parameter.
    Arsitektur Failover: Cloudflare (Layer 1) -> OpenRouter (Layer 2).
    """
    if not query or len(query.split()) <= 2:
        return None

    online_llm_enabled = _clean_env(os.getenv("MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM")).lower()
    if online_llm_enabled not in ENABLE_ONLINE_LLM_VALUES:
        return None

    system_prompt = """Kamu adalah sistem Intent Parser untuk MuterBandung. 
Tugasmu adalah membaca query user dan mengekstrak parameternya menjadi strict JSON.
Aturan:
- kategori: Ekstrak semua kata kunci tujuan/vibe wisata. Pilih dari ["Alam", "Budaya", "Edukasi", "Kuliner", "Petualangan", "Belanja", "Religi", "Sejarah", "Hiburan", "Seni", "Keluarga"]. (Jika ada kata keluarga, masukkan "Keluarga"). Jika tidak ada, kosongkan [].
- harga_maks: Integer nilai uang (misal 50000) atau null jika tidak ada batasan angka.
- lokasi: String wilayah, daerah, atau landmark (misal "dago", "lembang", "kawah putih") atau null.
- ramah_anak: Boolean true jika untuk keluarga/anak, false, atau null.
- gratis: Boolean true jika teks meminta gratis/tanpa tiket, false, atau null.
KEMBALIKAN JSON SAJA. TANPA TEKS LAIN."""

    # --- EKSEKUSI FAILOVER ---
    content = None
    
    # 1. Coba Cloudflare Workers AI
    print("[LLM] Attempting Layer 1 (Cloudflare)...")
    content, cf_error = _call_cloudflare_ai(system_prompt, query)
    if isinstance(content, dict): content = json.dumps(content)
    
    # 2. Jika Cloudflare gagal, pindah ke OpenRouter
    if not content:
        print(f"[LLM] Layer 1 Failed ({cf_error}). Switching to Layer 2 (OpenRouter)...")
        content, or_error = _call_openrouter(system_prompt, query)
        
    if not content:
        print("[LLM] All Layers Failed.")
        return None

    # --- PARSING JSON ---
    try:
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            content = match.group(0)
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"[LLM Parser] JSON Error: {e}")
        return None



