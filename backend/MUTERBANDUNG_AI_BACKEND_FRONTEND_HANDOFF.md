# MuterBandung AI Backend + Frontend Handoff

Tanggal audit: 2026-06-17  
Branch saat audit: `feature/backend-ai-core-stable`  
Status dokumen: panduan kerja untuk AI agent, backend developer, dan frontend developer.

Dokumen ini menyatukan dan memperluas:

- `backend/BACKEND_AI_AGENT_IMPLEMENTATION.md`
- `backend/FRONTEND_AI_INTEGRATION_GUIDE.md`

Tujuannya bukan membuat dokumen marketing. Tujuannya adalah agar developer paham alur sistem saat ini, file mana yang dipakai, dataset mana yang menjadi runtime, endpoint mana yang tersedia, dan bagian mana yang masih perlu dibereskan.

---

## 1. Ringkasan Sistem Saat Ini

MuterBandung saat ini memakai arsitektur tiga lapis:

| Layer | Folder/File | Peran |
|---|---|---|
| Frontend | `frontend/` | UI Next.js. Menampilkan pencarian wisata, planner, penginapan, chatbot, dan card rekomendasi. |
| Backend Core | `backend_core/app/main.py` | FastAPI gateway/proxy. Saat ini meneruskan request ke Backend AI. Cocok untuk auth, logging, rate limit, dan API gateway logic. |
| Backend AI | `backend/app/main.py` | Flask AI engine. Menjalankan recommender wisata, chatbot/RAG, penginapan, persona, dan behaviour service. |

Alur request utama:

```text
User di Frontend
  -> Next.js API rewrite / frontend service
  -> Backend Core FastAPI (default port 8001)
  -> Backend AI Flask (default port 5000)
  -> Service AI + dataset CSV/JSON + model/rules
  -> Response JSON kembali ke UI
```

Catatan penting:

- Scoring AI utama berada di Backend AI, bukan Frontend.
- Backend Core saat ini hanya proxy. Jangan taruh logic recommender berat di gateway.
- Frontend boleh mapping response untuk tampilan, tapi tidak boleh menghitung ranking utama.
- LLM boleh membantu parsing intent dan membuat narasi, tetapi fakta utama tetap dari dataset dan perhitungan Python.

---

## 2. Server Lokal dan Port

| Service | Default Command | Port | Catatan |
|---|---|---:|---|
| Backend AI Flask | `.\Scripts\restart_backend_ai_5000.ps1` | 5000 | Script ini menjalankan `backend/app/main.py`. |
| Backend Core FastAPI | `cd backend_core` lalu `uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload` | 8001 | `next.config.ts` default proxy ke `127.0.0.1:8001`. |
| Frontend Next.js | `cd frontend` lalu `npm run dev` | 3000 | Rewrites `/api/:path*` ke Backend Core. |

Environment penting:

| Env | Dipakai Oleh | Fungsi |
|---|---|---|
| `AI_ENGINE_URL` | `backend_core/app/main.py` | URL Backend AI. Default `http://127.0.0.1:5000`. |
| `MUTERBANDUNG_DATASET_PATH` | `backend/app/main.py`, `recommender.py` | Override dataset wisata runtime. |
| `MUTERBANDUNG_DB_PATH` | `backend/app/main.py`, `recommender.py` | Alias lama untuk override dataset wisata. |
| `MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM` | `chatbot_service.py`, `llm_extractor.py` | Jika `true/1/yes/on`, online LLM boleh dipanggil. Jika off, sistem fallback lokal. |
| `CLOUDFLARE_ACCOUNT_ID` | `llm_extractor.py`, `chatbot_service.py` | Credential Cloudflare Workers AI. |
| `CLOUDFLARE_API_TOKEN` | `llm_extractor.py`, `chatbot_service.py` | Credential Cloudflare Workers AI. |
| `OPENROUTER_API_KEY` | `llm_extractor.py`, `chatbot_service.py` | Credential OpenRouter fallback. |
| `OPENROUTER_MODEL` | `llm_extractor.py`, `chatbot_service.py` | Override model OpenRouter. Default `meta-llama/llama-3.1-8b-instruct`. |

Catatan audit:

- `.env.example` saat ini belum lengkap untuk semua env di atas. Sebaiknya nanti diperbarui.
- Jangan push API key asli. Jika ada file helper yang menyimpan credential-like value, pindahkan ke `.env`.

---

## 3. Dataset Runtime

Sistem saat ini masih memakai file-based database berupa CSV/JSON. Belum memakai PostgreSQL/MySQL.

| Dataset | Path | Status Saat Audit | Peran |
|---|---|---:|---|
| Wisata runtime | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_WISATA_CLEANED.csv` | 587 rows, 89 columns | Database utama AI Planner wisata. |
| Penginapan runtime | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_PENGINAPAN_ONLY.csv` | 547 rows, 89 columns | Database penginapan untuk endpoint `/api/penginapan`. |
| Landmark alias | `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/landmark_aliases.csv` | 13 rows, 5 columns | Membantu lokasi seperti Jatinangor, Lembang, Ciwidey, Bandung Utara. |
| Persona rules | `MUTERBANDUNG_CORE_SYSTEM/1_Dataset_Runtime/Persona_Home/PERSONA_HOME_RULES_2026-06-13.json` | Ada | Fallback rules untuk persona homepage. |
| Oleh-oleh runtime | belum aktif di backend branch ini | Tidak ditemukan sebagai curated runtime service | Jangan klaim fitur oleh-oleh backend aktif sebelum service/dataset final dibuat. |

Kolom penting wisata/penginapan:

```text
location_id, location_name, category, multi_labels,
avg_sentimen_skor, total_ulasan, sentimen_label_lokasi,
latitude, longitude, price_min, price_max,
jam_buka, jam_tutup, estimasi_durasi_menit,
subcategory, tags_sintetis, jam_buka_weekday,
jam_tutup_weekday, jam_buka_weekend, jam_tutup_weekend
```

Aturan dataset:

- Jangan langsung edit raw scrape untuk runtime.
- Jika dataset baru dibuat, simpan sebagai versi baru dan update path/env secara eksplisit.
- Untuk penginapan, `latitude` dan `longitude` lebih penting daripada harga. Data tanpa koordinat sebaiknya tidak masuk rekomendasi jarak.
- Untuk wisata, lokasi query harus diuji dengan `landmark_aliases.csv`, bukan hanya semantic text.

---

## 4. Backend AI: File dan Tanggung Jawab

| File | Fungsi | Boleh Diubah Untuk |
|---|---|---|
| `backend/app/main.py` | Router Flask dan orchestrator API. | Tambah endpoint, rapikan route order, validasi payload, metadata response. |
| `backend/app/services/recommender.py` | Core recommender wisata. | Scoring, filter, lokasi, fasilitas, fallback, explanation backend. |
| `backend/app/services/llm_extractor.py` | LLM intent parser. Cloudflare layer 1, OpenRouter layer 2. | Parsing query natural ke kategori, budget, lokasi, gratis, ramah anak. |
| `backend/app/services/chatbot_service.py` | Chatbot Cepot/RAG. | Guardrail context, fallback, online LLM, evidence based response. |
| `backend/app/services/llm_evidence_pack.py` | Membungkus hasil recommender menjadi evidence pack. | Field bukti untuk LLM dan validator. |
| `backend/app/services/llm_guard.py` | Prompt guard dan validator output LLM. | Anti-halusinasi, validasi selected candidates, fact claims. |
| `backend/app/services/penginapan_service.py` | Service penginapan jarak + rating/sentiment. | Distance scoring, filter tipe, response hotel. |
| `backend/app/services/persona_service.py` | Persona homepage. KMeans + rules fallback. | Personalisasi beranda, bukan planner/search. |
| `backend/app/services/behaviour_service.py` | Behaviour next-category. LSTM + Markov fallback. | Saran kategori berikutnya, bukan planner/search. |

---

## 5. Endpoint Backend AI

### 5.1 `POST /api/recommend`

Fungsi: rekomendasi wisata utama.

Input umum:

```json
{
  "query": "wisata edukasi di jatinangor",
  "categories": ["Edukasi"],
  "max_price": 100000,
  "min_rating": 4.0,
  "free_only": false,
  "open_now": false,
  "day_type": "weekday",
  "open_at_hour": 10,
  "user_lat": -6.9147,
  "user_lon": 107.6098,
  "max_distance_km": 30,
  "sort_by": "balanced",
  "top_k": 5
}
```

Prioritas filter:

1. Manual filter dari frontend/user.
2. LLM intent parser, hanya jika tidak ada kategori manual.
3. Lexical/heuristic logic di recommender.
4. Fallback relaxation jika filter otomatis terlalu sempit.

Output utama:

```json
{
  "status": "success",
  "query": "...",
  "ai_intents": {},
  "manual_filters": {},
  "implicit_filters": {},
  "location_context": {},
  "realworld_filters": {},
  "database_source": "...",
  "recommendations": [],
  "llm_evidence_pack": {},
  "llm_prompt_guard": {},
  "api_schema_version": "muterbandung.api.recommend.v1",
  "data_version": "...",
  "request_id": "...",
  "generated_at": "..."
}
```

Item di `recommendations` berisi field penting:

```text
rank, location_id, location_name, category, multi_labels,
label_taxonomy, realworld_flags, final_score, distance_km,
distance_label, media, score_breakdown, sentiment_score,
adjusted_sentiment_score, sentiment_model_source,
sentiment_available, review_confidence_label,
info_praktis, alasan
```

Catatan frontend:

- Backend mengembalikan `recommendations`, bukan `destinations`.
- `frontend/types/api.ts` masih mendefinisikan `destinations` dan `packages`. Ini perlu disinkronkan.
- `ExplorePageContent.tsx` sudah mencoba fallback mapping dari `data`, `recommendations`, atau `destinations`, tetapi type contract masih perlu diperbaiki.

---

### 5.2 `POST /api/chat`

Fungsi: chatbot Cepot berbasis evidence.

Input:

```json
{
  "message": "Saya ingin wisata alam murah dekat Lembang",
  "top_k": 5
}
```

Output penting:

```text
answer, recommendations, llm_output, llm_validation,
metadata.llm_used, metadata.fallback_used, metadata.parser_source,
llm_evidence_pack
```

Aturan:

- Query di luar konteks wisata diblok oleh guardrail lokal.
- Jika online LLM off atau gagal, sistem memakai fallback lokal.
- Frontend jangan menampilkan error merah untuk out-of-context. Itu fitur safety, bukan crash.

---

### 5.3 `GET /api/penginapan`

Fungsi: mengambil penginapan, idealnya setelah user memilih destinasi wisata.

Query params backend:

```text
limit
page
sentimentFilter
category
lat
lon
```

Contoh:

```text
/api/penginapan?limit=10&page=1&lat=-6.9147&lon=107.6098&category=hotel
```

Output:

```json
{
  "status": "success",
  "message": "Penginapan retrieved successfully",
  "data": [],
  "meta": {
    "total": 0,
    "page": 1,
    "limit": 10,
    "total_pages": 0
  }
}
```

Catatan audit:

- `frontend/services/penginapan.ts` mengirim param `sentiment`, sedangkan backend membaca `sentimentFilter`.
- Ini perlu disamakan. Pilih salah satu nama, lalu update frontend dan backend.
- Scoring penginapan saat ini: 70% jarak + 30% rating jika `lat/lon` dikirim.

---

### 5.4 `POST /api/persona/home`

Fungsi: memberi persona untuk homepage/rekomendasi beranda.

Input:

```json
{
  "favorite_place_labels": ["alam", "keluarga"],
  "activity_labels": ["santai"],
  "target_visitor_labels": ["anak"],
  "mood_labels": ["tenang"],
  "free_only": false
}
```

Output:

```json
{
  "status": "success",
  "persona": {
    "persona_id": "family_planner",
    "persona_name": "...",
    "persona_source": "ml_kmeans_clustering",
    "persona_confidence": 0.85,
    "home_boost_labels": [],
    "home_filter_flags": {},
    "do_not_apply_to_search": true,
    "do_not_apply_to_planner": true
  },
  "metadata": {
    "model_used": true,
    "fallback_used": false
  }
}
```

Aturan:

- Persona hanya untuk homepage atau section "Untuk Kamu".
- Persona tidak boleh mengalahkan query eksplisit user.
- Persona tidak boleh mengubah hasil AI Planner secara diam-diam.

---

### 5.5 `POST /api/behaviour/next`

Fungsi: memberi saran kategori berikutnya berdasarkan riwayat interaksi.

Input:

```json
{
  "current_category": "Alam",
  "session_categories": ["Alam", "Kuliner"]
}
```

Output:

```json
{
  "status": "success",
  "next_category_predictions": [
    { "category": "Oleh-oleh", "score": 0.42 }
  ],
  "metadata": {
    "model_source": "markov_order1_baseline",
    "fallback_used": true,
    "applies_to": "supporting_recommendation_only",
    "do_not_apply_to_search": true,
    "do_not_apply_to_planner": true
  }
}
```

Aturan:

- Behaviour adalah background intelligence.
- Dipakai untuk CTA atau rekomendasi pendukung, bukan search utama.
- Membutuhkan event/session history agar hasilnya masuk akal.

---

### 5.6 `POST /api/llm/validate`

Fungsi: validasi output LLM terhadap evidence pack.

Input:

```json
{
  "evidence_pack": {},
  "llm_output": {}
}
```

Output:

```text
valid, errors, warnings, sanitized_output, request metadata
```

Gunakan endpoint ini untuk QA saat developer mengubah prompt/RAG.

---

## 6. LLM, Guardrail, dan Failover

Ada dua jenis penggunaan LLM:

1. Intent parser di `llm_extractor.py`.
2. Chat/RAG explanation di `chatbot_service.py`.

Keduanya dikontrol oleh:

```text
MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM
```

Jika env ini tidak aktif, LLM online tidak dipanggil.

Flow LLM online:

```text
Cloudflare Workers AI
  -> jika gagal
OpenRouter
  -> jika gagal
local fallback
```

Aturan anti-halusinasi:

- LLM tidak boleh membuat destinasi baru.
- LLM tidak boleh mengarang harga, jarak, rating, atau jam buka.
- LLM hanya boleh menjelaskan data dari `llm_evidence_pack`.
- Output LLM divalidasi oleh `llm_guard.py`.

---

## 7. Frontend Integration Notes

### 7.1 API base URL

`frontend/next.config.ts`:

```ts
destination: `${process.env.NEXT_PUBLIC_API_URL || process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8001'}/api/:path*`
```

`frontend/services/api.ts`:

```ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
```

Makna praktis:

- Jika `NEXT_PUBLIC_API_URL` kosong, request frontend ke `/api/...` akan melewati Next.js rewrite.
- Default rewrite mengarah ke Backend Core port `8001`.
- Jika frontend ingin direct call, isi `NEXT_PUBLIC_API_URL`.

### 7.2 Recommendation mapping

Backend AI mengembalikan:

```text
recommendations[]
```

Frontend Explore saat ini mapping:

```ts
const rawRecommendations =
  (res as any).data ||
  (res as any).recommendations ||
  res.destinations ||
  [];
```

Pekerjaan frontend yang disarankan:

- Update `frontend/types/api.ts` agar sesuai response backend.
- Jadikan `recommendations` sebagai field utama.
- Pertahankan fallback mapping sementara jika masih ada response lama.

### 7.3 Penginapan mapping

Frontend penginapan memakai:

```text
frontend/services/penginapan.ts
frontend/types/penginapan.ts
frontend/components/sections/planner/AccommodationPageContent.tsx
```

Data penginapan akan lebih relevan jika frontend mengirim koordinat destinasi:

```text
lat
lon
```

Jika `lat/lon` tidak dikirim, backend fallback sorting ke rating.

---

## 8. Known Issues yang Harus Diketahui Developer

| Prioritas | Area | Masalah | Dampak | Saran Fix |
|---|---|---|---|---|
| P0 | `backend/app/main.py` | Route `/api/persona/home` dan `/api/behaviour/next` dideklarasikan setelah `if __name__ == '__main__': app.run(...)`. | Jika Flask dijalankan langsung sebagai script, route ini bisa tidak terdaftar karena `app.run` memblokir. | Pindahkan block `if __name__ == '__main__'` ke paling bawah file setelah semua route. |
| P0 | Security | Ada file helper `backend/enrich_location_llm.py` yang terlihat menyimpan credential-like values. | Risiko secret ikut push. | Pindahkan semua credential ke `.env`, hapus hardcoded token dari file. |
| P1 | Frontend types | `frontend/types/api.ts` masih memakai `destinations/packages`, sedangkan backend mengirim `recommendations`. | Type mismatch dan potensi bug saat refactor. | Update type contract sesuai backend response. |
| P1 | Penginapan param | Frontend mengirim `sentiment`, backend membaca `sentimentFilter`. | Filter sentiment penginapan tidak jalan. | Samakan nama param. |
| P1 | `.env.example` | Belum mencantumkan semua env LLM/gateway. | Developer baru sulit menjalankan sistem lengkap. | Tambah `AI_ENGINE_URL`, `NEXT_PUBLIC_API_URL`, `MUTERBANDUNG_ENABLE_ONLINE_CHAT_LLM`, `CLOUDFLARE_*`, `OPENROUTER_*`. |
| P1 | Location-aware search | Query lokasi seperti Jatinangor harus diuji lebih ketat. | Hasil bisa relevan kategori tetapi melenceng area. | Perkuat scoring/radius dari `landmark_aliases.csv` dan audit query lokasi. |
| P2 | Oleh-oleh | Service/backend runtime oleh-oleh tidak ditemukan di branch ini. | Jangan klaim fitur oleh-oleh aktif di backend. | Buat service dan dataset curated dulu jika ingin diaktifkan. |
| P2 | Backend Core | Gateway masih proxy umum. | Belum ada auth/logging/rate limit. | Tambah middleware sesuai kebutuhan production. |

---

## 9. File yang Boleh Diolah per Tim

### Backend AI

Fokus:

- `backend/app/main.py`
- `backend/app/services/recommender.py`
- `backend/app/services/llm_extractor.py`
- `backend/app/services/chatbot_service.py`
- `backend/app/services/llm_evidence_pack.py`
- `backend/app/services/llm_guard.py`
- `backend/app/services/penginapan_service.py`
- `backend/app/services/persona_service.py`
- `backend/app/services/behaviour_service.py`
- `.env.example`
- `backend/requirements.txt`

Jangan langsung ubah:

- Raw scrape JSON/CSV.
- Model `.pkl` atau `.keras`.
- Dataset runtime tanpa membuat versi/snapshot.

### Backend Core

Fokus:

- `backend_core/app/main.py`
- `backend_core/requirements.txt`

Pekerjaan berikutnya:

- Auth/session.
- Request logging.
- Rate limit.
- Stable error envelope.
- Proxy timeout policy.
- Forward metadata dari Backend AI ke Frontend.

### Frontend

Fokus:

- `frontend/services/api.ts`
- `frontend/services/recommendations.ts`
- `frontend/services/penginapan.ts`
- `frontend/types/api.ts`
- `frontend/types/penginapan.ts`
- `frontend/components/sections/explore/ExplorePageContent.tsx`
- `frontend/components/sections/planner/AccommodationPageContent.tsx`
- `frontend/components/ui/ChatbotWidget.tsx`

Pekerjaan berikutnya:

- Sinkron type response `/api/recommend`.
- Tampilkan loading/fallback state dengan benar.
- Kirim koordinat destinasi ke `/api/penginapan`.
- Tampilkan metadata confidence/fallback secara halus.
- Jangan hitung ranking utama di UI.

### Dataset / AI Engineer

Fokus:

- `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/`
- `MUTERBANDUNG_CORE_SYSTEM/1_Dataset_Runtime/Persona_Home/`
- `Models/`
- `Behaviour_Workspace/`
- `Penginapan_Workspace/`

Aturan:

- Dataset runtime harus punya versi.
- Perubahan besar harus ada audit file.
- Raw data jangan langsung dipakai aplikasi.
- Lat/lon wajib untuk fitur jarak.

---

## 10. Checklist Sebelum Push

Backend AI:

- [ ] `backend/app/main.py` route order aman.
- [ ] Tidak ada API key hardcoded.
- [ ] `/api/recommend` jalan dengan query umum.
- [ ] `/api/chat` jalan dengan fallback saat LLM online off.
- [ ] `/api/penginapan` jalan dengan `lat/lon`.
- [ ] `/api/persona/home` dan `/api/behaviour/next` benar-benar terdaftar saat server start.

Frontend:

- [ ] `frontend/types/api.ts` sesuai response backend.
- [ ] Explore membaca `recommendations`.
- [ ] Penginapan memakai param yang sama dengan backend.
- [ ] `NEXT_PUBLIC_API_URL` / rewrite sudah jelas.

Data:

- [ ] Dataset wisata runtime ada.
- [ ] Dataset penginapan runtime ada.
- [ ] `landmark_aliases.csv` ada.
- [ ] Dataset yang belum aktif tidak diklaim aktif.

Runtime lokal:

- [ ] Flask Backend AI port 5000 hidup.
- [ ] FastAPI Backend Core port 8001 hidup.
- [ ] Frontend port 3000 hidup.

---

## 11. Rekomendasi Urutan Kerja Developer Setelah Dokumen Ini

Urutan paling aman:

1. Bereskan route order di `backend/app/main.py`.
2. Bersihkan secret hardcoded dari helper script.
3. Sinkronkan `frontend/types/api.ts` dengan response `/api/recommend`.
4. Sinkronkan param sentiment penginapan.
5. Lengkapi `.env.example`.
6. Uji tiga server lokal.
7. Audit 10 query wisata lokasi:
   - `wisata edukasi di jatinangor`
   - `wisata alam murah lembang`
   - `kuliner malam bandung`
   - `wisata keluarga ciwidey`
   - `curug murah bandung`
   - `wisata gratis dekat alun alun`
   - `museum dekat gedung sate`
   - `wisata tidak terlalu ramai`
   - `wisata ada mushola dan parkir`
   - `hotel dekat destinasi yang dipilih`
8. Setelah stabil, baru aktifkan fitur pendukung seperti oleh-oleh atau behaviour UI.

---

## 12. Prinsip Utama untuk AI Agent

Jika AI agent lain melanjutkan pekerjaan ini, ikuti aturan ini:

1. Jangan mengubah ranking utama berdasarkan persona/behaviour.
2. Jangan memindahkan scoring AI ke frontend.
3. Jangan mengklaim oleh-oleh aktif sebelum service dan dataset runtime ada.
4. Jangan mengarang field response. Cek `recommender.py` dan `main.py`.
5. Jangan overwrite dataset runtime tanpa snapshot.
6. Jangan push secret/API key.
7. Jika LLM gagal, aplikasi harus tetap jalan.
8. Jika query user eksplisit, hormati query itu lebih tinggi dari model background.

Kesimpulan sistem saat ini:

```text
AI Planner = core search/recommender wisata.
Chatbot = RAG/explanation layer.
Penginapan = phase 2 setelah destinasi dipilih.
Persona = homepage personalization only.
Behaviour = next-suggestion/supporting layer only.
Oleh-oleh = belum aktif di backend branch ini.
```
