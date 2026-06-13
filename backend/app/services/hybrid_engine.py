"""
Hybrid Behaviour Engine — Service Module for Backend
Predicts next travel category using Markov Chain + LSTM (dummy) + Persona + Rules.
Architecture: 45% Markov + 25% LSTM + 20% Persona + 10% Rules
"""
import pickle
import json
import os
import random


class HybridBehaviourEngine:
    def __init__(self):
        print("Initializing Hybrid Behaviour Engine...")
        self.categories = [
            "Kuliner", "Belanja", "Alam", "Santai/Healing",
            "Hiburan", "Spot Foto", "Religi", "Sejarah"
        ]

        # 1. Load Markov Model (relative to project root)
        markov_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', '..',
            'Behaviour_Workspace', '03_Models', 'markov_order1_baseline.pkl'
        )
        markov_path = os.path.normpath(markov_path)
        try:
            with open(markov_path, 'rb') as f:
                self.markov_model = pickle.load(f)
            print(" - Markov Model Loaded (Weight 45%)")
        except Exception as e:
            print(f" - Markov load failed: {e}. Using empty fallback.")
            self.markov_model = {}

        # 2. LSTM (Failsafe — dummy for local prototype)
        self.use_real_lstm = False
        try:
            import tensorflow as tf
            raise ImportError("Bypass TF for local prototype")
        except ImportError:
            print(" - LSTM Dummy active (Weight 25%)")
            self.use_real_lstm = False

        # 3. Persona Mapping
        self.persona_mapping = {
            "Nature Seeker": {"Alam": 1.0, "Santai/Healing": 0.8, "Spot Foto": 0.6},
            "Urban Casual": {"Belanja": 1.0, "Kuliner": 0.9, "Hiburan": 0.7},
            "Culture Learner": {"Sejarah": 1.0, "Religi": 0.8}
        }

    def _get_markov_scores(self, current_category):
        if current_category in self.markov_model:
            return self.markov_model[current_category]
        return {}

    def _get_lstm_scores_dummy(self, time_context):
        scores = {c: random.uniform(0.01, 0.2) for c in self.categories}
        if time_context == "Pagi":
            scores["Kuliner"] = 0.8
            scores["Belanja"] = 0.5
        elif time_context == "Sore":
            scores["Santai/Healing"] = 0.7
        return scores

    def _get_rule_scores(self, time_context):
        scores = {c: 0.5 for c in self.categories}
        if time_context == "Malam":
            scores["Alam"] = 0.0
            scores["Hiburan"] = 1.0
        elif time_context == "Pagi":
            scores["Hiburan"] = 0.1
            scores["Alam"] = 0.9
        return scores

    def predict_next(self, current_category, time_context, user_persona):
        markov_scores = self._get_markov_scores(current_category)
        lstm_scores = self._get_lstm_scores_dummy(time_context)
        persona_scores = self.persona_mapping.get(user_persona, {})
        rule_scores = self._get_rule_scores(time_context)

        final_candidates = []

        for cat in self.categories:
            m_score = markov_scores.get(cat, 0.0)
            l_score = lstm_scores.get(cat, 0.0)
            p_score = persona_scores.get(cat, 0.1)
            r_score = rule_scores.get(cat, 0.5)

            final_score = (0.45 * m_score) + (0.25 * l_score) + (0.20 * p_score) + (0.10 * r_score)

            reasons = []
            if m_score > 0.4:
                reasons.append(f"Sangat populer dikunjungi setelah {current_category}.")
            if p_score > 0.7:
                reasons.append(f"Sangat cocok dengan jiwa Anda sebagai {user_persona}.")
            if r_score > 0.8:
                reasons.append(f"Ideal untuk waktu {time_context}.")

            reason_str = " ".join(reasons) if reasons else "Cocok sebagai alternatif tujuan selanjutnya."

            final_candidates.append({
                "category": cat,
                "score": round(final_score, 3),
                "reason": reason_str
            })

        final_candidates.sort(key=lambda x: x['score'], reverse=True)
        top_3 = final_candidates[:3]

        return {
            "current_category": current_category,
            "time_context": time_context,
            "user_persona": user_persona,
            "predictions": top_3
        }
