import unittest

import pandas as pd

from Scripts.validate_curated_dataset import REQUIRED_COLUMNS, validate_dataset, validate_dataframe


class TestDataValidation(unittest.TestCase):
    def test_canonical_dataset_has_no_blocking_errors(self):
        result = validate_dataset()
        summary = result["summary"]

        self.assertEqual(result["schema_version"], "muterbandung.data_validation.v1")
        self.assertEqual(summary["error_count"], 0)
        self.assertEqual(summary["gate_status"], "PASS_WITH_WARNINGS")
        self.assertGreaterEqual(summary["active_candidate_count"], 200)

    def test_invalid_dataset_reports_blocking_errors(self):
        row = {column: "" for column in REQUIRED_COLUMNS}
        row.update({
            "location_id": "LOC-TEST",
            "location_name": "Invalid Place",
            "category": "Wisata",
            "multi_labels": "[]",
            "latitude": "999",
            "longitude": "not-a-number",
            "price_min": "100000",
            "price_max": "50000",
            "price_type": "Gratis",
            "jam_buka_weekday": "25:00",
            "jam_tutup_weekday": "Tutup",
            "jam_buka_weekend": "08:00",
            "jam_tutup_weekend": "17:00",
            "estimasi_durasi_menit": "60",
            "deskripsi_google": "Deskripsi cukup panjang untuk test.",
            "tags_sintetis": "alam;test",
            "avg_rating": "6",
            "total_ulasan": "0",
            "final_primary_intent": "Alam",
            "final_core_labels": "Alam",
            "curation_action": "keep",
            "display_status": "bad_status",
            "is_active_verified": "maybe",
            "price_verified": "yes",
            "night_verified": "False",
            "indoor_verified": "False",
            "child_friendly_verified": "False",
            "parking_verified": "False",
            "wheelchair_accessible_verified": "False",
            "toilet_verified": "False",
            "mushola_verified": "False",
            "pet_friendly_verified": "False",
            "open_24h_verified": "False",
            "crowd_level": "crowded",
            "coordinate_verified": "False",
            "safety_verified": "False",
            "sentiment_score": "2",
            "sentiment_model_source": "unavailable",
            "sentiment_model_version": "",
            "sentiment_available": "True",
            "media_available": "True",
            "media_image_url": "",
            "media_destination_url": "",
            "media_website": "",
            "media_source": "",
            "media_place_id": "",
            "media_match_score": "2",
            "media_match_method": "",
            "media_audit_status": "missing",
        })
        result = validate_dataframe(pd.DataFrame([row]), dataset_path="<invalid-test>")
        codes = {issue["code"] for issue in result["issues"] if issue["severity"] == "ERROR"}

        self.assertGreater(result["summary"]["error_count"], 0)
        self.assertEqual(result["summary"]["gate_status"], "FAIL")
        self.assertIn("E_DISPLAY_STATUS_INVALID", codes)
        self.assertIn("E_NUMERIC_ABOVE_MAX", codes)
        self.assertIn("E_NUMERIC_INVALID", codes)
        self.assertIn("E_PRICE_MIN_GT_MAX", codes)
        self.assertIn("E_PRICE_FREE_INCONSISTENT", codes)
        self.assertIn("E_TIME_FORMAT_INVALID", codes)
        self.assertIn("E_BOOLEAN_INVALID", codes)
        self.assertIn("E_SENTIMENT_AVAILABLE_PROVENANCE_INVALID", codes)
        self.assertIn("E_MEDIA_AVAILABLE_WITHOUT_URL", codes)


if __name__ == "__main__":
    unittest.main()
