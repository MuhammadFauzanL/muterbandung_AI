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

    def _first_value(self, row, *keys, default=None):
        for key in keys:
            if key in row and row.get(key) is not None and not pd.isna(row.get(key)):
                value = row.get(key)
                if str(value).strip():
                    return value
        return default

    def _price_label(self, row):
        explicit = self._first_value(row, "price_str", "price", default=None)
        if explicit:
            return str(explicit)

        price_min = self._first_value(row, "price_min", default=None)
        price_max = self._first_value(row, "price_max", default=None)
        try:
            price_min = int(float(price_min)) if price_min is not None else None
            price_max = int(float(price_max)) if price_max is not None else None
        except (TypeError, ValueError):
            price_min = None
            price_max = None

        if price_min is not None and price_max is not None and price_min != price_max:
            return f"Rp {price_min:,} - Rp {price_max:,}".replace(",", ".")
        if price_min is not None:
            return f"Rp {price_min:,}".replace(",", ".")
        if price_max is not None:
            return f"Rp {price_max:,}".replace(",", ".")
        return "Hubungi untuk harga"

    def _clean_text(self, value):
        text = str(value or "").strip()
        replacements = {
            "â": '"',
            "â": '"',
            "â": "'",
            "â": "-",
            "â": "-",
            "Â": "",
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)
        return text.strip()

    def _row_to_item(self, row):
        sentiment_score = self._first_value(row, "sentiment_score", "avg_sentimen_skor", default=0.5)
        try:
            sentiment_score = float(sentiment_score)
        except (TypeError, ValueError):
            sentiment_score = 0.5

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

        image_url = self._first_value(row, "image_url", "media_image_url", default="")
        if not image_url:
            image_url = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop'

        rating = self._first_value(row, "avg_rating", "totalScore", default=0)
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            rating = 0.0

        latitude = self._first_value(row, "latitude", default=0)
        longitude = self._first_value(row, "longitude", default=0)
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            latitude = 0.0
            longitude = 0.0

        return {
            "penginapan_id": self._clean_text(self._first_value(row, "location_id", default="")),
            "name": self._clean_text(self._first_value(row, "location_name", "title", default="")).split(" | ")[0],
            "type": self._clean_text(self._first_value(row, "subcategory", "category", default="Penginapan")),
            "city": self._clean_text(self._first_value(row, "kota_kabupaten", "city", default="")),
            "district": self._clean_text(self._first_value(row, "kecamatan", "neighborhood", default="")),
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "price": self._price_label(row),
            "google_rating": rating,
            "image_url": str(image_url),
            "destination_url": str(self._first_value(row, "media_destination_url", "url", default="")),
            "website": str(self._first_value(row, "media_website", "website", default="")),
            "distance_km": float(row.get('distance_km', 0)) if 'distance_km' in row and row.get('distance_km') is not None else None,
            "ai_insight": {
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "badge_color": badge_color,
            }
        }

    def search_penginapans(self, query=None, limit=5, lat=None, lon=None):
        if self.df is None or self.df.empty:
            return []

        filtered_df = self.df.copy()
        query_text = str(query or "").lower()
        stopwords = {
            "cari", "carikan", "rekomendasi", "dekat", "sekitar", "di", "ke",
            "hotel", "penginapan", "villa", "guest", "house", "kost", "kamar",
            "yang", "murah", "bagus", "buat", "untuk",
        }
        tokens = [
            token
            for token in query_text.replace("-", " ").split()
            if len(token) > 2 and token not in stopwords
        ]
        if tokens:
            searchable_columns = [
                column
                for column in ("location_name", "subcategory", "kota_kabupaten", "kecamatan", "tags_sintetis")
                if column in filtered_df.columns
            ]
            if searchable_columns:
                haystack = filtered_df[searchable_columns].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
                mask = haystack.apply(lambda text: any(token in text for token in tokens))
                if mask.any():
                    filtered_df = filtered_df[mask]

        if lat is not None and lon is not None:
            filtered_df['distance_km'] = filtered_df.apply(
                lambda row: self._haversine_distance(lat, lon, row.get('latitude'), row.get('longitude')), axis=1
            )
            filtered_df = filtered_df.sort_values(by=['distance_km', 'avg_rating'], ascending=[True, False])
        elif 'avg_rating' in filtered_df:
            filtered_df = filtered_df.sort_values(by='avg_rating', ascending=False)

        return [self._row_to_item(row) for _, row in filtered_df.head(limit).iterrows()]

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

            item = self._row_to_item(row)
            item["ai_insight"] = {
                "sentiment_label": sentiment_label,
                "sentiment_score": float(sentiment_score),
                "badge_color": badge_color
            }
            results.append(item)

        return results, total_items

# Global instance
penginapan_service = PenginapanService()
