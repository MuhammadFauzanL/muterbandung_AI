"""
Shared test fixtures for the backend test suite.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User


@pytest.fixture(scope="module")
def client():
    """Create a TestClient that can be reused across tests in a module."""
    with TestClient(app) as c:
        yield c
    # Cleanup: remove any test users created during the module
    _cleanup_test_users()


def _cleanup_test_users():
    """Remove users with test email addresses from the database."""
    db = SessionLocal()
    try:
        test_emails = [
            "testuser@example.com",
            "dup@example.com",
            "short@example.com",
            "noname@example.com",
            "login@example.com",
            "wrongpw@example.com",
            "ghost@example.com",
            "format@example.com",
            "me@example.com",
            "nopw@example.com",
            "pref@example.com",
            "pref2@example.com",
            "pref-owner@example.com",
            "pref-other@example.com",
            "pref-overflow@example.com",
            "recommend@example.com",
            "recommend-personal@example.com",
            "recommend-free@example.com",
        ]
        db.query(User).filter(User.email.in_(test_emails)).delete(
            synchronize_session=False
        )
        db.commit()
    finally:
        db.close()
