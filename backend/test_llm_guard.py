import copy
import unittest

from app.services.llm_evidence_pack import build_llm_evidence_pack
from app.services.llm_guard import build_llm_prompt_guard, validate_llm_output
from test_llm_evidence_pack import TestLLMEvidencePack


class TestLLMGuard(unittest.TestCase):
    def setUp(self):
        base = TestLLMEvidencePack().sample_response()
        second = copy.deepcopy(base["recommendations"][0])
        second["rank"] = 2
        second["location_id"] = "loc_002"
        second["location_name"] = "Taman Hutan Raya Ir. H. Djuanda"
        second["info_praktis"]["harga"] = "Rp 15.000"
        base["recommendations"].append(second)
        self.pack = build_llm_evidence_pack(base)

    def valid_output(self):
        summaries = []
        for candidate in self.pack["candidates"]:
            practical = candidate["practical_info"]
            sentiment = candidate["sentiment"]
            summaries.append({
                "destination_id": candidate["destination_id"],
                "rank": candidate["rank"],
                "name": candidate["name"],
                "why": candidate["backend_reason"],
                "price": practical["price"],
                "opening_hours": practical["opening_hours"],
                "distance_label": practical["distance_label"],
                "sentiment_score": sentiment["score"],
                "sentiment_model_source": sentiment["model_source"],
                "media": candidate["media"],
                "realworld_flags": {
                    "coordinate_verified": candidate["realworld_flags"]["coordinate_verified"],
                    "safety_verified": candidate["realworld_flags"]["safety_verified"],
                },
                "limitations": candidate["limitations"],
            })
        return {
            "schema_version": "muterbandung.llm_output.v1",
            "answer": "Saya merekomendasikan dua destinasi sesuai urutan backend.",
            "selected_destination_ids": [candidate["destination_id"] for candidate in self.pack["candidates"]],
            "destination_summaries": summaries,
            "warnings": [
                "Harga dan jam buka perlu dicek ulang sebelum berangkat."
            ],
            "follow_up_question": None,
        }

    def test_prompt_guard_contains_core_rules(self):
        guard = build_llm_prompt_guard(self.pack)

        self.assertEqual(guard["schema_version"], "muterbandung.llm_prompt_guard.v1")
        self.assertEqual(guard["output_schema_version"], "muterbandung.llm_output.v1")
        self.assertIn("Jangan membuat destinasi", guard["system_prompt"])
        self.assertIn("Do not rerank", " ".join(guard["rules"]))

    def test_valid_output_passes(self):
        result = validate_llm_output(self.valid_output(), self.pack)
        self.assertTrue(result["valid"], result["errors"])
        self.assertIsNotNone(result["sanitized_output"])

    def test_rejects_hallucinated_destination(self):
        output = self.valid_output()
        output["selected_destination_ids"][0] = "loc_fake"
        output["destination_summaries"][0]["destination_id"] = "loc_fake"

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("not allowed" in error for error in result["errors"]))

    def test_rejects_reranking(self):
        output = self.valid_output()
        output["selected_destination_ids"] = list(reversed(output["selected_destination_ids"]))
        output["destination_summaries"] = list(reversed(output["destination_summaries"]))

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("backend rank order" in error for error in result["errors"]))

    def test_rejects_fake_price(self):
        output = self.valid_output()
        output["destination_summaries"][0]["price"] = "Rp 999.000"

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("price" in error.lower() for error in result["errors"]))

    def test_rejects_fake_distance(self):
        output = self.valid_output()
        output["answer"] = "Tempat ini hanya 9 km dari lokasi Anda."

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("distance" in error.lower() for error in result["errors"]))

    def test_rejects_unavailable_media_url(self):
        output = self.valid_output()
        output["destination_summaries"][0]["media"]["image_url"] = "https://example.com/fake.jpg"

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("media.image_url" in error for error in result["errors"]))

    def test_accepts_media_url_when_present_in_evidence(self):
        base = TestLLMEvidencePack().sample_response()
        base["recommendations"][0]["media"] = {
            "available": True,
            "image_url": "https://example.com/valid.jpg",
            "destination_url": "https://example.com/maps",
            "website": "",
            "source": "curated_dataset",
        }
        pack = build_llm_evidence_pack(base)
        candidate = pack["candidates"][0]
        practical = candidate["practical_info"]
        output = {
            "schema_version": "muterbandung.llm_output.v1",
            "answer": "Gambar tersedia di https://example.com/valid.jpg",
            "selected_destination_ids": [candidate["destination_id"]],
            "destination_summaries": [
                {
                    "destination_id": candidate["destination_id"],
                    "rank": candidate["rank"],
                    "name": candidate["name"],
                    "why": candidate["backend_reason"],
                    "price": practical["price"],
                    "opening_hours": practical["opening_hours"],
                    "distance_label": practical["distance_label"],
                    "media": candidate["media"],
                    "limitations": candidate["limitations"],
                }
            ],
            "warnings": [],
            "follow_up_question": None,
        }

        result = validate_llm_output(output, pack)

        self.assertTrue(result["valid"], result["errors"])

    def test_rejects_unsupported_facility_field(self):
        output = self.valid_output()
        output["destination_summaries"][0]["facilities"] = ["parkir luas"]

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("unsupported fields" in error for error in result["errors"]))

    def test_rejects_positive_facility_claim_without_flag(self):
        output = self.valid_output()
        output["answer"] = "Destinasi ini tersedia parkir luas."

        result = validate_llm_output(output, self.pack)

        self.assertFalse(result["valid"])
        self.assertTrue(any("parking_verified" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
