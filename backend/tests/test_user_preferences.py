"""
Tests for user preference onboarding endpoints.
"""

from __future__ import annotations


def _get_token(client, email="pref@example.com"):
    client.post("/auth/register", json={
        "name": "Preference User",
        "email": email,
        "password": "securepass123",
    })
    resp = client.post("/auth/login", json={
        "email": email,
        "password": "securepass123",
    })
    return resp.json()["data"]["access_token"]


class TestUserPreferences:
    """Tests for GET/PUT /me/preferences."""

    def test_put_preferences_without_token_returns_unauthorized(self, client):
        resp = client.put("/me/preferences", json={
            "favoritePlaceTypes": ["nature"],
            "favoriteActivities": ["healing"],
            "visitorTarget": "family",
            "preferredAtmospheres": ["outdoor"],
            "freeOnly": False,
        })
        assert resp.status_code in (401, 403)

    def test_put_preferences_with_valid_token_saves(self, client):
        token = _get_token(client)
        resp = client.put(
            "/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "favoritePlaceTypes": ["nature", "culinary"],
                "favoriteActivities": ["healing"],
                "visitorTarget": "family",
                "preferredAtmospheres": ["outdoor"],
                "freeOnly": True,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "User preferences saved successfully"
        assert body["data"]["favoritePlaceTypes"] == ["nature", "culinary"]
        assert body["data"]["favoriteActivities"] == ["healing"]
        assert body["data"]["visitorTarget"] == "family"
        assert body["data"]["preferredAtmospheres"] == ["outdoor"]
        assert body["data"]["freeOnly"] is True

    def test_get_preferences_returns_current_user_preferences(self, client):
        token = _get_token(client, email="pref2@example.com")
        client.put(
            "/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "favoritePlaceTypes": ["education"],
                "favoriteActivities": ["photo_spot"],
                "visitorTarget": "child_friendly",
                "preferredAtmospheres": ["indoor"],
                "freeOnly": False,
            },
        )

        resp = client.get(
            "/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["favoritePlaceTypes"] == ["education"]
        assert body["data"]["visitorTarget"] == "child_friendly"

    def test_get_preferences_is_scoped_to_current_user(self, client):
        owner_token = _get_token(client, email="pref-owner@example.com")
        other_token = _get_token(client, email="pref-other@example.com")

        client.put(
            "/me/preferences",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={
                "favoritePlaceTypes": ["nature"],
                "favoriteActivities": ["healing"],
                "visitorTarget": "family",
                "preferredAtmospheres": ["outdoor"],
                "freeOnly": True,
            },
        )

        resp = client.get(
            "/me/preferences",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["data"] is None

    def test_preferences_over_max_place_types_returns_validation_error(self, client):
        token = _get_token(client, email="pref-overflow@example.com")
        resp = client.put(
            "/me/preferences",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "favoritePlaceTypes": ["nature", "culinary", "shopping", "history"],
                "favoriteActivities": ["healing"],
                "visitorTarget": "family",
                "preferredAtmospheres": ["outdoor"],
                "freeOnly": False,
            },
        )
        assert resp.status_code == 422
