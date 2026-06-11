# Full System Audit Stage 3 - Backend, API Contract, Scoring, Filters, and Frontend Surface

## Scope

Tahap 3 mengaudit jalur runtime:

```text
Frontend -> Flask API -> MuterBandungRecommender -> Evidence Pack -> LLM Guard
```

Fokusnya adalah kontrak API, filtering, scoring, behavior edge case, surface frontend, dan kesiapan backend sebelum integrasi LLM provider.

## Files Reviewed

- `Scripts/app.py`
- `Scripts/recommender.py`
- `Scripts/llm_evidence_pack.py`
- `Scripts/llm_guard.py`
- `Scripts/static/script.js`
- `Scripts/static/style.css`
- `Scripts/templates/index.html`

## Syntax Verification

```powershell
python -B -m py_compile Scripts\app.py Scripts\recommender.py Scripts\llm_evidence_pack.py Scripts\llm_guard.py
node --check Scripts\static\script.js
```

Result:

```text
PASS
```

## Runtime API Verification

Live API:

```text
POST http://127.0.0.1:5000/api/recommend
```

Skenario yang dicek:

| Scenario | Result |
|---|---|
| `wisata alam sejuk` | 200, 5 rekomendasi, evidence + guard tersedia |
| `tempat melihat aurora` | 200, no strong match aktif |
| `tempat wisata dekat saya` tanpa lokasi | 200, no strong match "Lokasi diperlukan" |
| `museum dekat Gedung Sate` | 200, landmark context aktif |
| `wisata di bawah 50000` | 200, implicit max_price 50000 |
| `museum terdekat radius 5 km` + lokasi user | 200, radius dan nearest aktif |
| `/api/llm/validate` valid output | 200, valid true |
| `/api/llm/validate` fake destination id | 422, valid false |

## Backend Strengths

### 1. Arsitektur hybrid sudah benar

`Scripts/app.py` menjalankan:

```text
engine.recommend(...)
-> build_llm_evidence_pack(results)
-> build_llm_prompt_guard(evidence_pack)
```

Artinya LLM tidak menentukan kandidat awal. Backend tetap menjadi penentu kandidat dan evidence.

### 2. Dataset aktif difilter sebelum scoring

`MuterBandungRecommender` otomatis mengarah ke:

```text
Dataset/3_Curated/DATABASE_WISATA_LABELED_V2_REVIEWED.csv
```

Lalu hanya memakai:

```text
display_status = active_candidate
curation_action != remove
```

Runtime memuat:

```text
213 destinasi aktif dari 234 baris
```

### 3. Filtering deterministik cukup matang

Filter yang sudah ada:

- kategori/intent;
- harga maksimum;
- gratis;
- rating minimum;
- jam buka;
- night-only;
- shopping subtype;
- fasilitas terverifikasi;
- lokasi user/landmark;
- radius dan mode ranking nearest/balanced/relevance.

### 4. No strong match sudah melindungi query mustahil

Query seperti:

```text
aurora
pantai
gurun pasir
ski/salju
curug malam
glamping gratis
```

tidak dipaksa menghasilkan destinasi palsu.

### 5. Sentiment metadata sudah netral

API mengirim:

```text
sentiment_score
sentiment_model_source
sentiment_model_version
sentiment_available
```

Tidak lagi bergantung pada nama field misleading `sentimen_indobert`.

### 6. Media metadata konservatif

Frontend hanya menampilkan media jika:

```text
media.available === true
```

Backend juga hanya menerima URL yang diawali `http://` atau `https://`.

### 7. Frontend sudah melakukan HTML escaping

`Scripts/static/script.js` memakai `escapeHtml(...)` untuk konten yang masuk ke `innerHTML`. Ini mengurangi risiko XSS dari field dataset/API.

## Backend and API Weaknesses

### Finding 1 - Input validation belum formal

Severity: **High before public API / LLM provider**

`/api/recommend` menerima JSON silent:

```python
data = request.get_json(silent=True) or {}
```

Dampak yang ditemukan:

```text
malformed JSON -> dianggap request kosong -> tetap menghasilkan rekomendasi
```

Seharusnya malformed JSON mendapat `400 Bad Request`.

### Finding 2 - Boolean string bisa salah terbaca

Severity: **High for external clients**

Payload:

```json
{"query": "wisata alam", "free_only": "false"}
```

Terbaca sebagai:

```text
free_only: true
```

Penyebab:

```python
free_only = bool(data.get('free_only', False))
```

Di Python, string non-empty `"false"` bernilai `True`.

### Finding 3 - `open_at_hour` non-string bisa membuat 500

Severity: **High**

Payload:

```json
{"query": "wisata malam", "open_at_hour": 20}
```

Menghasilkan:

```text
500 Internal Server Error
```

Penyebab: `open_at_hour.strip()` dipanggil tanpa validasi tipe.

### Finding 4 - Numeric range tidak divalidasi

Severity: **Medium**

Contoh:

```json
{"max_price": -1}
{"min_rating": 99}
```

Saat ini tetap diproses dan menghasilkan 0 rekomendasi tanpa pesan validasi. Untuk UI mungkin tidak masalah karena form punya batas, tetapi API eksternal/LLM tool bisa mengirim nilai aneh.

### Finding 5 - Query sangat panjang tidak dibatasi

Severity: **Medium-High before LLM**

Query 2000 karakter tetap diproses. Jika nanti query/evidence dikirim ke LLM, ini dapat berdampak pada:

- latency;
- token cost;
- prompt quality;
- potensi prompt injection/noise.

### Finding 6 - `top_k` dari request diabaikan

Severity: **Low-Medium**

Frontend memang butuh 5 hasil, tetapi API mengunci:

```python
top_k=5
```

Payload `top_k` tidak dipakai. Ini baik untuk konsistensi demo, tetapi perlu didokumentasikan atau divalidasi agar client tidak salah asumsi.

### Finding 7 - Radius filter mempertahankan kandidat dengan jarak NaN

Severity: **Medium**

Pada `_attach_distance_columns`, saat radius aktif:

```python
enriched['__distance_km'].isna() | (__distance_km <= radius)
```

Kandidat dengan koordinat tidak terverifikasi tetap lolos radius karena jaraknya `NaN`. Ini konservatif agar data tidak hilang, tetapi untuk query "radius 5 km" bisa membingungkan karena ada kandidat yang jaraknya tidak dihitung namun masih berada di candidate pool.

Rekomendasi: jika user explicit radius, kandidat tanpa jarak terverifikasi sebaiknya:

- dikeluarkan, atau
- tetap masuk hanya jika diberi warning eksplisit dan tidak berada top result.

### Finding 8 - API response belum punya metadata versi

Severity: **Medium**

Response belum membawa:

```text
api_schema_version
data_version
model_version
request_id
generated_at
```

Ini penting untuk debugging LLM dan audit akademik.

### Finding 9 - Frontend wording bisa misleading

Severity: **Low-Medium**

UI memakai istilah:

```text
AI Recommender
AI sedang menganalisis
Mengapa AI merekomendasikan ini?
```

Saat ini "AI" lebih tepat dimaknai sebagai semantic recommender, bukan LLM reasoning. Untuk sidang atau laporan, perlu dijelaskan bahwa rekomendasi utama tetap deterministic/semantic backend, bukan LLM bebas.

## Scoring Audit

Scoring saat ada query:

```text
similarity: 35%
sentiment: 35%
rating: 20%
confidence: 10%
```

Tanpa query:

```text
sentiment: 55%
rating: 30%
confidence: 15%
```

Location-aware mode:

```text
balanced: relevance 75%, distance 25%
balanced + nearby query: relevance 55%, distance 45%
nearest: relevance 35%, distance 65%
```

Verdict:

```text
Good for prototype and explainable enough.
```

Catatan: karena sentiment berbobot besar, ketersediaan dan provenance sentiment sudah benar-benar penting. Perbaikan metadata sentiment sebelumnya adalah keputusan tepat.

## Frontend Surface

Frontend sudah mendukung:

- query natural language;
- kategori checkbox;
- max price;
- free only;
- min rating;
- open now;
- day type/open time;
- ranking mode;
- max radius;
- geolocation user;
- media image/link;
- sentiment display;
- score breakdown.

Keterbatasan:

- hanya menampilkan jam weekday pada card;
- belum menampilkan warning evidence/global limitations;
- belum menampilkan status verifikasi real-world;
- belum ada panel "data caveat" untuk LLM/readiness;
- belum menampilkan no-strong-match sebagai status khusus selain error-like empty state.

## Stage 3 Verdict

```text
BACKEND RECOMMENDER: STRONG FOR PROTOTYPE
API CONTRACT: FUNCTIONAL BUT NEEDS SCHEMA VALIDATION
SCORING/FILTERING: GOOD AND DEFENSIVE
LLM-SAFE SURFACE: PARTIAL, NEEDS STRICTER INPUT GOVERNANCE
FRONTEND: USABLE, BUT SHOULD SHOW VERIFICATION CAVEATS
```

## Recommended Fixes Before LLM Provider Integration

1. Tambahkan schema validation untuk `/api/recommend`.
2. Tolak malformed JSON dengan 400.
3. Buat parser boolean eksplisit:

```text
true/false, 1/0, yes/no
```

4. Validasi `open_at_hour` sebagai format `HH:MM`.
5. Batasi panjang query, misalnya 300-500 karakter.
6. Validasi range:

```text
max_price >= 0
1 <= min_rating <= 5
0 < max_distance_km <= reasonable limit
```

7. Tambahkan response metadata:

```json
{
  "api_schema_version": "muterbandung.recommend.v1",
  "data_version": "DATABASE_WISATA_LABELED_V2_REVIEWED.csv",
  "request_id": "...",
  "generated_at": "..."
}
```

8. Jika radius eksplisit, jangan diam-diam mempertahankan kandidat `distance_km = null` tanpa warning.
9. Frontend perlu menampilkan:

```text
data limitations
realworld verification flags
weekday + weekend hours
```

## Next Stage

Tahap 4 harus fokus ke:

- unit tests;
- QC suite;
- groundtruth evaluator;
- LLM evidence pack;
- prompt guard;
- validator coverage;
- notebook dokumentasi.
