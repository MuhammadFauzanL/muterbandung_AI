# Instruksi Wiring Backend ke Hugging Face Model Persona + Behaviour

Tanggal: 2026-06-19

Repo Hugging Face model:

```text
fauzanlubada/muterbandung-ai-models
```

Status upload:

```text
persona/persona_kmeans.pkl
persona/persona_scaler.pkl
behaviour/markov_order1_baseline.pkl
behaviour/behaviour_lstm_muterbandung_v1.keras
behaviour/category_encoder_v1.pkl
behaviour/time_encoder_v1.pkl
behaviour/behaviour_lstm_artifacts_v1.pkl
```

Tujuan dokumen ini adalah memberi instruksi cara menghubungkan backend MuterBandung agar `persona_service.py` dan `behaviour_service.py` bisa memakai model dari Hugging Face Hub.

## Konsep yang Dipakai

Hugging Face dipakai sebagai **model artifact storage / model registry**.

Backend MuterBandung tetap menjalankan inference sendiri:

```text
Frontend
  -> Backend MuterBandung
      -> persona_service.py
          -> download model dari Hugging Face jika file lokal tidak ada
      -> behaviour_service.py
          -> download model dari Hugging Face jika file lokal tidak ada
      -> recommender.py
          -> memakai persona/behaviour signal
```

Jadi Hugging Face bukan menggantikan AI Planner. Hugging Face hanya menyimpan file model.

## Env Backend yang Dibutuhkan

Tambahkan ke env backend:

```env
HF_TOKEN=hf_TOKEN_READ_ONLY_BARU
MUTERBANDUNG_HF_REPO_ID=fauzanlubada/muterbandung-ai-models
MUTERBANDUNG_HF_REVISION=main
MUTERBANDUNG_ENABLE_HF_MODEL_DOWNLOAD=true
```

Catatan:

- Karena repo Hugging Face dibuat private, backend perlu `HF_TOKEN`.
- Untuk production, buat token baru yang **read-only**.
- Jangan pakai token upload lama untuk production.
- Jangan commit token ke git.

## Dependency Backend

Pastikan dependency ini ada:

```text
huggingface-hub
joblib
tensorflow
scikit-learn
```

Di `main_clean_worktree/backend/requirements.txt`, `huggingface-hub==0.36.0` sudah ada.

## File Baru yang Disarankan

Buat helper baru:

```text
main_clean_worktree/backend/app/services/hf_model_loader.py
```

Isi yang disarankan:

```python
from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import hf_hub_download


DEFAULT_REPO_ID = "fauzanlubada/muterbandung-ai-models"


def hf_model_download_enabled() -> bool:
    return os.getenv("MUTERBANDUNG_ENABLE_HF_MODEL_DOWNLOAD", "false").lower() in {
        "1",
        "true",
        "yes",
    }


def download_model_file(filename: str) -> Path | None:
    if not hf_model_download_enabled():
        return None

    repo_id = os.getenv("MUTERBANDUNG_HF_REPO_ID", DEFAULT_REPO_ID)
    revision = os.getenv("MUTERBANDUNG_HF_REVISION", "main")
    token = os.getenv("HF_TOKEN")

    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="model",
            revision=revision,
            token=token,
        )
        return Path(path)
    except Exception as exc:
        print(f"[HFModelLoader] Failed to download {filename}: {exc}")
        return None


def resolve_local_or_hf(local_path: Path, hf_filename: str) -> Path:
    if local_path.exists():
        return local_path

    hf_path = download_model_file(hf_filename)
    if hf_path and hf_path.exists():
        return hf_path

    return local_path
```

## Update `persona_service.py`

File:

```text
main_clean_worktree/backend/app/services/persona_service.py
```

Tambahkan import:

```python
from app.services.hf_model_loader import resolve_local_or_hf
```

Setelah definisi path lokal:

```python
KMEANS_PATH = _resolve_path("MUTERBANDUNG_PERSONA_KMEANS_PATH", "Models", "persona_kmeans.pkl")
SCALER_PATH = _resolve_path("MUTERBANDUNG_PERSONA_SCALER_PATH", "Models", "persona_scaler.pkl")
```

Tambahkan:

```python
KMEANS_PATH = resolve_local_or_hf(KMEANS_PATH, "persona/persona_kmeans.pkl")
SCALER_PATH = resolve_local_or_hf(SCALER_PATH, "persona/persona_scaler.pkl")
```

Hasilnya:

```python
KMEANS_PATH = _resolve_path("MUTERBANDUNG_PERSONA_KMEANS_PATH", "Models", "persona_kmeans.pkl")
SCALER_PATH = _resolve_path("MUTERBANDUNG_PERSONA_SCALER_PATH", "Models", "persona_scaler.pkl")

KMEANS_PATH = resolve_local_or_hf(KMEANS_PATH, "persona/persona_kmeans.pkl")
SCALER_PATH = resolve_local_or_hf(SCALER_PATH, "persona/persona_scaler.pkl")
```

Dengan pola ini:

- Jika model lokal ada, backend memakai model lokal.
- Jika model lokal tidak ada, backend download dari Hugging Face.
- Jika download gagal, service tetap fallback ke rules.

## Update `behaviour_service.py`

File:

```text
main_clean_worktree/backend/app/services/behaviour_service.py
```

Tambahkan import:

```python
from app.services.hf_model_loader import resolve_local_or_hf
```

Setelah definisi path lokal:

```python
MARKOV_PATH = _first_existing_path(...)
LSTM_PATH = _first_existing_path(...)
CAT_ENCODER_PATH = _first_existing_path(...)
```

Tambahkan:

```python
MARKOV_PATH = resolve_local_or_hf(MARKOV_PATH, "behaviour/markov_order1_baseline.pkl")
LSTM_PATH = resolve_local_or_hf(LSTM_PATH, "behaviour/behaviour_lstm_muterbandung_v1.keras")
CAT_ENCODER_PATH = resolve_local_or_hf(CAT_ENCODER_PATH, "behaviour/category_encoder_v1.pkl")
```

Jika nanti `time_encoder_v1.pkl` dipakai, tambahkan juga:

```python
TIME_ENCODER_PATH = _first_existing_path(
    "MUTERBANDUNG_BEHAVIOUR_TIME_ENCODER_PATH",
    ("MUTERBANDUNG_CORE_SYSTEM", "2_Models", "LSTM_Engine", "time_encoder_v1.pkl"),
)
TIME_ENCODER_PATH = resolve_local_or_hf(TIME_ENCODER_PATH, "behaviour/time_encoder_v1.pkl")
```

Untuk artifact metadata:

```python
ARTIFACTS_PATH = _first_existing_path(
    "MUTERBANDUNG_BEHAVIOUR_ARTIFACTS_PATH",
    ("MUTERBANDUNG_CORE_SYSTEM", "2_Models", "LSTM_Engine", "behaviour_lstm_artifacts_v1.pkl"),
)
ARTIFACTS_PATH = resolve_local_or_hf(
    ARTIFACTS_PATH,
    "behaviour/behaviour_lstm_artifacts_v1.pkl",
)
```

Catatan:

- Service sekarang minimal butuh Markov, LSTM, dan category encoder.
- Time encoder dan artifacts belum wajib untuk inference service sekarang, tetapi baik untuk dokumentasi dan audit.

## Cara Memanggil Model dari Backend

Setelah wiring selesai, service dipakai seperti biasa.

Contoh persona:

```python
from app.services.persona_service import persona_service

result = persona_service.determine_home_persona({
    "favorite_place_labels": ["alam", "taman"],
    "activity_labels": ["foto", "jalan santai"],
    "target_visitor_labels": ["keluarga"],
    "mood_labels": ["tenang"],
    "free_only": True,
})

print(result)
```

Contoh behaviour:

```python
from app.services.behaviour_service import behaviour_service

result = behaviour_service.predict_next_category({
    "current_category": "Kuliner",
    "session_categories": ["Kuliner", "Belanja"],
})

print(result)
```

## Cara Memanggil dari Endpoint MuterBandung

Normalnya frontend tidak memanggil persona/behaviour langsung. Frontend memanggil endpoint AI:

```text
POST /recommendations/ai-planner
POST /recommendations/cepot-chat
```

Lalu backend:

1. `recommendations.py` menerima request.
2. `chatbot_service.py` atau `recommender.py` memproses query.
3. `recommender.py` memanggil persona/behaviour sebagai signal.
4. Output dikembalikan sebagai `recommendations`.

Jadi dari sisi aplikasi, tetap pakai endpoint yang sama.

## Test Manual Setelah Wiring

Masuk backend:

```bat
cd /d "D:\File\file\Fauzan Lubada\PIJAK\main_clean_worktree\backend"
```

Set env:

```bat
set HF_TOKEN=hf_TOKEN_READ_ONLY_BARU
set MUTERBANDUNG_HF_REPO_ID=fauzanlubada/muterbandung-ai-models
set MUTERBANDUNG_HF_REVISION=main
set MUTERBANDUNG_ENABLE_HF_MODEL_DOWNLOAD=true
```

Jalankan backend:

```bat
..\..\.venv_clean_verify\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Test Cepot:

```powershell
$body = @{ message = "aku mau wisata alam di Bandung"; top_k = 3 } | ConvertTo-Json -Compress
Invoke-WebRequest -UseBasicParsing -Method Post `
  -Uri "http://127.0.0.1:8001/recommendations/cepot-chat" `
  -ContentType "application/json" `
  -Body $body
```

Test AI Planner:

```powershell
$body = @{
  query = "wisata alam murah di Bandung"
  top_k = 5
  persona_context = @{
    favorite_place_labels = @("alam", "taman")
    activity_labels = @("jalan santai")
    target_visitor_labels = @("keluarga")
    mood_labels = @("tenang")
    free_only = $true
  }
  behaviour_context = @{
    current_category = "Kuliner"
    session_categories = @("Kuliner", "Belanja")
  }
} | ConvertTo-Json -Depth 5 -Compress

Invoke-WebRequest -UseBasicParsing -Method Post `
  -Uri "http://127.0.0.1:8001/recommendations/ai-planner" `
  -ContentType "application/json" `
  -Body $body
```

## Tanda Berhasil

Di log backend harus muncul kira-kira:

```text
[PersonaService] ML Models (KMeans & Scaler) loaded successfully!
[BehaviourService] Markov model loaded.
[BehaviourService] LSTM Deep Learning model loaded!
```

Jika model lokal tidak ada dan HF aktif, Hugging Face akan mengunduh file ke cache lokal, biasanya di:

```text
C:\Users\<user>\.cache\huggingface\hub
```

## Output yang Harus Dicek

Pada response AI Planner, cek `score_breakdown`:

```text
persona_model_used
persona_source
persona_applied
behaviour_model_used
behaviour_model_source
behaviour_applied
personalization_boost
personalization_applied
```

Jika nilai ini muncul dan bukan fallback kosong, berarti model signal sudah masuk.

## Failure Mode yang Wajar

### Repo private tapi token tidak ada

Gejala:

```text
401 Unauthorized
```

Solusi:

```env
HF_TOKEN=hf_read_only_token
```

### Repo id salah

Gejala:

```text
Repository Not Found
```

Solusi:

```env
MUTERBANDUNG_HF_REPO_ID=fauzanlubada/muterbandung-ai-models
```

### Download dimatikan

Gejala:

```text
ML Models not found. Will fallback to rules.
```

Solusi:

```env
MUTERBANDUNG_ENABLE_HF_MODEL_DOWNLOAD=true
```

### TensorFlow tidak tersedia

Gejala:

```text
Error loading LSTM model
```

Solusi:

```bat
pip install -r requirements.txt
```

atau pastikan dependency:

```text
tensorflow
tf-keras
```

## Rekomendasi Implementasi

Urutan paling aman:

1. Tambahkan `hf_model_loader.py`.
2. Update `persona_service.py`.
3. Update `behaviour_service.py`.
4. Test import service saja.
5. Test endpoint `cepot-chat`.
6. Test endpoint `ai-planner`.
7. Baru deploy ke server.

## Catatan Penting

Untuk production, token Hugging Face backend cukup read-only.

Jangan pakai token upload yang pernah muncul di chat. Token upload boleh dipakai sementara untuk eksperimen lokal, tetapi setelah selesai sebaiknya revoke dan ganti token baru.
