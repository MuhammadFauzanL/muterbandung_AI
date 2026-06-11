"""
Health check endpoints.

- /health/live   — Liveness: confirms the process is running (for k8s/load balancers).
- /health/ready  — Readiness: confirms dependencies (DB) are reachable.
- /health        — Combined check (backward-compatible).
"""

import logging

# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from sqlalchemy import text

from app.database import SessionLocal
from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter()


def _check_database() -> bool:
    """Return True if the database is reachable."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as exc:
        logger.warning("Database health check failed: %s", exc)
        return False


@router.get("/health/live")
async def liveness():
    """
    Liveness probe — always returns 200 if the process is up.
    Does NOT check external dependencies.
    """
    return success_response(
        message="Backend is running",
        data={
            "service": "AI Travel Recommendation Backend",
            "status": "ok",
        },
    )


@router.get("/health/ready")
async def readiness():
    """
    Readiness probe — returns 200 only if ALL dependencies are healthy.
    Returns 503 if any dependency is unavailable.
    """
    db_ok = _check_database()

    if not db_ok:
        return error_response(
            message="Service not ready",
            status_code=503,
            errors=[{"dependency": "database", "status": "unavailable"}],
        )

    return success_response(
        message="Service is ready",
        data={
            "service": "AI Travel Recommendation Backend",
            "status": "ok",
            "database": "ok",
        },
    )


@router.get("/health")
async def health_check():
    """
    Combined health check (backward-compatible).
    Always returns HTTP 200 but reports dependency status in the body.
    """
    db_ok = _check_database()

    return success_response(
        message="Backend is running",
        data={
            "service": "AI Travel Recommendation Backend",
            "status": "ok",
            "database": "ok" if db_ok else "unavailable",
        },
    )
