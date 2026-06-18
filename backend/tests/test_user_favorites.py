"""
Tests for user favorites endpoints: GET/POST/DELETE /me/favorites.
"""

import pytest

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
FAVORITES_URL = "/me/favorites"


def _register_and_login(client, email: str):
    """Helper: register user and return Bearer token."""
    client.post(
        REGISTER_URL,
        json={"name": "Fav User", "email": email, "password": "pass1234"},
    )
    resp = client.post(LOGIN_URL, json={"email": email, "password": "pass1234"})
    return resp.json()["data"]["access_token"]


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


class TestUserFavorites:
    """Favorite CRUD tests."""

    def test_get_favorites_empty(self, client):
        token = _register_and_login(client, "fav-empty@example.com")
        resp = client.get(FAVORITES_URL, headers=_auth_headers(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []
        assert body["meta"]["total"] == 0

    def test_add_favorite_invalid_destination(self, client):
        token = _register_and_login(client, "fav-invalid@example.com")
        resp = client.post(
            f"{FAVORITES_URL}/LOC-NONEXISTENT",
            headers=_auth_headers(token),
        )
        assert resp.status_code == 404

    def test_add_and_get_favorite(self, client):
        token = _register_and_login(client, "fav-add@example.com")

        # We need a real destination. Get one from /destinations/popular.
        pop_resp = client.get("/destinations/popular?limit=1")
        destinations = pop_resp.json().get("data", [])
        if not destinations:
            pytest.skip("No active destinations in DB")
        dest_id = destinations[0]["id"]

        # Add to favorites
        add_resp = client.post(
            f"{FAVORITES_URL}/{dest_id}",
            headers=_auth_headers(token),
        )
        assert add_resp.status_code == 200 or add_resp.status_code == 201
        # Idempotent: adding again should still succeed
        add_resp2 = client.post(
            f"{FAVORITES_URL}/{dest_id}",
            headers=_auth_headers(token),
        )
        assert add_resp2.status_code in (200, 201)

        # Check it appears in list
        list_resp = client.get(FAVORITES_URL, headers=_auth_headers(token))
        assert list_resp.status_code == 200
        items = list_resp.json()["data"]
        assert any(item["id"] == dest_id for item in items)
        assert all(item.get("isFavorite") is True for item in items)

    def test_remove_favorite(self, client):
        token = _register_and_login(client, "fav-remove@example.com")

        pop_resp = client.get("/destinations/popular?limit=1")
        destinations = pop_resp.json().get("data", [])
        if not destinations:
            pytest.skip("No active destinations in DB")
        dest_id = destinations[0]["id"]

        # Add then remove
        client.post(
            f"{FAVORITES_URL}/{dest_id}",
            headers=_auth_headers(token),
        )
        del_resp = client.delete(
            f"{FAVORITES_URL}/{dest_id}",
            headers=_auth_headers(token),
        )
        assert del_resp.status_code == 200

        # Should be gone from list
        list_resp = client.get(FAVORITES_URL, headers=_auth_headers(token))
        items = list_resp.json()["data"]
        assert not any(item["id"] == dest_id for item in items)

    def test_favorites_requires_auth(self, client):
        resp = client.get(FAVORITES_URL)
        assert resp.status_code in (401, 403)

    def test_is_favorite_in_recommendations(self, client):
        """is_favorite should be True in recommendation cards for favorited dests."""
        token = _register_and_login(client, "fav-rec@example.com")

        pop_resp = client.get("/destinations/popular?limit=1")
        destinations = pop_resp.json().get("data", [])
        if not destinations:
            pytest.skip("No active destinations in DB")
        dest_id = destinations[0]["id"]

        # Favorite it
        client.post(
            f"{FAVORITES_URL}/{dest_id}",
            headers=_auth_headers(token),
        )

        # Check recommendation endpoint
        rec_resp = client.get(
            "/recommendations/destinations?limit=50",
            headers=_auth_headers(token),
        )
        assert rec_resp.status_code == 200
        rec_items = rec_resp.json()["data"]
        favorited = [item for item in rec_items if item["id"] == dest_id]
        if favorited:
            assert favorited[0].get("isFavorite") is True
