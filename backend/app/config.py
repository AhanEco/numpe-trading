"""Application configuration using pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./numpe.db",
        description="Async database URL. Use postgresql+asyncpg://... for production.",
    )

    # ── Security ──────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(
        default="change-me-in-production-use-a-long-random-string",
        description="Secret key used for JWT signing.",
    )
    ADMIN_PASSWORD: str = Field(
        default="admin",
        description="Admin password for settings management.",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,
        description="JWT token lifetime in minutes (default 24 hours).",
    )

    # ── External APIs ─────────────────────────────────────────────────────
    API_KEY: str = Field(
        default="",
        description="API key for market data provider.",
    )
    NEWS_API_KEY: str = Field(
        default="",
        description="API key for news data provider.",
    )

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins.",
    )

    # ── Scheduler ─────────────────────────────────────────────────────────
    UPDATE_INTERVAL_MINUTES: int = Field(
        default=30,
        description="How often (in minutes) the background data update runs.",
    )

    # ── Timezone ──────────────────────────────────────────────────────────
    TIMEZONE: str = Field(
        default="Asia/Kolkata",
        description="Application timezone.",
    )

    # ── Application ───────────────────────────────────────────────────────
    APP_NAME: str = "Numpe Trading Software"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        """Return CORS origins as a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
