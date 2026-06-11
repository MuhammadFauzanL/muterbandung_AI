"""
Shared test fixtures for the backend test suite.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient that can be reused across tests in a module."""
    with TestClient(app) as c:
        yield c
