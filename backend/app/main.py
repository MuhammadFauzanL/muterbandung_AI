"""
FastAPI application entry-point.
Run with: uvicorn app.main:app --reload
"""

import logging
from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.api import api_router


# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ────────────────────────
@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("🚀  %s starting …", settings.app_name)
    logger.info("📦  Environment : %s", settings.app_env)
    logger.info("🗄️  Database    : %s", settings.database_url.rsplit("@", 1)[-1])
    yield
    # Shutdown
    logger.info("🛑  %s shutting down …", settings.app_name)


# ── App Factory ──────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend API untuk AI Travel Recommendation System – MuterBandung. "
        "Menyediakan endpoint untuk destinasi wisata, rekomendasi paket, "
        "dan AI chatbot berbasis evidence."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)


# ── Exception Handlers ──────────────────────────────────
register_exception_handlers(app)


# ── Routers ──────────────────────────────────────────────
app.include_router(api_router)
