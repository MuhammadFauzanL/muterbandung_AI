import unittest

from app.main import API_SCHEMA_VERSION, app


class TestAPIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def assert_error_mentions(self, response, expected_text):
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data.get("status"), "error")
        self.assertIn("api_schema_version", data)
        self.assertIn("data_version", data)
        self.assertIn("request_id", data)
        self.assertIn("generated_at", data)
        errors = data.get("errors") or []
        self.assertTrue(
            any(expected_text in error for error in errors),
            f"Expected {expected_text!r} in errors: {errors}",
        )

    def test_malformed_json_returns_400(self):
        response = self.client.post(
            "/api/recommend",
            data="{bad",
            content_type="application/json",
        )
        self.assert_error_mentions(response, "Malformed JSON")

    def test_json_body_must_be_object(self):
        response = self.client.post("/api/recommend", json=["wisata alam"])
        self.assert_error_mentions(response, "JSON body must be an object")

    def test_invalid_contract_values_return_400(self):
        cases = [
            ({"query": "wisata malam", "open_at_hour": 20}, "open_at_hour"),
            ({"query": "wisata bandung", "max_price": -1}, "max_price"),
            ({"query": "wisata bandung", "min_rating": 99}, "min_rating"),
            ({"query": "wisata bandung", "top_k": 0}, "top_k"),
            ({"query": "wisata bandung", "sort_by": "random"}, "sort_by"),
            ({"query": "wisata bandung", "max_distance_km": 5}, "max_distance_km"),
            ({"query": "a" * 501}, "query"),
        ]
        for payload, expected_error in cases:
            with self.subTest(payload=payload):
                response = self.client.post("/api/recommend", json=payload)
                self.assert_error_mentions(response, expected_error)

    def test_string_false_boolean_is_false(self):
        response = self.client.post(
            "/api/recommend",
            json={"query": "wisata bandung", "free_only": "false", "top_k": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertFalse(data.get("manual_filters", {}).get("free_only"))

    def test_top_k_is_honored_and_metadata_present(self):
        response = self.client.post(
            "/api/recommend",
            json={"query": "wisata alam yang sejuk", "top_k": 2},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("api_schema_version"), API_SCHEMA_VERSION)
        self.assertIn("data_version", data)
        self.assertIn("request_id", data)
        self.assertIn("generated_at", data)
        self.assertLessEqual(len(data.get("recommendations", [])), 2)

    def test_open_at_hour_accepts_hh_mm_string(self):
        response = self.client.post(
            "/api/recommend",
            json={
                "query": "tempat nongkrong malam",
                "day_type": "weekend",
                "open_at_hour": "8:00",
                "top_k": 1,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("manual_filters", {}).get("open_at_hour"), "08:00")


if __name__ == "__main__":
    unittest.main()
