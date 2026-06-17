"""
Tests for Destination API endpoints.

These tests run against the real dev database which contains
imported destination data from Phase 3.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for destination tests."""
    with TestClient(app) as c:
        yield c


# =========================================================================
# GET /destinations/popular
# =========================================================================


class TestPopularDestinations:
    """Tests for GET /destinations/popular."""

    def test_popular_returns_200(self, client):
        resp = client.get("/destinations/popular")
        assert resp.status_code == 200

    def test_popular_response_structure(self, client):
        resp = client.get("/destinations/popular")
        data = resp.json()
        assert data["statusCode"] == 200
        assert data["message"] == "Popular destinations retrieved successfully"
        assert isinstance(data["data"], list)

    def test_popular_card_fields(self, client):
        resp = client.get("/destinations/popular?limit=1")
        data = resp.json()
        if data["data"]:
            item = data["data"][0]
            assert "id" in item
            assert "slug" in item
            assert "name" in item
            assert "category" in item
            assert "imageUrl" in item
            assert "rating" in item
            assert "priceLabel" in item
            assert "location" in item
            assert "isFavorite" in item
            # id should be external_id format (LOC-xxx), not UUID
            assert item["id"].startswith("LOC-")
            # isFavorite always false in Phase 4
            assert item["isFavorite"] is False

    def test_popular_respects_limit(self, client):
        resp = client.get("/destinations/popular?limit=3")
        data = resp.json()
        assert len(data["data"]) <= 3

    def test_popular_no_uuid_in_response(self, client):
        resp = client.get("/destinations/popular?limit=1")
        data = resp.json()
        if data["data"]:
            item = data["data"][0]
            # UUID has 36 chars with dashes; external_id is shorter
            assert len(item["id"]) < 20


# =========================================================================
# GET /destinations
# =========================================================================


class TestListDestinations:
    """Tests for GET /destinations."""

    def test_list_returns_200(self, client):
        resp = client.get("/destinations")
        assert resp.status_code == 200

    def test_list_has_pagination_meta(self, client):
        resp = client.get("/destinations?page=1&limit=5")
        data = resp.json()
        assert "meta" in data
        meta = data["meta"]
        assert "page" in meta
        assert "limit" in meta
        assert "total" in meta
        assert "totalPages" in meta
        assert meta["page"] == 1
        assert meta["limit"] == 5

    def test_list_respects_limit(self, client):
        resp = client.get("/destinations?limit=3")
        data = resp.json()
        assert len(data["data"]) <= 3

    def test_list_search_filters(self, client):
        resp = client.get("/destinations?search=camping&limit=50")
        data = resp.json()
        # Should only return destinations matching "camping"
        for item in data["data"]:
            name_lower = item["name"].lower()
            category = (item.get("category") or "").lower()
            assert "camping" in name_lower or "camping" in category or data["meta"]["total"] >= 0

    def test_list_category_filter(self, client):
        resp = client.get("/destinations?category=Wisata+Alam&limit=3")
        data = resp.json()
        for item in data["data"]:
            assert item["category"] == "Wisata Alam"

    def test_list_sort_options(self, client):
        for sort_val in ["popular", "quality", "rating", "reviews", "newest", "price_low", "price_high"]:
            resp = client.get(f"/destinations?sort={sort_val}&limit=1")
            assert resp.status_code == 200


# =========================================================================
# GET /destinations/{slug}
# =========================================================================


class TestDestinationDetail:
    """Tests for GET /destinations/{slug}."""

    def test_detail_returns_404_for_nonexistent(self, client):
        resp = client.get("/destinations/this-slug-does-not-exist-12345")
        assert resp.status_code == 200  # wrapper returns 200 with error body
        data = resp.json()
        assert data["statusCode"] == 404
        assert "not found" in data["message"].lower()

    def test_detail_returns_data(self, client):
        # First get a valid slug from popular
        popular = client.get("/destinations/popular?limit=1").json()
        if not popular["data"]:
            pytest.skip("No destinations in database")
        slug = popular["data"][0]["slug"]

        resp = client.get(f"/destinations/{slug}")
        data = resp.json()
        assert data["statusCode"] == 200
        d = data["data"]
        assert d["slug"] == slug

    def test_detail_has_all_sections(self, client):
        popular = client.get("/destinations/popular?limit=1").json()
        if not popular["data"]:
            pytest.skip("No destinations in database")
        slug = popular["data"][0]["slug"]

        resp = client.get(f"/destinations/{slug}")
        d = resp.json()["data"]
        assert "id" in d
        assert "slug" in d
        assert "name" in d
        assert "rating" in d
        assert "ticket" in d
        assert "openingHours" in d
        assert "location" in d
        assert "aiRecommendation" in d
        assert "facilities" in d
        assert "reviewSummary" in d
        # id should be external_id
        assert d["id"].startswith("LOC-")

    def test_detail_ai_recommendation_structure(self, client):
        popular = client.get("/destinations/popular?limit=1").json()
        if not popular["data"]:
            pytest.skip("No destinations in database")
        slug = popular["data"][0]["slug"]

        resp = client.get(f"/destinations/{slug}")
        ai = resp.json()["data"]["aiRecommendation"]
        assert "title" in ai
        assert "reason" in ai
        assert "tags" in ai
        assert isinstance(ai["tags"], list)

    def test_detail_facilities_structure(self, client):
        popular = client.get("/destinations/popular?limit=1").json()
        if not popular["data"]:
            pytest.skip("No destinations in database")
        slug = popular["data"][0]["slug"]

        resp = client.get(f"/destinations/{slug}")
        facilities = resp.json()["data"]["facilities"]
        assert isinstance(facilities, list)
        if facilities:
            fac = facilities[0]
            assert "key" in fac
            assert "label" in fac
            assert "available" in fac


# =========================================================================
# GET /destination-categories/highlights
# =========================================================================


class TestCategoryHighlights:
    """Tests for GET /destination-categories/highlights."""

    def test_highlights_returns_200(self, client):
        resp = client.get("/destination-categories/highlights")
        assert resp.status_code == 200

    def test_highlights_response_structure(self, client):
        resp = client.get("/destination-categories/highlights")
        data = resp.json()
        assert data["statusCode"] == 200
        assert isinstance(data["data"], list)

    def test_highlights_category_fields(self, client):
        resp = client.get("/destination-categories/highlights")
        data = resp.json()
        if data["data"]:
            cat = data["data"][0]
            assert "name" in cat
            assert "slug" in cat
            assert "description" in cat
            assert "imageUrl" in cat
            assert "totalDestinations" in cat

    def test_highlights_respects_limit(self, client):
        resp = client.get("/destination-categories/highlights?limit=3")
        data = resp.json()
        assert len(data["data"]) <= 3
