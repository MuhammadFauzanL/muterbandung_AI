import json
import sys

# Memastikan modul bisa diimport
try:
    from hybrid_engine import HybridBehaviourEngine
    from recommender import MuterBandungRecommender
except ImportError as e:
    print(f"Error loading modules: {e}")
    sys.exit(1)

def run_minimal_trial():
    print("="*65)
    print(" [SISTEM] MEMANASKAN MESIN KECERDASAN MUTERBANDUNG (V1.0)")
    print("="*65)
    
    print("\n[1/2] Memuat Otak Perilaku (Markov + Persona)...")
    hybrid = HybridBehaviourEngine()
    
    print("\n[2/2] Memuat Otak Pencarian Makna (MiniLM)...")
    recommender = MuterBandungRecommender()
    
    print("\n" + "="*65)
    print(" [OK] SISTEM SIAP! MARI KITA UJI COBA")
    print("="*65)
    
    # SETTING SKENARIO (Bisa Anda ubah nanti)
    skenario_lokasi = "Penginapan"
    skenario_waktu = "Pagi"
    skenario_persona = "Culture Learner" # Suka Sejarah/Budaya
    
    print(f"KONDISI SAAT INI:")
    print(f" - Posisi Anda : Baru keluar dari {skenario_lokasi}")
    print(f" - Waktu       : {skenario_waktu} hari")
    print(f" - Selera Anda : {skenario_persona}\n")
    
    print("[TAHAP 1]: AI MENEBAK KATEGORI TUJUAN SELANJUTNYA...")
    hasil_hybrid_str = hybrid.predict_next(
        current_category=skenario_lokasi,
        time_context=skenario_waktu,
        user_persona=skenario_persona
    )
    hasil_hybrid = json.loads(hasil_hybrid_str)
    
    kategori_target = hasil_hybrid['recommendations'][0]['category']
    alasan_target = hasil_hybrid['recommendations'][0]['reason']
    
    print(f" -> Kategori Terpilih : {kategori_target.upper()}")
    print(f" -> Alasan AI         : {alasan_target}\n")
    
    print(f"[TAHAP 2]: AI MENCARI TEMPAT {kategori_target.upper()} TERBAIK...")
    # Rahasia RAG: Menggabungkan tebakan Kategori dengan Persona menjadi Prompt Semantik
    query_pencarian = f"{kategori_target} sejarah budaya museum religi"
    
    hasil_tempat = recommender.recommend(query=query_pencarian, top_k=3)
    
    for i, tempat in enumerate(hasil_tempat['recommendations'], start=1):
        print(f"\n >>> JUARA {i} : {tempat['location_name']}")
        print(f"   Kategori   : {tempat['category']} - {tempat.get('subcategory', 'Umum')}")
        print(f"   Sentimen   : {tempat['score_breakdown']['sentiment_score']:.2f} (Skor Reputasi)")
        print(f"   Kecocokan  : {tempat['score_breakdown']['similarity']*100:.1f}%")
        print(f"   Alasan Rekomendasi: {tempat.get('explanation', 'Tempat ini sesuai dengan profil dan pergerakan Anda.')}")

if __name__ == "__main__":
    run_minimal_trial()
