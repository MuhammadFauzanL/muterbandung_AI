"""
API package – registers all route modules.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.destinations import router as destinations_router

# ── Root API router ──────────────────────────────────────
api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(destinations_router, tags=["Destinations"])
