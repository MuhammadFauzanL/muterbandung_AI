import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def train_persona_model():
    print("Mulai melatih Model Persona (K-Means) pada Dataset UCI TripAdvisor...\n")
    
    # 1. Load Data
    csv_path = r'D:\File\file\Fauzan Lubada\PIJAK\travel_reviews\tripadvisor_review.csv'
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di {csv_path}")
        return

    # 2. Preprocessing (Ubah nama kolom agar jelas)
    columns_map = {
        'Category 1': 'Art_Galleries',
        'Category 2': 'Dance_Clubs',
        'Category 3': 'Juice_Bars',
        'Category 4': 'Restaurants',
        'Category 5': 'Museums',
        'Category 6': 'Resorts',
        'Category 7': 'Parks_Picnic',
        'Category 8': 'Beaches',
        'Category 9': 'Theaters',
        'Category 10': 'Religious_Institutions'
    }
    df = df.rename(columns=columns_map)
    
    # Pisahkan User ID dari fitur yang akan di-train
    X = df.drop('User ID', axis=1)

    # Normalisasi Data (Opsional tapi disarankan untuk K-Means)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Modeling (K-Means Clustering)
    # Kita asumsikan ingin membagi menjadi 3 Persona utama
    NUM_CLUSTERS = 3
    kmeans = KMeans(n_clusters=NUM_CLUSTERS, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)

    # 4. Profiling (Melihat Karakteristik tiap Persona)
    print("=== HASIL KLASTERING (CENTROIDS) ===")
    print("Angka di bawah adalah Rata-rata Rating (0-4) yang diberikan oleh tiap Persona pada masing-masing kategori:")
    
    # Kita pakai data asli (bukan yang di-scale) agar angkanya masuk akal (rating 0-4)
    cluster_means = df.drop('User ID', axis=1).groupby('Cluster').mean()
    
    for i in range(NUM_CLUSTERS):
        print(f"\n[ PERSONA KLASTER {i} ]")
        print(f"Jumlah User di klaster ini: {len(df[df['Cluster'] == i])} orang")
        
        # Ambil 3 kategori dengan rating tertinggi untuk klaster ini
        top_categories = cluster_means.loc[i].sort_values(ascending=False).head(3)
        print("Ciri Khas (Top 3 Kategori Kesukaan):")
        for cat, rating in top_categories.items():
            print(f" - {cat}: {rating:.2f} bintang")

if __name__ == "__main__":
    train_persona_model()
