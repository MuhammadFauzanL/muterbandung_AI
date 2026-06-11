"""
Contract tests for health check endpoints.
Validates response schema, status codes, and required fields.
"""


class TestHealthEndpoint:
    """Tests for GET /health (combined check)."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_schema(self, client):
        """Response must follow the standard success format."""
        data = client.get("/health").json()
        assert "statusCode" in data
        assert "message" in data
        assert "data" in data

    def test_health_response_values(self, client):
        data = client.get("/health").json()
        assert data["statusCode"] == 200
        assert data["message"] == "Backend is running"
        assert data["data"]["service"] == "AI Travel Recommendation Backend"
        assert data["data"]["status"] == "ok"
        assert data["data"]["database"] in ("ok", "unavailable")


class TestLivenessEndpoint:
    """Tests for GET /health/live (liveness probe)."""

    def test_liveness_returns_200(self, client):
        response = client.get("/health/live")
        assert response.status_code == 200

    def test_liveness_response_schema(self, client):
        data = client.get("/health/live").json()
        assert data["statusCode"] == 200
        assert data["data"]["status"] == "ok"
        # Liveness must NOT include database field
        assert "database" not in data["data"]


class TestReadinessEndpoint:
    """Tests for GET /health/ready (readiness probe)."""

    def test_readiness_response_has_standard_schema(self, client):
        """Readiness always returns standard format, regardless of status."""
        data = client.get("/health/ready").json()
        assert "statusCode" in data
        assert "message" in data


class TestSwaggerDocs:
    """Ensure API documentation endpoints are accessible."""

    def test_docs_returns_200(self, client):
        assert client.get("/docs").status_code == 200

    def test_redoc_returns_200(self, client):
        assert client.get("/redoc").status_code == 200

    def test_openapi_json_returns_200(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert data["info"]["title"] == "AI Travel Recommendation Backend"
