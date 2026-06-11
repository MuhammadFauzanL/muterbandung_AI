"""
API package – registers all route modules.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.api.health import router as health_router

# ── Root API router ──────────────────────────────────────
api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router, tags=["Health"])

# Phase 2+: add more routers here, e.g.:
# from app.api.auth import router as auth_router
# api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
