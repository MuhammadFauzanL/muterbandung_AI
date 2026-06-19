# AI Planner Main Integration Notes

Prepared in `main_clean_worktree` as an isolated main-branch staging area.

## Layers Added

- AI Planner core: `backend/app/services/recommender.py`
- Cepot chat: `backend/app/services/chatbot_service.py`
- LLM extraction/failover: `backend/app/services/llm_extractor.py`
- Evidence pack: `backend/app/services/llm_evidence_pack.py`
- Guard/validation: `backend/app/services/llm_guard.py`
- Persona model signal: `backend/app/services/persona_service.py`
- Behaviour model signal: `backend/app/services/behaviour_service.py`
- Penginapan support: `backend/app/services/penginapan_service.py`

## API Contract

- New AI Planner route: `POST /recommendations/ai-planner`
- New Cepot route: `POST /recommendations/cepot-chat`
- AI recommendations keep `recommendations[]`.
- Every recommendation can carry `score_breakdown`.
- Frontend accepts both:
  - `score_breakdown` from backend AI
  - `scoreBreakdown` from older frontend/data contracts

## Personalization Policy

- Persona and behaviour are score signals, not hardcoded ranking replacement.
- Persona applies to planner/search only when the KMeans persona model is used.
- Behaviour applies when LSTM or Markov model output is available.
- Rule/fallback-only persona is not applied to planner ranking.
- Empty behaviour fallback is not applied to planner ranking.

## Model/Data Files Included

- `Models/persona_kmeans.pkl`
- `Models/persona_scaler.pkl`
- `MUTERBANDUNG_CORE_SYSTEM/1_Dataset_Runtime/Persona_Home/PERSONA_HOME_RULES_2026-06-13.json`
- `MUTERBANDUNG_CORE_SYSTEM/2_Models/markov_order1_baseline.pkl`
- `MUTERBANDUNG_CORE_SYSTEM/2_Models/LSTM_Engine/category_encoder_v1.pkl`
- `MUTERBANDUNG_CORE_SYSTEM/2_Models/LSTM_Engine/behaviour_lstm_muterbandung_v1.keras`
- `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_PENGINAPAN_ONLY.csv`
- `ai_workspace/Wisata_Workspace/01_Dataset/3_Curated/DATABASE_PENGINAPAN_GALLERY.csv`

## Verification Performed

- Python syntax compile passed for added/changed backend AI files.
- `git diff --check` passed.
- Frontend lint/build was not run because `frontend/node_modules` is not installed in `main_clean_worktree`.
