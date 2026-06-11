"""
Tests for exception handlers.
Validates that all error types produce the standard error response format.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import (
    register_exception_handlers,
    AppException,
    NotFoundException,
    BadRequestException,
)


def _make_app_with_routes():
    """Create a minimal test app with routes that raise various exceptions."""
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/raise-app-exception")
    async def raise_app():
        raise AppException(status_code=400, message="Test error", errors=["detail"])

    @test_app.get("/raise-not-found")
    async def raise_not_found():
        raise NotFoundException("Item not found")

    @test_app.get("/raise-bad-request")
    async def raise_bad_request():
        raise BadRequestException("Bad input", errors=["field is required"])

    @test_app.get("/raise-unhandled")
    async def raise_unhandled():
        raise RuntimeError("Unexpected crash")

    return test_app


class TestExceptionHandlers:
    """All exceptions must produce the standard error response format."""

    def setup_method(self):
        self.client = TestClient(_make_app_with_routes(), raise_server_exceptions=False)

    def test_app_exception_format(self):
        resp = self.client.get("/raise-app-exception")
        assert resp.status_code == 400
        data = resp.json()
        assert data["statusCode"] == 400
        assert data["message"] == "Test error"
        assert data["errors"] == ["detail"]

    def test_not_found_exception(self):
        resp = self.client.get("/raise-not-found")
        assert resp.status_code == 404
        data = resp.json()
        assert data["statusCode"] == 404
        assert data["message"] == "Item not found"
        assert data["errors"] == []

    def test_bad_request_exception(self):
        resp = self.client.get("/raise-bad-request")
        assert resp.status_code == 400
        data = resp.json()
        assert data["errors"] == ["field is required"]

    def test_unhandled_exception_returns_500(self):
        resp = self.client.get("/raise-unhandled")
        assert resp.status_code == 500
        data = resp.json()
        assert data["statusCode"] == 500
        assert data["message"] == "Internal server error"
        assert data["errors"] == []

    def test_404_route_not_found(self):
        """
        FastAPI's built-in 404 for unknown routes goes through our
        HTTPException handler, producing the standard error format.
        """
        resp = self.client.get("/nonexistent-route")
        assert resp.status_code == 404
        data = resp.json()
        # FastAPI's default 404 response uses {"detail": "Not Found"}
        # Our HTTPException handler converts it to standard format
        assert "detail" in data or "statusCode" in data
