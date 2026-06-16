import os
import json
import numpy as np

# Path configurations
BASE_DIR = r'D:\File\file\Fauzan Lubada\PIJAK'
MODELS_DIR = os.path.join(BASE_DIR, 'Models')
KMEANS_PATH = os.path.join(MODELS_DIR, 'persona_kmeans.pkl')
SCALER_PATH = os.path.join(MODELS_DIR, 'persona_scaler.pkl')

RULES_PATH = os.path.join(
    BASE_DIR,
    'MUTERBANDUNG_CORE_SYSTEM',
    '1_Dataset_Runtime',
    'Persona_Home',
    'PERSONA_HOME_RULES_2026-06-13.json'
)

class PersonaService:
    def __init__(self):
        self.kmeans_model = None
        self.scaler = None
        self.rules = self._load_rules()
        self._load_ml_models()

    def _load_rules(self):
        try:
            with open(RULES_PATH, 'r', encoding='utf-8') as f:
                return json.load(f).get('personas', [])
        except Exception as e:
            print(f'[PersonaService] Error loading rules: {e}')
            return []

    def _load_ml_models(self):
        try:
            import joblib
            if os.path.exists(KMEANS_PATH) and os.path.exists(SCALER_PATH):
                self.kmeans_model = joblib.load(KMEANS_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                print('[PersonaService] ML Models (KMeans & Scaler) loaded successfully!')
            else:
                print('[PersonaService] ML Models not found. Will fallback to rules.')
        except Exception as e:
            print(f'[PersonaService] Failed to load ML models: {e}')

    def _get_fallback_persona(self, reason='Rules failed'):
        return {
            'status': 'success',
            'persona': {
                'persona_id': 'general_explorer',
                'persona_name': 'General Explorer',
                'persona_source': 'fallback_rule',
                'persona_confidence': 0.3,
                'home_boost_labels': [],
                'home_filter_flags': {},
                'do_not_apply_to_search': True,
                'do_not_apply_to_planner': True
            },
            'metadata': {
                'model_used': False,
                'fallback_used': True,
                'fallback_reason': reason
            }
        }

    def _map_cluster_to_persona(self, cluster_id):
        mapping = {
            0: 'nature_seeker',
            1: 'family_planner',
            2: 'urban_explorer'
        }
        return mapping.get(int(cluster_id), 'general_explorer')

    def determine_home_persona(self, payload):
        # 1. COBA MENGGUNAKAN MODEL ML (K-MEANS) TERLEBIH DAHULU
        if self.kmeans_model and self.scaler:
            try:
                features = [
                    len(payload.get('favorite_place_labels', [])),
                    len(payload.get('activity_labels', [])),
                    len(payload.get('target_visitor_labels', [])),
                    len(payload.get('mood_labels', [])),
                    1 if payload.get('free_only') else 0
                ]
                
                features_array = np.array([features])
                scaled_features = self.scaler.transform(features_array)
                
                cluster_pred = self.kmeans_model.predict(scaled_features)[0]
                predicted_persona_id = self._map_cluster_to_persona(cluster_pred)
                
                best_match = next((p for p in self.rules if p.get('persona_id') == predicted_persona_id), None)
                
                if best_match:
                    return {
                        'status': 'success',
                        'persona': {
                            'persona_id': best_match.get('persona_id'),
                            'persona_name': best_match.get('persona_name'),
                            'persona_source': 'ml_kmeans_clustering',
                            'persona_confidence': 0.85,
                            'home_boost_labels': best_match.get('home_boost_labels', []),
                            'home_filter_flags': best_match.get('home_filter_flags', {}),
                            'do_not_apply_to_search': True,
                            'do_not_apply_to_planner': True
                        },
                        'metadata': {
                            'model_used': True,
                            'model_path': KMEANS_PATH,
                            'fallback_used': False
                        }
                    }
            except Exception as e:
                print(f'[PersonaService] ML Prediction failed, attempting fallback to rules. Error: {e}')

        # 2. LAYER 2 (FALLBACK): JIKA ML GAGAL ATAU TIDAK ADA, GUNAKAN RULES
        if not self.rules:
            return self._get_fallback_persona('Rules empty and ML failed')

        user_labels = set()
        for key in ['favorite_place_labels', 'activity_labels', 'target_visitor_labels', 'mood_labels']:
            labels = payload.get(key, [])
            if isinstance(labels, list):
                for lbl in labels:
                    user_labels.add(str(lbl).lower().strip())

        best_match = None
        max_matches = 0

        for persona in self.rules:
            trigger_labels = [str(l).lower().strip() for l in persona.get('trigger_labels', [])]
            match_count = sum(1 for label in user_labels if label in trigger_labels)
            
            if match_count > max_matches:
                max_matches = match_count
                best_match = persona

        if not best_match or max_matches == 0:
            return self._get_fallback_persona('No matching labels found in fallback rules')

        confidence = round(min(max_matches / len(user_labels) if user_labels else 0.5, 0.95), 2)

        return {
            'status': 'success',
            'persona': {
                'persona_id': best_match.get('persona_id', 'unknown'),
                'persona_name': best_match.get('persona_name', 'Unknown Persona'),
                'persona_source': 'rule_based_home_v1',
                'persona_confidence': confidence,
                'home_boost_labels': best_match.get('home_boost_labels', []),
                'home_filter_flags': best_match.get('home_filter_flags', {}),
                'do_not_apply_to_search': True,
                'do_not_apply_to_planner': True
            },
            'metadata': {
                'model_used': False,
                'fallback_used': True,
                'fallback_reason': 'ML model bypassed or failed, using explicit rules'
            }
        }

persona_service = PersonaService()
