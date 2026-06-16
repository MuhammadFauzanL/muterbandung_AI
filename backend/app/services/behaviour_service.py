import os

BASE_DIR = r'D:\File\file\Fauzan Lubada\PIJAK'
MODELS_DIR = os.path.join(BASE_DIR, 'Behaviour_Workspace')
MARKOV_PATH = os.path.join(MODELS_DIR, '03_Models', 'markov_order1_baseline.pkl')
LSTM_PATH = os.path.join(MODELS_DIR, 'lstm_v1_extracted', 'behaviour_lstm_muterbandung_v1.keras')
CAT_ENCODER_PATH = os.path.join(MODELS_DIR, 'lstm_v1_extracted', 'category_encoder_v1.pkl')

class BehaviourService:
    def __init__(self):
        self.markov_model = None
        self.lstm_model = None
        self.cat_encoder = None
        self._load_models()

    def _load_models(self):
        try:
            import pickle
            if os.path.exists(MARKOV_PATH):
                with open(MARKOV_PATH, 'rb') as f:
                    self.markov_model = pickle.load(f)
                print("[BehaviourService] Markov model loaded.")
        except Exception as e:
            print(f"[BehaviourService] Error loading Markov model: {e}")

        try:
            from tensorflow.keras.models import load_model
            import joblib
            if os.path.exists(LSTM_PATH) and os.path.exists(CAT_ENCODER_PATH):
                self.lstm_model = load_model(LSTM_PATH)
                self.cat_encoder = joblib.load(CAT_ENCODER_PATH)
                print("[BehaviourService] LSTM Deep Learning model loaded!")
            else:
                print("[BehaviourService] LSTM Model or Encoder not found.")
        except Exception as e:
            print(f"[BehaviourService] Error loading LSTM model: {e}")

    def _get_fallback_response(self, reason):
        return {
            "status": "success",
            "next_category_predictions": [],
            "metadata": {
                "model_source": "fallback_empty",
                "fallback_used": True,
                "fallback_reason": reason,
                "applies_to": "supporting_recommendation_only",
                "do_not_apply_to_search": True,
                "do_not_apply_to_planner": True
            }
        }

    def predict_next_category(self, payload):
        current_category = payload.get("current_category")
        session_categories = payload.get("session_categories", [])
        
        active_state = str(current_category).strip() if current_category else None
        if not active_state and session_categories:
            active_state = str(session_categories[-1]).strip()

        if not active_state:
            return self._get_fallback_response("No current or previous category provided")

        # 1. COBA MENGGUNAKAN DEEP LEARNING (LSTM) TERLEBIH DAHULU
        if self.lstm_model and self.cat_encoder and len(session_categories) > 0:
            try:
                import numpy as np
                # LSTM butuh sequence. Kita padding menjadi panjang tertentu (misal 5)
                seq_length = 5
                
                # Transform kategori teks ke angka
                encoded_seq = []
                for cat in session_categories[-seq_length:]:
                    try:
                        encoded_seq.append(self.cat_encoder.transform([[cat]])[0][0])
                    except:
                        encoded_seq.append(0) # Unknown category fallback
                
                # Padding sequence
                while len(encoded_seq) < seq_length:
                    encoded_seq.insert(0, 0)
                    
                input_data = np.array([encoded_seq])
                
                # Prediksi probabilitas
                predictions = self.lstm_model.predict(input_data, verbose=0)[0]
                
                # Ambil Top 3
                top_indices = predictions.argsort()[-3:][::-1]
                top_preds = []
                
                for idx in top_indices:
                    cat_name = self.cat_encoder.inverse_transform([[idx]])[0][0]
                    score = predictions[idx]
                    top_preds.append({
                        "category": str(cat_name),
                        "score": round(float(score), 2)
                    })

                return {
                    "status": "success",
                    "next_category_predictions": top_preds,
                    "metadata": {
                        "model_source": "deep_learning_lstm_v1",
                        "model_path": LSTM_PATH,
                        "fallback_used": False,
                        "applies_to": "supporting_recommendation_only",
                        "do_not_apply_to_search": True,
                        "do_not_apply_to_planner": True
                    }
                }
            except Exception as e:
                print(f"[BehaviourService] LSTM Prediction failed, falling back to Markov. Error: {e}")

        # 2. LAYER 2 (FALLBACK): JIKA LSTM GAGAL, GUNAKAN MARKOV BASELINE
        if not self.markov_model:
            return self._get_fallback_response("Both LSTM and Markov models unavailable")

        try:
            if isinstance(self.markov_model, dict):
                transitions = self.markov_model.get(active_state)
                if not transitions:
                    for k in self.markov_model.keys():
                        if str(k).lower() == active_state.lower():
                            transitions = self.markov_model[k]
                            break
                            
                if transitions:
                    sorted_preds = sorted(transitions.items(), key=lambda item: item[1], reverse=True)
                    top_preds = []
                    for cat, score in sorted_preds[:3]:
                        top_preds.append({
                            "category": cat,
                            "score": round(float(score), 2)
                        })
                        
                    return {
                        "status": "success",
                        "next_category_predictions": top_preds,
                        "metadata": {
                            "model_source": "markov_order1_baseline",
                            "model_path": MARKOV_PATH,
                            "fallback_used": True,
                            "fallback_reason": "LSTM bypassed/failed, using Markov fallback",
                            "applies_to": "supporting_recommendation_only",
                            "do_not_apply_to_search": True,
                            "do_not_apply_to_planner": True
                        }
                    }
        except Exception as e:
            print(f"[BehaviourService] Prediction error: {e}")
            
        return self._get_fallback_response(f"Active category '{active_state}' unknown to fallback model")

behaviour_service = BehaviourService()
