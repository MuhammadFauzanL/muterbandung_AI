import os
import json
import requests
from dotenv import load_dotenv

# Load env variables from .env
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Default Model: Poolside Laguna M.1 (Free). Fast and currently not rate-limited.
DEFAULT_MODEL = "poolside/laguna-m.1:free"

def generate_rag_summary(query, evidence_pack, module="wisata", timeout=8.0):
    """
    Sends the evidence_pack to OpenRouter to generate a natural, conversational summary.
    Falls back to None if API key is missing or request fails.
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY.startswith("sk-or-v1-...") or len(OPENROUTER_API_KEY) < 10:
        print("[LLM Service] OpenRouter API Key not configured. Skipping external LLM call.")
        return None

    # Construct the JSON prompt payload
    evidence_json = json.dumps(evidence_pack, indent=2, ensure_ascii=False)
    
    system_prompt = (
        "Anda adalah Asisten MuterBandung, asisten pintar berbasis AI yang memberikan rekomendasi pariwisata "
        "dan penginapan di wilayah Bandung secara ramah, luwes, dan seperti teman.\n\n"
        "Tugas Anda:\n"
        "1. Baca data rekomendasi (evidence_pack) yang diberikan dalam format JSON.\n"
        "2. Buatlah 1 paragraf ringkas (maksimal 3 kalimat) yang menjelaskan hasil rekomendasi teratas kepada pengguna.\n"
        "3. Berikan alasan MENGAPA tempat itu cocok dengan kriteria/keinginan pengguna (baca dari 'query' dan 'alasan').\n"
        "4. Gunakan bahasa Indonesia yang luwes (bisa pakai kata 'Anda', 'kita', dsb). Jangan terlihat seperti robot pembaca data.\n"
        "5. Jangan sertakan format Markdown/bold berlebihan, cukup teks biasa yang rapi."
    )

    user_prompt = (
        f"Konteks Pencarian Pengguna (Query): '{query}'\n"
        f"Modul yang dicari: {module}\n\n"
        f"Berikut adalah data teratas hasil dari mesin logika Python kami:\n{evidence_json}\n\n"
        "Tolong buatkan ringkasannya sekarang."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "MuterBandung Local",
    }

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 150
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        
        # Extract the LLM reply
        ai_reply = data["choices"][0]["message"]["content"].strip()
        print(f"[LLM Service] Generated RAG summary ({len(ai_reply)} chars).")
        return ai_reply
        
    except requests.exceptions.Timeout:
        print("[LLM Service] OpenRouter API request timed out.")
        return None
    except Exception as e:
        print(f"[LLM Service] Error calling OpenRouter API: {e}")
        return None
