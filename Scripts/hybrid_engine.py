import pickle
import json
import os
import random

class HybridBehaviourEngine:
    def __init__(self):
        print("Membangunkan Hybrid Engine...")
        self.categories = [
            "Kuliner", "Belanja", "Alam", "Santai/Healing", 
            "Hiburan", "Spot Foto", "Religi", "Sejarah"
        ]
        
        # 1. Load Markov Model
        markov_path = r'D:\File\file\Fauzan Lubada\PIJAK\Behaviour_Workspace\03_Models\markov_order1_baseline.pkl'
        try:
            with open(markov_path, 'rb') as f:
                self.markov_model = pickle.load(f)
            print(" - Markov Model Loaded (Bobot 45%)")
        except Exception as e:
            print(f"Gagal meload Markov: {e}")
            self.markov_model = {}

        # 2. Load LSTM (Failsafe for Windows DLL Error)
        self.use_real_lstm = False
        try:
            import tensorflow as tf
            # self.lstm_model = tf.keras.models.load_model(...)
            # Karena error DLL lokal, kita paksa bypass untuk simulasi
            raise ImportError("Bypass TF for local prototype")
        except ImportError:
            print(" - TensorFlow DLL Error / Bypass aktif. Menggunakan LSTM Dummy (Bobot 25%)")
            self.use_real_lstm = False

        # 3. Persona Mapping
        self.persona_mapping = {
            "Nature Seeker": {"Alam": 1.0, "Santai/Healing": 0.8, "Spot Foto": 0.6},
            "Urban Casual": {"Belanja": 1.0, "Kuliner": 0.9, "Hiburan": 0.7},
            "Culture Learner": {"Sejarah": 1.0, "Religi": 0.8, "Budaya": 0.8}
        }

    def _get_markov_scores(self, current_category):
        # Ambil probabilitas dari markov. Jika tidak ada, kembalikan 0
        if current_category in self.markov_model:
            return self.markov_model[current_category]
        return {}

    def _get_lstm_scores_dummy(self, time_context):
        # Simulasi tebakan LSTM (biasanya butuh sequence panjang)
        scores = {c: random.uniform(0.01, 0.2) for c in self.categories}
        if time_context == "Pagi":
            scores["Kuliner"] = 0.8  # LSTM pura-puranya nebak sarapan
            scores["Belanja"] = 0.5
        elif time_context == "Sore":
            scores["Santai/Healing"] = 0.7
        return scores

    def _get_rule_scores(self, time_context):
        # 10% Business Rules
        scores = {c: 0.5 for c in self.categories} # Default netral
        if time_context == "Malam":
            scores["Alam"] = 0.0 # Jangan ke alam terbuka malam hari
            scores["Hiburan"] = 1.0
        elif time_context == "Pagi":
            scores["Hiburan"] = 0.1 # Klub malam tutup
            scores["Alam"] = 0.9
        return scores

    def predict_next(self, current_category, time_context, user_persona):
        # Menghitung Komponen Hibrida
        markov_scores = self._get_markov_scores(current_category)
        lstm_scores = self._get_lstm_scores_dummy(time_context)
        persona_scores = self.persona_mapping.get(user_persona, {})
        rule_scores = self._get_rule_scores(time_context)

        final_candidates = []

        for cat in self.categories:
            # Mengambil skor masing-masing komponen
            m_score = markov_scores.get(cat, 0.0)
            l_score = lstm_scores.get(cat, 0.0)
            p_score = persona_scores.get(cat, 0.1) # default kecil jika tak ada di persona
            r_score = rule_scores.get(cat, 0.5)

            # FORMULA ARSITEKTUR FINAL
            final_score = (0.45 * m_score) + (0.25 * l_score) + (0.20 * p_score) + (0.10 * r_score)

            # Membuat kalimat Alasan (Explainability)
            reasons = []
            if m_score > 0.4: reasons.append(f"Sangat populer dikunjungi setelah {current_category}.")
            if p_score > 0.7: reasons.append(f"Sangat cocok dengan jiwa Anda sebagai {user_persona}.")
            if r_score > 0.8: reasons.append(f"Ideal untuk waktu {time_context}.")
            
            reason_str = " ".join(reasons) if reasons else "Cocok sebagai alternatif tujuan selanjutnya."

            final_candidates.append({
                "category": cat,
                "score": round(final_score, 3),
                "reason": reason_str
            })

        # Urutkan dari skor tertinggi ke terendah
        final_candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Ambil Top 3
        top_3 = final_candidates[:3]

        # Format sesuai JSON yang diminta
        output = {
            "current_category": current_category,
            "time_context": time_context,
            "recommendations": top_3
        }

        return json.dumps(output, indent=2)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("MENGUJI PROTOTYPE HYBRID BEHAVIOUR ENGINE")
    print("="*50)
    
    engine = HybridBehaviourEngine()
    
    # Skenario: User baru keluar dari Hotel (Penginapan) di Pagi hari, Persona: Urban Casual (Suka Belanja/Makan)
    hasil = engine.predict_next(
        current_category="Penginapan",
        time_context="Pagi",
        user_persona="Urban Casual"
    )
    
    print("\nHASIL REKOMENDASI AI:")
    print(hasil)
    print("="*50)
    print("Tahap Selanjutnya: Lempar Top-1 Category (contoh 'Kuliner') ke recommender.py untuk cari nama kafenya!")
