import json
import re
import unittest
from pathlib import Path

from Scripts.app import app


SNAPSHOT_PATH = Path("Dataset/4_Evaluation/api_schema_snapshot.json")
ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$")


def sorted_keys(value):
    return sorted((value or {}).keys())


class TestAPISchemaSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls.snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))

    def assert_keys_match(self, actual, expected, label):
        self.assertEqual(
            sorted_keys(actual),
            sorted(expected),
            f"{label} schema drifted. Update {SNAPSHOT_PATH} only after reviewing compatibility.",
        )

    def test_recommend_success_schema_matches_snapshot(self):
        response = self.client.post(
            "/api/recommend",
            json=self.snapshot["recommend_request"],
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assert_keys_match(data, self.snapshot["top_level_keys"], "top-level response")
        self.assertEqual(
            data["api_schema_version"],
            self.snapshot["expected_schema_versions"]["api_schema_version"],
        )
        self.assertRegex(data["generated_at"], ISO_UTC_RE)
        self.assertIsInstance(data["request_id"], str)
        self.assertTrue(data["request_id"])
        self.assertIsInstance(data["data_version"], str)
        self.assertTrue(data["data_version"])
        self.assertEqual(data["status"], "success")
        self.assertLessEqual(len(data["recommendations"]), self.snapshot["recommend_request"]["top_k"])
        self.assertGreater(len(data["recommendations"]), 0)

        item = data["recommendations"][0]
        self.assert_keys_match(item, self.snapshot["recommendation_keys"], "recommendation item")
        for field, expected_keys in self.snapshot["recommendation_nested_keys"].items():
            self.assert_keys_match(item[field], expected_keys, f"recommendation.{field}")

        pack = data["llm_evidence_pack"]
        self.assert_keys_match(pack, self.snapshot["llm_evidence_pack_keys"], "llm_evidence_pack")
        self.assertEqual(
            pack["schema_version"],
            self.snapshot["expected_schema_versions"]["llm_evidence_pack"],
        )
        for field in ("ranking_policy", "input_context", "source_fields"):
            self.assert_keys_match(
                pack[field],
                self.snapshot["llm_evidence_pack_nested_keys"][field],
                f"llm_evidence_pack.{field}",
            )
        self.assertGreater(len(pack["candidates"]), 0)
        candidate = pack["candidates"][0]
        self.assert_keys_match(
            candidate,
            self.snapshot["llm_evidence_pack_nested_keys"]["candidate"],
            "llm_evidence_pack.candidate",
        )
        self.assert_keys_match(
            candidate["practical_info"],
            self.snapshot["llm_evidence_pack_nested_keys"]["candidate_practical_info"],
            "llm_evidence_pack.candidate.practical_info",
        )
        self.assert_keys_match(
            candidate["sentiment"],
            self.snapshot["llm_evidence_pack_nested_keys"]["candidate_sentiment"],
            "llm_evidence_pack.candidate.sentiment",
        )
        self.assert_keys_match(
            candidate["media"],
            self.snapshot["llm_evidence_pack_nested_keys"]["candidate_media"],
            "llm_evidence_pack.candidate.media",
        )

        guard = data["llm_prompt_guard"]
        self.assert_keys_match(guard, self.snapshot["llm_prompt_guard_keys"], "llm_prompt_guard")
        self.assertEqual(
            guard["schema_version"],
            self.snapshot["expected_schema_versions"]["llm_prompt_guard"],
        )
        self.assertEqual(
            guard["output_schema_version"],
            self.snapshot["expected_schema_versions"]["llm_output"],
        )
        self.assert_keys_match(
            guard["output_contract"],
            self.snapshot["llm_prompt_guard_nested_keys"]["output_contract"],
            "llm_prompt_guard.output_contract",
        )

    def test_recommend_error_schema_matches_snapshot(self):
        response = self.client.post("/api/recommend", data="{bad", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assert_keys_match(data, self.snapshot["error_top_level_keys"], "error response")
        self.assertEqual(data["status"], "error")
        self.assertIsInstance(data["errors"], list)
        self.assertTrue(data["errors"])
        self.assertEqual(
            data["api_schema_version"],
            self.snapshot["expected_schema_versions"]["api_schema_version"],
        )
        self.assertRegex(data["generated_at"], ISO_UTC_RE)


if __name__ == "__main__":
    unittest.main()
