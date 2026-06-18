"""
Tests for destination recommendation endpoints.
"""

from __future__ import annotations


def _get_token(client, email="recommend@example.com"):
    client.post("/auth/register", json={
        "name": "Recommendation User",
        "email": email,
        "password": "securepass123",
    })
    resp = client.post("/auth/login", json={
        "email": email,
        "password": "securepass123",
    })
    return resp.json()["data"]["access_token"]


def _save_preferences(client, token, payload):
    return client.put(
        "/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )


class TestDestinationRecommendations:
    """Tests for GET /recommendations/destinations."""

    def test_guest_recommendations_fallback_to_default_quality(self, client):
        resp = client.get("/recommendations/destinations?page=1&limit=5")
        assert resp.status_code == 200

        body = resp.json()
        assert body["statusCode"] == 200
        assert body["message"] == "Default recommendations retrieved successfully"
        assert isinstance(body["data"], list)
        assert body["meta"]["page"] == 1
        assert body["meta"]["limit"] == 5
        assert len(body["data"]) <= 5

    def test_invalid_token_returns_unauthorized(self, client):
        resp = client.get(
            "/recommendations/destinations",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert resp.status_code == 401

    def test_logged_in_user_without_preferences_gets_default_recommendations(self, client):
        token = _get_token(client)
        resp = client.get(
            "/recommendations/destinations?limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Default recommendations retrieved successfully"
        assert len(body["data"]) <= 3

    def test_preferences_raise_matching_destinations_with_personal_reason(self, client):
        token = _get_token(client, email="recommend-personal@example.com")
        pref_resp = _save_preferences(
            client,
            token,
            {
                "favoritePlaceTypes": ["nature"],
                "favoriteActivities": ["photo_spot"],
                "visitorTarget": "family",
                "preferredAtmospheres": ["outdoor"],
                "freeOnly": False,
            },
        )
        assert pref_resp.status_code == 200

        resp = client.get(
            "/recommendations/destinations?limit=8",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        body = resp.json()
        assert body["message"] == "Personalized recommendations retrieved successfully"
        if body["data"]:
            assert any(
                "Cocok karena kamu memilih" in item["scoreReason"]
                for item in body["data"]
            )
            assert any(
                item.get("primaryIntent") in {"Alam", "Keluarga"}
                or "Alam" in item["scoreReason"]
                or "Outdoor" in item["scoreReason"]
                for item in body["data"]
            )

    def test_free_only_preference_returns_free_destinations(self, client):
        token = _get_token(client, email="recommend-free@example.com")
        pref_resp = _save_preferences(
            client,
            token,
            {
                "favoritePlaceTypes": ["nature"],
                "favoriteActivities": ["healing"],
                "visitorTarget": "family",
                "preferredAtmospheres": ["outdoor"],
                "freeOnly": True,
            },
        )
        assert pref_resp.status_code == 200

        resp = client.get(
            "/recommendations/destinations?limit=10",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

        for item in resp.json()["data"]:
            assert item["priceLabel"] == "Gratis"
