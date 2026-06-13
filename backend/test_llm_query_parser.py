import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.services.llm_query_parser import LLMQueryParser


VALID_CATEGORIES = [
    "alam",
    "budaya",
    "kuliner",
    "ramah anak",
    "edukasi",
    "malam",
]


class TestLLMQueryParser(unittest.TestCase):
    def setUp(self):
        self.original_env = {
            key: os.environ.get(key)
            for key in [
                "CF_ACCOUNT_ID",
                "CF_API_TOKEN",
                "CLOUDFLARE_ACCOUNT_ID",
                "CLOUDFLARE_API_TOKEN",
                "MUTERBANDUNG_LLM_QUERY_PARSER_ENABLED",
            ]
        }
        for key in self.original_env:
            os.environ.pop(key, None)

    def tearDown(self):
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_parse_text_response_sanitizes_json_and_categories(self):
        parser = LLMQueryParser(valid_categories=VALID_CATEGORIES, max_price=10_000_000)
        result = parser.parse_text_response(
            """
            Berikut hasilnya:
            {"semantic_query":"wisata alam ramah anak","max_price":100000,
             "categories":["alam","Ramah Anak","Kategori Palsu"],
             "free_only":false,"open_at_hour":"20:00","confidence":"high"}
            """
        )

        self.assertTrue(result.ok)
        self.assertEqual(result.semantic_query, "wisata alam ramah anak")
        self.assertEqual(result.max_price, 100000)
        self.assertEqual(result.categories, ["alam", "ramah anak"])
        self.assertFalse(result.free_only)
        self.assertEqual(result.open_at_hour, "20:00")
        self.assertEqual(result.confidence, "high")

    def test_parse_falls_back_when_cloudflare_config_missing(self):
        parser = LLMQueryParser(valid_categories=VALID_CATEGORIES, max_price=10_000_000)
        result = parser.parse("wisata alam murah buat anak jangan lebih dari cepek")

        self.assertFalse(result.ok)
        self.assertEqual(result.parser_source, "lexical_fallback")
        self.assertEqual(result.parser_error, "cloudflare_config_missing")

    def test_invalid_price_and_invalid_hour_are_ignored(self):
        parser = LLMQueryParser(valid_categories=VALID_CATEGORIES, max_price=10_000_000)
        result = parser.parse_text_response(
            '{"semantic_query":"wisata malam","max_price":999999999,'
            '"categories":["malam"],"open_at_hour":"27:00","confidence":"medium"}'
        )

        self.assertTrue(result.ok)
        self.assertIsNone(result.max_price)
        self.assertIsNone(result.open_at_hour)
        self.assertEqual(result.categories, ["malam"])


if __name__ == "__main__":
    unittest.main()
