"""
Tests for user event tracking: POST /me/events.
"""

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"
EVENTS_URL = "/me/events"


def _register_and_login(client, email: str):
    client.post(
        REGISTER_URL,
        json={"name": "Event User", "email": email, "password": "pass1234"},
    )
    resp = client.post(LOGIN_URL, json={"email": email, "password": "pass1234"})
    return resp.json()["data"]["access_token"]


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


class TestUserEvents:
    """Event tracking tests."""

    def test_track_view_detail(self, client):
        token = _register_and_login(client, "evt-view@example.com")

        pop_resp = client.get("/destinations/popular?limit=1")
        destinations = pop_resp.json().get("data", [])
        dest_id = destinations[0]["id"] if destinations else "LOC-001"

        resp = client.post(
            EVENTS_URL,
            json={
                "event_type": "view_detail",
                "destination_id": dest_id,
            },
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200 or resp.status_code == 201

    def test_track_search_without_destination(self, client):
        token = _register_and_login(client, "evt-search@example.com")
        resp = client.post(
            EVENTS_URL,
            json={
                "event_type": "search",
                "metadata": {"query": "wisata alam"},
            },
            headers=_auth_headers(token),
        )
        assert resp.status_code in (200, 201)

    def test_track_planner_add(self, client):
        token = _register_and_login(client, "evt-planner@example.com")

        pop_resp = client.get("/destinations/popular?limit=1")
        destinations = pop_resp.json().get("data", [])
        dest_id = destinations[0]["id"] if destinations else "LOC-001"

        resp = client.post(
            EVENTS_URL,
            json={
                "event_type": "planner_add",
                "destination_id": dest_id,
            },
            headers=_auth_headers(token),
        )
        assert resp.status_code in (200, 201)

    def test_invalid_event_type(self, client):
        token = _register_and_login(client, "evt-invalid@example.com")
        resp = client.post(
            EVENTS_URL,
            json={"event_type": "invalid_type"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 422

    def test_events_requires_auth(self, client):
        resp = client.post(
            EVENTS_URL,
            json={"event_type": "view_detail", "destination_id": "LOC-001"},
        )
        assert resp.status_code in (401, 403)
