"""
Tests for accommodation endpoints.
"""

from __future__ import annotations


class TestAccommodations:
    def test_list_accommodations_returns_200(self, client):
        resp = client.get("/accommodations?limit=5")
        assert resp.status_code == 200
        body = resp.json()
        assert body["statusCode"] == 200
        assert isinstance(body["data"], list)
        assert body["meta"]["limit"] == 5

    def test_accommodation_filters_returns_metadata(self, client):
        resp = client.get("/accommodations/filters")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "types" in data
        assert "priceOptions" in data
        assert "ratingOptions" in data
        assert "facilityOptions" in data
        assert "sortOptions" in data

    def test_nearby_accommodations_for_destination_returns_200(self, client):
        destinations = client.get("/destinations?limit=1").json()["data"]
        if not destinations:
            return

        slug = destinations[0]["slug"]
        resp = client.get(
            f"/destinations/{slug}/nearby-accommodations?limit=3&radiusKm=10"
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["statusCode"] == 200
        assert isinstance(body["data"], list)
        assert body["meta"]["limit"] == 3

    def test_nearby_accommodations_invalid_destination_returns_404(self, client):
        resp = client.get("/destinations/not-a-real-destination/nearby-accommodations")
        assert resp.status_code == 404
