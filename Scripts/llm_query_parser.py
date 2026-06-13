import json
import os
import re
from dataclasses import dataclass
from typing import List, Optional

import requests


DEFAULT_MODEL = "@cf/meta/llama-3.1-8b-instruct"
DEFAULT_TIMEOUT_SECONDS = 3.0


@dataclass
class QueryParserResult:
    semantic_query: Optional[str] = None
    max_price: Optional[int] = None
    categories: Optional[List[str]] = None
    free_only: Optional[bool] = None
    open_at_hour: Optional[str] = None
    confidence: Optional[str] = None
    parser_source: str = "lexical_fallback"
    parser_error: Optional[str] = None

    @property
    def ok(self):
        return self.parser_source == "cloudflare_llm" and self.parser_error is None

    def to_metadata(self):
        extracted = {
            "semantic_query": self.semantic_query,
            "max_price": self.max_price,
            "categories": self.categories or [],
            "free_only": self.free_only,
            "open_at_hour": self.open_at_hour,
            "confidence": self.confidence,
        }
        return {
            "llm_parser_used": self.ok,
            "parser_source": self.parser_source,
            "parser_error": self.parser_error,
            "extracted": extracted,
        }


class LLMQueryParser:
    """Cloudflare query parser for filter extraction, with safe local fallback."""

    def __init__(self, valid_categories, max_price=10_000_000, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
        self.valid_category_map = self._build_category_map(valid_categories)
        self.max_price = int(max_price)
        self.timeout_seconds = float(timeout_seconds)
        self.enabled = os.getenv("MUTERBANDUNG_LLM_QUERY_PARSER_ENABLED", "1").strip().lower() not in {
            "0",
            "false",
            "no",
            "off",
        }
        self.account_id = os.getenv("CF_ACCOUNT_ID") or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = os.getenv("CF_API_TOKEN") or os.getenv("CLOUDFLARE_API_TOKEN")
        self.model = os.getenv("CF_QUERY_PARSER_MODEL") or os.getenv("CF_MODEL") or DEFAULT_MODEL

    @staticmethod
    def _normalize(value):
        text = str(value or "").strip().lower()
        text = re.sub(r"\s+", " ", text)
        return text

    @classmethod
    def _build_category_map(cls, valid_categories):
        category_map = {}
        for category in valid_categories or []:
            label = str(category).strip()
            if not label:
                continue
            category_map[cls._normalize(label)] = label
            category_map[cls._normalize(label.replace("_", " "))] = label
        return category_map

    @staticmethod
    def _extract_json_object(text):
        if not isinstance(text, str):
            return None
        start = text.find("{")
        if start < 0:
            return None

        depth = 0
        in_string = False
        escape = False
        for index in range(start, len(text)):
            char = text[index]
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]
        return None

    def _sanitize_categories(self, values):
        if not isinstance(values, list):
            values = [values] if values else []
        sanitized = []
        for value in values:
            key = self._normalize(value)
            category = self.valid_category_map.get(key)
            if category and category not in sanitized:
                sanitized.append(category)
        return sanitized

    def _sanitize_payload(self, payload):
        if not isinstance(payload, dict):
            raise ValueError("parser_payload_not_object")

        semantic_query = payload.get("semantic_query")
        if not isinstance(semantic_query, str) or not semantic_query.strip():
            semantic_query = None
        else:
            semantic_query = semantic_query.strip()[:300]

        max_price = payload.get("max_price")
        if isinstance(max_price, bool):
            max_price = None
        elif max_price is not None:
            try:
                max_price = int(str(max_price).replace(".", "").replace(",", "").strip())
                if max_price < 0 or max_price > self.max_price:
                    max_price = None
            except (TypeError, ValueError):
                max_price = None

        free_only = payload.get("free_only")
        if free_only is not None and not isinstance(free_only, bool):
            free_only = None

        open_at_hour = payload.get("open_at_hour")
        if isinstance(open_at_hour, str) and re.fullmatch(r"\d{2}:[0-5]\d", open_at_hour.strip()):
            hour = int(open_at_hour[:2])
            open_at_hour = open_at_hour.strip() if hour <= 23 else None
        else:
            open_at_hour = None

        confidence = payload.get("confidence")
        if confidence not in {"low", "medium", "high"}:
            confidence = None

        return QueryParserResult(
            semantic_query=semantic_query,
            max_price=max_price,
            categories=self._sanitize_categories(payload.get("categories")),
            free_only=free_only,
            open_at_hour=open_at_hour,
            confidence=confidence,
            parser_source="cloudflare_llm",
        )

    def _build_prompt(self, query):
        valid_categories = sorted(set(self.valid_category_map.values()))
        return (
            "Anda adalah parser query MuterBandung. Tugas Anda hanya mengekstrak filter, "
            "bukan memberi rekomendasi. Jawab hanya JSON valid tanpa markdown.\n\n"
            "Schema:\n"
            "{\n"
            '  "semantic_query": string|null,\n'
            '  "max_price": integer|null,\n'
            '  "categories": string[],\n'
            '  "free_only": boolean|null,\n'
            '  "open_at_hour": "HH:MM"|null,\n'
            '  "confidence": "low"|"medium"|"high"\n'
            "}\n\n"
            f"Kategori valid: {', '.join(valid_categories)}.\n"
            "Aturan: jangan mengarang kategori di luar daftar; jika ragu kosongkan field. "
            "Contoh slang harga: cepek=100000, gocap=50000, ceban=10000.\n\n"
            f"Query user: {query}"
        )

    def parse_text_response(self, text):
        try:
            json_block = self._extract_json_object(text)
            if not json_block:
                return QueryParserResult(parser_error="json_block_not_found")
            payload = json.loads(json_block)
            return self._sanitize_payload(payload)
        except Exception as exc:
            return QueryParserResult(parser_error=f"parse_error:{type(exc).__name__}")

    def parse(self, query):
        if not isinstance(query, str) or not query.strip():
            return QueryParserResult(parser_source="not_called", parser_error="empty_query")
        if not self.enabled:
            return QueryParserResult(parser_source="lexical_fallback", parser_error="parser_disabled")
        if not self.account_id or not self.api_token:
            return QueryParserResult(parser_source="lexical_fallback", parser_error="cloudflare_config_missing")

        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Anda hanya mengekstrak JSON filter untuk sistem rekomendasi wisata.",
                },
                {"role": "user", "content": self._build_prompt(query)},
            ],
            "max_tokens": 256,
            "temperature": 0,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
            data = response.json()
            if response.status_code != 200 or not data.get("success"):
                return QueryParserResult(parser_error=f"cloudflare_status_{response.status_code}")
            content = (data.get("result") or {}).get("response")
            result = self.parse_text_response(content)
            if result.ok:
                return result
            result.parser_source = "lexical_fallback"
            return result
        except requests.exceptions.Timeout:
            return QueryParserResult(parser_error="cloudflare_timeout")
        except Exception as exc:
            return QueryParserResult(parser_error=f"cloudflare_error:{type(exc).__name__}")
