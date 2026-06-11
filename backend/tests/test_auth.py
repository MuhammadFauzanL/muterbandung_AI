"""
Tests for authentication endpoints (Phase 2).

Covers:
- POST /auth/register
- POST /auth/login
- GET  /auth/me
"""

from __future__ import annotations

from app.core.security import hash_password, verify_password, create_access_token


# ── Security Unit Tests ──────────────────────────────────


class TestPasswordHashing:
    """Verify bcrypt password hashing and verification."""

    def test_hash_password_returns_bcrypt_hash(self):
        hashed = hash_password("testpassword")
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_hash_is_unique_each_call(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # Different salts


class TestJWT:
    """Verify JWT token creation and decoding."""

    def test_create_and_decode_token(self):
        from app.core.security import decode_access_token

        token = create_access_token({"sub": "user-123", "email": "a@b.com"})
        payload = decode_access_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "a@b.com"
        assert "exp" in payload

    def test_invalid_token_raises(self):
        from app.core.security import decode_access_token
        from app.core.exceptions import UnauthorizedException
        import pytest

        with pytest.raises(UnauthorizedException):
            decode_access_token("not.a.valid.token")


# ── Register Endpoint Tests ─────────────────────────────


class TestRegister:
    """Tests for POST /auth/register."""

    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["statusCode"] == 201
        assert body["message"] == "Register success"
        assert body["data"]["name"] == "Test User"
        assert body["data"]["email"] == "testuser@example.com"
        assert body["data"]["is_active"] is True
        assert "id" in body["data"]
        assert "created_at" in body["data"]
        # Must never leak password_hash
        assert "password_hash" not in body["data"]
        assert "password" not in body["data"]

    def test_register_duplicate_email(self, client):
        payload = {
            "name": "First",
            "email": "dup@example.com",
            "password": "securepass123",
        }
        resp1 = client.post("/auth/register", json=payload)
        assert resp1.status_code == 201

        resp2 = client.post("/auth/register", json=payload)
        assert resp2.status_code == 409
        body = resp2.json()
        assert body["statusCode"] == 409
        assert body["message"] == "Email already registered"

    def test_register_short_password(self, client):
        resp = client.post("/auth/register", json={
            "name": "Short",
            "email": "short@example.com",
            "password": "abc",  # too short
        })
        assert resp.status_code == 422
        body = resp.json()
        assert body["statusCode"] == 422

    def test_register_invalid_email(self, client):
        resp = client.post("/auth/register", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "securepass123",
        })
        assert resp.status_code == 422

    def test_register_missing_name(self, client):
        resp = client.post("/auth/register", json={
            "email": "noname@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 422


# ── Login Endpoint Tests ─────────────────────────────────


class TestLogin:
    """Tests for POST /auth/login."""

    def _register(self, client, email="login@example.com"):
        client.post("/auth/register", json={
            "name": "Login User",
            "email": email,
            "password": "securepass123",
        })

    def test_login_success(self, client):
        self._register(client)
        resp = client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["statusCode"] == 200
        assert body["message"] == "Login success"
        assert "access_token" in body["data"]
        assert body["data"]["token_type"] == "bearer"
        assert body["data"]["user"]["email"] == "login@example.com"
        # Must never leak password_hash
        assert "password_hash" not in body["data"]["user"]

    def test_login_wrong_password(self, client):
        self._register(client, email="wrongpw@example.com")
        resp = client.post("/auth/login", json={
            "email": "wrongpw@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401
        body = resp.json()
        assert body["message"] == "Invalid email or password"

    def test_login_nonexistent_email(self, client):
        resp = client.post("/auth/login", json={
            "email": "ghost@example.com",
            "password": "anything",
        })
        assert resp.status_code == 401

    def test_login_response_format(self, client):
        self._register(client, email="format@example.com")
        resp = client.post("/auth/login", json={
            "email": "format@example.com",
            "password": "securepass123",
        })
        body = resp.json()
        # Standard response format
        assert "statusCode" in body
        assert "message" in body
        assert "data" in body
        # Token response shape
        data = body["data"]
        assert "access_token" in data
        assert "token_type" in data
        assert "user" in data
        # User shape
        user = data["user"]
        assert set(user.keys()) == {"id", "name", "email", "is_active", "created_at"}


# ── Me Endpoint Tests ────────────────────────────────────


class TestMe:
    """Tests for GET /auth/me."""

    def _get_token(self, client, email="me@example.com"):
        client.post("/auth/register", json={
            "name": "Me User",
            "email": email,
            "password": "securepass123",
        })
        resp = client.post("/auth/login", json={
            "email": email,
            "password": "securepass123",
        })
        return resp.json()["data"]["access_token"]

    def test_me_with_valid_token(self, client):
        token = self._get_token(client)
        resp = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["statusCode"] == 200
        assert body["message"] == "Current user retrieved successfully"
        assert body["data"]["email"] == "me@example.com"
        assert "password_hash" not in body["data"]

    def test_me_without_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)

    def test_me_with_invalid_token(self, client):
        resp = client.get("/auth/me", headers={
            "Authorization": "Bearer invalidtoken",
        })
        assert resp.status_code == 401

    def test_me_response_has_no_password(self, client):
        token = self._get_token(client, email="nopw@example.com")
        resp = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        body = resp.json()
        assert "password_hash" not in body["data"]
        assert "password" not in body["data"]
