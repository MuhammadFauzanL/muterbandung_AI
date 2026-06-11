"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""

# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict  


class Settings(BaseSettings):
    """Central configuration for the application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────
    app_name: str = "AI Travel Recommendation Backend"
    app_env: str = "development"
    app_debug: bool = True

    # ── Database ─────────────────────────────────────────
    database_url: str = "postgresql://postgres:postgres@localhost:5432/muterbdg_db"

    # ── JWT (Phase 2) ────────────────────────────────────
    jwt_secret_key: str = "change_this_later"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── CORS / Frontend ──────────────────────────────────
    frontend_url: str = "http://localhost:3000"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


# Singleton instance – import this wherever config is needed.
settings = Settings()
