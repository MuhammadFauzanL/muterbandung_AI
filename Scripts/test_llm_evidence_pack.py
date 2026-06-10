import json
import math
import unittest

from Scripts.llm_evidence_pack import build_llm_evidence_pack


class TestLLMEvidencePack(unittest.TestCase):
    def sample_response(self):
        return {
            "status": "success",
            "query": "wisata alam sejuk",
            "ai_intents": {
                "active_intents": ["Alam"],
                "scores": {"Alam": 0.8},
            },
            "manual_filters": {"categories": None},
            "implicit_filters": {"free_only": False},
            "location_context": {"enabled": False},
            "fallback": {"used": False, "reason": None},
            "no_strong_match": {"used": False, "label": None, "reason": None},
            "recommendations": [
                {
                    "rank": 1,
                    "location_id": "loc_001",
                    "location_name": "Glamping Legok Kondang",
                    "category": "Tempat Camping",
                    "multi_labels": ["Alam", "Outdoor"],
                    "label_taxonomy": {
                        "primary_intent": "Alam",
                        "core_labels": ["Alam", "Outdoor"],
                        "secondary_labels": [],
                        "shopping_subtype": math.nan,
                    },
                    "realworld_flags": {
                        "coordinate_verified": True,
                        "safety_verified": True,
                        "crowd_level": "unknown",
                    },
                    "final_score": 82.72,
                    "distance_km": None,
                    "distance_label": None,
                    "score_breakdown": {
                        "similarity": 0.6921,
                        "google_rating": 4.81,
                        "confidence": 0.5611,
                        "matched_intents": ["Alam"],
                        "penalized_intents": [],
                        "distance_score": None,
                        "ranking_mode": "relevance",
                        "sentiment_score": 0.9615,
                        "adjusted_sentiment_score": 0.9091,
                        "sentiment_used_for_ranking": 0.9091,
                        "sentiment_label": "Sangat Positif",
                        "sentiment_model_source": "tfidf_linearsvc",
                        "sentiment_model_version": "run_nlp_pipeline_v2",
                        "sentiment_available": True,
                        "sentiment_review_count": 52,
                        "review_confidence": 0.74,
                        "review_confidence_label": "medium_review_confidence",
                    },
                    "sentiment_metadata": {
                        "sentiment_score": 0.9615,
                        "adjusted_sentiment_score": 0.9091,
                        "sentiment_label": "Sangat Positif",
                        "sentiment_model_source": "tfidf_linearsvc",
                        "sentiment_model_version": "run_nlp_pipeline_v2",
                        "sentiment_available": True,
                        "sentiment_review_count": 52,
                        "review_confidence": 0.74,
                        "review_confidence_label": "medium_review_confidence",
                    },
                    "info_praktis": {
                        "harga": "Rp 250.000 - Rp 1.500.000 (Berbayar)",
                        "jam_buka_weekday": "00:00 - 23:59",
                        "jam_buka_weekend": "00:00 - 23:59",
                        "estimasi_durasi": "90 menit",
                        "koordinat": [-7.1181959, 107.4202751],
                    },
                    "alasan": "Cocok dengan wisata alam sejuk.",
                }
            ],
        }

    def test_builds_guarded_evidence_pack(self):
        pack = build_llm_evidence_pack(self.sample_response())

        self.assertEqual(pack["schema_version"], "muterbandung.llm_evidence_pack.v1")
        self.assertFalse(pack["ranking_policy"]["llm_may_create_destinations"])
        self.assertFalse(pack["ranking_policy"]["llm_may_rerank"])
        self.assertEqual(pack["ranking_policy"]["allowed_destination_ids"], ["loc_001"])
        self.assertEqual(pack["candidates"][0]["destination_id"], "loc_001")
        self.assertEqual(pack["candidates"][0]["sentiment"]["model_source"], "tfidf_linearsvc")
        self.assertEqual(pack["candidates"][0]["sentiment"]["adjusted_score"], 0.9091)
        self.assertEqual(pack["candidates"][0]["sentiment"]["used_for_ranking"], 0.9091)
        self.assertEqual(pack["candidates"][0]["sentiment"]["review_confidence_label"], "medium_review_confidence")
        self.assertEqual(pack["candidates"][0]["media"]["available"], False)
        self.assertEqual(pack["candidates"][0]["media"]["source"], "not_available_in_curated_dataset")
        self.assertIn("backend_reason", pack["candidates"][0])
        self.assertIn("media", pack["source_fields"])

    def test_pack_is_strict_json_serializable(self):
        pack = build_llm_evidence_pack(self.sample_response())
        json.dumps(pack, allow_nan=False)

    def test_empty_recommendations_still_has_guardrails(self):
        response = self.sample_response()
        response["recommendations"] = []
        pack = build_llm_evidence_pack(response)

        self.assertEqual(pack["ranking_policy"]["allowed_destination_ids"], [])
        self.assertEqual(pack["candidates"], [])
        self.assertIn("global_limitations", pack)

    def test_unverified_fields_become_candidate_limitations(self):
        response = self.sample_response()
        item = response["recommendations"][0]
        item["multi_labels"] = ["Malam", "Indoor", "Ramah Anak"]
        item["label_taxonomy"]["core_labels"] = ["Malam", "Indoor", "Ramah Anak"]
        item["realworld_flags"] = {
            "is_active_verified": False,
            "price_verified": False,
            "coordinate_verified": False,
            "night_verified": False,
            "indoor_verified": False,
            "child_friendly_verified": False,
            "parking_verified": False,
            "wheelchair_accessible_verified": False,
            "toilet_verified": False,
            "mushola_verified": False,
            "pet_friendly_verified": False,
            "safety_verified": False,
            "open_24h_verified": False,
            "crowd_level": "unknown",
        }
        item["sentiment_metadata"]["sentiment_available"] = False
        item["score_breakdown"]["sentiment_available"] = False
        item["info_praktis"]["jam_buka_weekend"] = "Tidak ada info"

        pack = build_llm_evidence_pack(response)
        limitations = pack["candidates"][0]["limitations"]

        self.assertIn("Status aktif destinasi belum terverifikasi penuh.", limitations)
        self.assertIn("Harga belum terverifikasi penuh.", limitations)
        self.assertIn("Media/gambar belum tersedia atau belum terverifikasi untuk destinasi ini.", limitations)
        self.assertIn("Detail fasilitas belum terverifikasi; jangan menyebut fasilitas spesifik kecuali flag terkait bernilai true.", limitations)
        self.assertIn("Jam buka belum lengkap untuk sebagian hari.", limitations)
        self.assertIn("Kelayakan kunjungan malam belum terverifikasi penuh.", limitations)
        self.assertIn("Status indoor belum terverifikasi penuh.", limitations)
        self.assertIn("Klaim ramah anak belum terverifikasi penuh.", limitations)


if __name__ == "__main__":
    unittest.main()
