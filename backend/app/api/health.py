"""
Health check endpoint.
Used by monitoring, load balancers, and frontend to verify backend status.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from sqlalchemy import text 

from app.database import SessionLocal
from app.utils.response import success_response

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check – confirms the backend service is running
    and the database connection is alive.
    """
    # Attempt a lightweight DB query
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "unavailable"

    return success_response(
        message="Backend is running",
        data={
            "service": "AI Travel Recommendation Backend",
            "status": "ok",
            "database": db_status,
        },
    )
