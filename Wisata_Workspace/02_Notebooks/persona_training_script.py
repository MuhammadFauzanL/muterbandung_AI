import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import seaborn as sns
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

print("=== TAHAP 0: Memuat Data ===")
project_root = Path('../../').resolve()
dataset_path = project_root / 'travel_ratings_extracted' / 'google_review_ratings.csv'

if not dataset_path.exists():
    dataset_path = Path(r'D:\File\file\Fauzan Lubada\PIJAK\travel_ratings_extracted\google_review_ratings.csv')
    project_root = Path(r'D:\File\file\Fauzan Lubada\PIJAK')

df_raw = pd.read_csv(dataset_path)
if 'Unnamed: 25' in df_raw.columns:
    df_raw = df_raw.drop(columns=['Unnamed: 25'])

columns_map = {
    'Category 1': 'Churches_Religi', 'Category 2': 'Resorts', 'Category 3': 'Beaches_Water',
    'Category 4': 'Parks_Alam', 'Category 5': 'Theaters', 'Category 6': 'Museums',
    'Category 7': 'Malls', 'Category 8': 'Zoo', 'Category 9': 'Restaurants',
    'Category 10': 'Pubs_Bars', 'Category 11': 'Local_Services', 'Category 12': 'Burger_Pizza_FastFood',
    'Category 13': 'Hotels', 'Category 14': 'Juice_Bars', 'Category 15': 'Art_Galleries',
    'Category 16': 'Dance_Clubs', 'Category 17': 'Swimming_Pools', 'Category 18': 'Gyms',
    'Category 19': 'Bakeries_OlehOleh', 'Category 20': 'Beauty_Spas', 'Category 21': 'Cafes',
    'Category 22': 'View_Points', 'Category 23': 'Monuments', 'Category 24': 'Gardens'
}
df_mapped = df_raw.rename(columns=columns_map)
print(f"Data terload: {df_mapped.shape[0]} Baris, {df_mapped.shape[1]} Kolom.\n")

print("=== TAHAP 1: Audit Data ===")
X = df_mapped.drop('User', axis=1)
X = X.apply(pd.to_numeric, errors='coerce')
X = X.fillna(X.mean())
print("Data berhasil dibersihkan dan siap diproses.\n")

print("=== TAHAP 2 & 3: K-Means Training (K=6) ===")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

final_k = 6
kmeans_final = KMeans(n_clusters=final_k, random_state=42, n_init=10)
df_mapped['Cluster'] = kmeans_final.fit_predict(X_scaled)

cluster_means = df_mapped.drop('User', axis=1, errors='ignore').groupby('Cluster').mean(numeric_only=True)
global_means = X.mean()
cluster_uniqueness = cluster_means - global_means

for i in range(final_k):
    count = len(df_mapped[df_mapped['Cluster'] == i])
    print(f"--- Cluster {i} ({count} pengguna) ---")
    top_unique = cluster_uniqueness.loc[i].sort_values(ascending=False).head(3)
    for cat, val in top_unique.items():
        print(f"  + {cat} (+{val:.2f})")
    print()

print("=== TAHAP 5: Export Model ke .pkl ===")
models_dir = project_root / 'Models'
os.makedirs(models_dir, exist_ok=True)

joblib.dump(scaler, models_dir / 'persona_scaler.pkl')
joblib.dump(kmeans_final, models_dir / 'persona_kmeans.pkl')

print(f"SUKSES! Model ML berhasil diekspor ke folder:\n{models_dir}")
print("File yang tercipta: persona_scaler.pkl dan persona_kmeans.pkl\n")

print("=== TAHAP 4: Evaluasi & Visualisasi 2D ===")
sil_score = silhouette_score(X_scaled, df_mapped['Cluster'])
print(f"Silhouette Score (K={final_k}): {sil_score:.3f}")
print("Membuka Jendela Grafik... (Tutup jendela grafik untuk mengakhiri program)")

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame(data=X_pca, columns=['PCA_1', 'PCA_2'])
pca_df['Persona'] = df_mapped['Cluster'].astype(str)

plt.figure(figsize=(10, 7))
sns.scatterplot(x='PCA_1', y='PCA_2', hue='Persona', palette='tab10', data=pca_df, s=60, alpha=0.7)
plt.title('Sebaran Persona Turis (Visualisasi 2D PCA)')
plt.xlabel('Komponen Utama 1')
plt.ylabel('Komponen Utama 2')
plt.legend(title='Klaster Persona', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()
