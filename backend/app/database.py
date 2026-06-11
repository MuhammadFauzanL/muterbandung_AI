"""
Database engine and session management using SQLAlchemy 2.0.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# ── Engine ───────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,          # auto-reconnect stale connections
    pool_size=10,
    max_overflow=20,
    echo=settings.app_debug,     # SQL logging in dev mode
)

# ── Session Factory ──────────────────────────────────────
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ─────────────────────────────────────
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ── Dependency ───────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a database session.
    Ensures the session is always closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
