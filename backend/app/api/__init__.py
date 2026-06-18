"""
API package – registers all route modules.
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.destinations import router as destinations_router
from app.api.recommendations import router as recommendations_router
from app.api.user_preferences import router as user_preferences_router
from app.api.user_favorites import router as user_favorites_router
from app.api.user_events import router as user_events_router

# ── Root API router ──────────────────────────────────────
api_router = APIRouter()

# Register sub-routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(destinations_router, tags=["Destinations"])
api_router.include_router(recommendations_router, tags=["Recommendations"])
api_router.include_router(user_preferences_router, tags=["User Preferences"])
api_router.include_router(user_favorites_router, tags=["User Favorites"])
api_router.include_router(user_events_router, tags=["User Events"])

