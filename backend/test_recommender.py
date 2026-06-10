import sys
import os
# Import torch first to avoid DLL conflict under Windows
import torch
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))
from app.services.recommender import MuterBandungRecommender
import unittest
import pandas as pd

class TestMuterBandungRecommender(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Initialize recommender with dataset
        cls.recommender = MuterBandungRecommender(db_path='DATABASE_WISATA_FINAL_PARIPURNA.csv')

    def test_initialization(self):
        """Test if database is loaded correctly and nulls are handled."""
        self.assertIsNotNone(self.recommender.df)
        self.assertGreater(len(self.recommender.df), 0)
        
        # Test if avg_rating has any remaining nulls (should be 0)
        null_count = self.recommender.df['avg_rating'].isnull().sum()
        self.assertEqual(null_count, 0)
        
        # Test if parsed labels column exists and is list
        self.assertTrue('multi_labels_parsed' in self.recommender.df.columns)
        first_row_labels = self.recommender.df['multi_labels_parsed'].iloc[0]
        self.assertIsInstance(first_row_labels, list)

    def test_parse_multi_labels(self):
        """Test safe list parsing logic."""
        self.assertEqual(self.recommender._parse_multi_labels("['Alam', 'Kuliner']"), ['Alam', 'Kuliner'])
        self.assertEqual(self.recommender._parse_multi_labels("[]"), [])
        self.assertEqual(self.recommender._parse_multi_labels(None), [])
        self.assertEqual(self.recommender._parse_multi_labels("Invalid string"), [])

    def test_time_parsing(self):
        """Test parsing of opening time strings to minutes."""
        self.assertEqual(self.recommender._parse_time_to_minutes("08:00"), 480)
        self.assertEqual(self.recommender._parse_time_to_minutes("17:30"), 1050)
        self.assertEqual(self.recommender._parse_time_to_minutes("00:00"), 0)
        self.assertEqual(self.recommender._parse_time_to_minutes("Tutup"), None)
        self.assertEqual(self.recommender._parse_time_to_minutes(None), None)

    def test_is_open(self):
        """Test is_open logic including overnight scenarios."""
        # Standard day hours (08:00 - 17:00)
        self.assertTrue(self.recommender._is_open("08:00", "17:00", "12:00"))
        self.assertTrue(self.recommender._is_open("08:00", "17:00", "08:00"))
        self.assertTrue(self.recommender._is_open("08:00", "17:00", "17:00"))
        self.assertFalse(self.recommender._is_open("08:00", "17:00", "07:59"))
        self.assertFalse(self.recommender._is_open("08:00", "17:00", "18:00"))
        
        # Overnight hours (18:00 - 02:00)
        self.assertTrue(self.recommender._is_open("18:00", "02:00", "20:00"))
        self.assertTrue(self.recommender._is_open("18:00", "02:00", "01:00"))
        self.assertFalse(self.recommender._is_open("18:00", "02:00", "12:00"))
        
        # Closed places
        self.assertFalse(self.recommender._is_open("Tutup", "Tutup", "12:00"))

    def test_hard_filtering_categories(self):
        """Test Step A: Category and multi-label filtering."""
        # Filter for Alam and Ramah Anak
        res = self.recommender.recommend(categories=["Alam", "Ramah Anak"], top_k=234)
        self.assertEqual(res['status'], 'success')
        
        for item in res['recommendations']:
            labels = [l.lower() for l in item['multi_labels']]
            cat = item['category'].lower()
            # Must match either primary category or multi labels for both "Alam" and "Ramah Anak"
            has_alam = "alam" in labels or "alam" in cat or "wisata alam" in cat
            has_child = "ramah anak" in labels or "ramah anak" in cat
            self.assertTrue(has_alam, f"Failed for {item['location_name']}")
            self.assertTrue(has_child, f"Failed for {item['location_name']}")

    def test_hard_filtering_price(self):
        """Test Step A: Price filtering."""
        max_budget = 20000
        res = self.recommender.recommend(max_price=max_budget, top_k=234)
        
        for item in res['recommendations']:
            # Find the row in database to check the actual price
            row = self.recommender.df[self.recommender.df['location_name'] == item['location_name']].iloc[0]
            self.assertLessEqual(row['price_max'], max_budget)

        # Free only filter
        res_free = self.recommender.recommend(free_only=True, top_k=234)
        for item in res_free['recommendations']:
            row = self.recommender.df[self.recommender.df['location_name'] == item['location_name']].iloc[0]
            is_free = str(row['price_type']).lower() == 'gratis' or row['price_max'] == 0
            self.assertTrue(is_free)

    def test_hard_filtering_rating(self):
        """Test Step A: Rating filtering."""
        min_rat = 4.5
        res = self.recommender.recommend(min_rating=min_rat, top_k=234)
        
        for item in res['recommendations']:
            self.assertGreaterEqual(item['score_breakdown']['google_rating'], min_rat)

    def test_scoring_weights_and_range(self):
        """Test Step C: Weighted scoring output ranges and constraints."""
        # 1. Hybrid Search (text + filters)
        res = self.recommender.recommend(query="wisata alam sejuk", categories=["Alam"], top_k=5)
        self.assertLessEqual(len(res['recommendations']), 5)
        
        previous_score = 101.0
        for item in res['recommendations']:
            score = item['final_score']
            # Score must be between 0 and 100
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 100.0)
            # Scores must be sorted in descending order
            self.assertLessEqual(score, previous_score)
            previous_score = score
            
            # Score breakdown parts should exist
            bd = item['score_breakdown']
            self.assertIn('similarity', bd)
            self.assertIn('sentiment_score', bd)
            self.assertIn('adjusted_sentiment_score', bd)
            self.assertIn('sentiment_used_for_ranking', bd)
            self.assertIn('sentiment_model_source', bd)
            self.assertIn('sentiment_model_version', bd)
            self.assertIn('sentiment_available', bd)
            self.assertIn('review_confidence', bd)
            self.assertIn('review_confidence_label', bd)
            self.assertIn(bd['review_confidence_label'], {
                'low_review_confidence',
                'medium_review_confidence',
                'high_review_confidence',
            })
            self.assertNotIn('sentimen_indobert', bd)
            self.assertIn('google_rating', bd)
            self.assertIn('confidence', bd)
            
            # Since query is text, similarity weight should be active (> 0)
            self.assertGreater(bd['similarity'], -0.01) # cosine similarity is non-negative here

    def test_explanation_presence(self):
        """Test if explanation is generated in Indonesian."""
        res = self.recommender.recommend(query="kuliner bandung", top_k=1)
        self.assertTrue(len(res['recommendations']) > 0)
        item = res['recommendations'][0]
        self.assertIn('alasan', item)
        self.assertIsInstance(item['alasan'], str)
        self.assertGreater(len(item['alasan']), 10)

    def test_media_metadata_contract(self):
        """Media metadata should be present and only expose audited URLs."""
        self.assertIn('media_available', self.recommender.df.columns)
        media_rows = self.recommender.df[self.recommender.df['media_available'] == True]
        self.assertGreater(len(media_rows), 0)

        media = self.recommender._get_media_metadata(media_rows.iloc[0])
        self.assertTrue(media['available'])
        self.assertTrue(media['image_url'].startswith('http') or media['destination_url'].startswith('http'))
        self.assertIn('audit_status', media)

        res = self.recommender.recommend(query="wisata alam sejuk", top_k=1)
        self.assertIn('media', res['recommendations'][0])
        self.assertIn('available', res['recommendations'][0]['media'])

    def test_adjusted_sentiment_shrinks_low_review_extremes(self):
        """Bayesian shrinkage should make low-review extremes less overconfident."""
        prior = self.recommender.sentiment_global_average
        low_review = pd.Series({
            'sentiment_score': 1.0,
            'avg_sentimen_skor': 1.0,
            'total_ulasan': 5,
            'sentiment_available': True,
            'sentimen_label_lokasi': 'Sangat Positif',
        })
        high_review = pd.Series({
            'sentiment_score': 1.0,
            'avg_sentimen_skor': 1.0,
            'total_ulasan': self.recommender.sentiment_review_count_p95 * 2,
            'sentiment_available': True,
            'sentimen_label_lokasi': 'Sangat Positif',
        })

        low_meta = self.recommender._get_sentiment_metadata(low_review)
        high_meta = self.recommender._get_sentiment_metadata(high_review)

        self.assertLess(low_meta['adjusted_sentiment_score'], 1.0)
        self.assertLess(abs(high_meta['adjusted_sentiment_score'] - 1.0), abs(low_meta['adjusted_sentiment_score'] - 1.0))
        self.assertGreaterEqual(low_meta['adjusted_sentiment_score'], prior)
        self.assertEqual(high_meta['review_confidence'], 1.0)
        self.assertIn(low_meta['review_confidence_label'], {
            'low_review_confidence',
            'medium_review_confidence',
        })
        self.assertEqual(high_meta['review_confidence_label'], 'high_review_confidence')

if __name__ == '__main__':
    unittest.main()
