import os
import sys

# Ensure import of recommender works when executing from different working directories
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommender import MuterBandungRecommender

def main():
    print("=" * 70)
    print("DEMO MUTERBANDUNG CORE RECOMMENDER ENGINE V1.0")
    print("=" * 70)
    
    # Initialize engine
    try:
        engine = MuterBandungRecommender(db_path='DATABASE_WISATA_FINAL_PARIPURNA.csv')
    except Exception as e:
        print(f"Error initializing recommender engine: {e}")
        return

    # Skenario 1: Pencarian Teks Murni (UC-1)
    # Query: "wisata alam yang sejuk"
    print("\n--- SKENARIO 1: Pencarian Teks Murni (UC-1) ---")
    print("Query: 'wisata alam yang sejuk'")
    results_1 = engine.recommend(query="wisata alam yang sejuk", top_k=3)
    engine.print_recommendations(results_1)
    
    # Skenario 2: Filter Murni / Tanpa Teks (UC-2)
    # Filter: Kategori Kuliner, Gratis Only
    print("\n--- SKENARIO 2: Filter Murni / Tanpa Teks (UC-2) ---")
    print("Filter: Kategori 'Kuliner', Gratis")
    results_2 = engine.recommend(categories=["Kuliner"], free_only=True, top_k=3)
    engine.print_recommendations(results_2)
    
    # Skenario 3: Hybrid / Teks + Filter (UC-3)
    # Query: "wisata alam yang cocok untuk anak kecil"
    # Filter: Kategori Alam & Ramah Anak, Harga Maks 50.000
    print("\n--- SKENARIO 3: Hybrid / Teks + Filter (UC-3) ---")
    print("Query : 'wisata alam yang cocok untuk anak kecil'")
    print("Filter: Kategori ['Alam', 'Ramah Anak'], Harga Maks 50.000")
    results_3 = engine.recommend(
        query="wisata alam yang cocok untuk anak kecil",
        categories=["Alam", "Ramah Anak"],
        max_price=50000,
        top_k=3
    )
    engine.print_recommendations(results_3)
    
    # Skenario 4: Jam Operasional / Mau Jalan Sekarang (UC-4)
    # Query: "tempat nongkrong santai"
    # Filter: Buka Hari Weekend, Jam 20:00
    print("\n--- SKENARIO 4: Jam Operasional / Weekend Malam (UC-4) ---")
    print("Query : 'tempat nongkrong santai'")
    print("Filter: Weekend jam 20:00")
    results_4 = engine.recommend(
        query="tempat nongkrong santai",
        day_type="weekend",
        open_at_hour="20:00",
        top_k=3
    )
    engine.print_recommendations(results_4)

if __name__ == "__main__":
    main()
