import os
import pandas as pd
import numpy as np

# Path to the database
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PENGINAPAN_DB_PATH = os.path.join(
    PROJECT_ROOT,
    "ai_workspace",
    "Wisata_Workspace",
    "01_Dataset",
    "3_Curated",
    "DATABASE_PENGINAPAN_ONLY.csv",
)

class PenginapanService:
    def __init__(self, db_path=PENGINAPAN_DB_PATH):
        self.db_path = db_path
        self.df = None
        self._load_data()

    def _load_data(self):
        try:
            self.df = pd.read_csv(self.db_path)
            # Replace NaNs with suitable defaults
            self.df.replace([np.nan, np.inf, -np.inf], None, inplace=True)
            print(f"Loaded {len(self.df)} penginapan from {self.db_path}")
        except Exception as e:
            print(f"Failed to load penginapan dataset: {e}")
            self.df = pd.DataFrame()

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        import math
        R = 6371.0 # Radius of earth in kilometers
        
        try:
            lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                 math.sin(dlon / 2) * math.sin(dlon / 2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        except (ValueError, TypeError):
            return float('inf')

    def get_penginapans(self, limit=20, page=1, sentiment_filter=None, lat=None, lon=None, category_filter=None):
        if self.df is None or self.df.empty:
            return [], 0

        # Create a copy to filter
        filtered_df = self.df.copy()

        # Category Filter mapping
        if category_filter and category_filter.lower() != 'semua':
            cat_lower = category_filter.lower().replace(' ', '_')
            filtered_df = filtered_df[filtered_df['subcategory'].str.lower().str.contains(cat_lower, na=False)]

        # Sentiment Filter mapping
        if sentiment_filter:
            sf = str(sentiment_filter).strip().lower()
            if sf == 'positif':
                filtered_df = filtered_df[filtered_df['sentiment_score'] > 0.5]
            elif sf == 'negatif':
                filtered_df = filtered_df[filtered_df['sentiment_score'] < 0]
            elif sf == 'netral':
                filtered_df = filtered_df[(filtered_df['sentiment_score'] >= 0) & (filtered_df['sentiment_score'] <= 0.5)]

        # Distance & Score Calculation
        if lat is not None and lon is not None:
            # Calculate distance for each row
            filtered_df['distance_km'] = filtered_df.apply(
                lambda row: self._haversine_distance(lat, lon, row['latitude'], row['longitude']), axis=1
            )
            # Distance score: closer is better. Max distance ~20km gets 0 score. 0km gets 1.0 score.
            max_dist = 20.0
            filtered_df['distance_score'] = (1.0 - (filtered_df['distance_km'] / max_dist)).clip(lower=0.0)
            
            # Combine rating and distance
            # Base rating is 1 to 5. Normalize it to 0-1.
            filtered_df['rating_score'] = (filtered_df.get('avg_rating', 0) / 5.0).clip(upper=1.0)
            
            # Final Score: 70% Distance + 30% Rating
            filtered_df['final_score'] = (0.7 * filtered_df['distance_score']) + (0.3 * filtered_df['rating_score'])
            
            # Sort by final score descending
            filtered_df = filtered_df.sort_values(by='final_score', ascending=False)
        else:
            # Fallback sort by rating
            filtered_df = filtered_df.sort_values(by='avg_rating', ascending=False) if 'avg_rating' in filtered_df else filtered_df

        total_items = len(filtered_df)
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        results = []
        for _, row in paginated_df.iterrows():
            sentiment_score = row.get('sentiment_score')
            if pd.isna(sentiment_score) or sentiment_score is None:
                sentiment_score = 0.5
            
            # Determine badge color
            badge_color = 'gray'
            sentiment_label = 'Netral'
            if sentiment_score > 0.7:
                badge_color = 'green'
                sentiment_label = 'Sangat Positif'
            elif sentiment_score > 0.5:
                badge_color = 'lightgreen'
                sentiment_label = 'Positif'
            elif sentiment_score < 0:
                badge_color = 'red'
                sentiment_label = 'Negatif'

            # Try to build image URL
            image_url = row.get('image_url')
            if not image_url or pd.isna(image_url):
                image_url = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop'

            item = {
                "penginapan_id": str(row.get('location_id', '')),
                "name": str(row.get('location_name', '')),
                "type": str(row.get('subcategory', 'Penginapan')),
                "coordinates": {
                    "latitude": float(row.get('latitude', 0)),
                    "longitude": float(row.get('longitude', 0))
                },
                "price": str(row.get('price_str', 'Hubungi untuk harga')),
                "google_rating": float(row.get('avg_rating', 0)),
                "image_url": str(image_url),
                "distance_km": float(row.get('distance_km', 0)) if 'distance_km' in row else None,
                "ai_insight": {
                    "sentiment_label": sentiment_label,
                    "sentiment_score": float(sentiment_score),
                    "badge_color": badge_color
                }
            }
            results.append(item)

        return results, total_items

# Global instance
penginapan_service = PenginapanService()
