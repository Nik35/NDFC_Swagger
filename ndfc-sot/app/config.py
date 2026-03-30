"""Application configuration via environment variables."""

from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """App settings loaded from env vars / .env file.

    Environment variables are prefixed with ``NDFC_SOT_`` — e.g.
    ``NDFC_SOT_API_KEY``, ``NDFC_SOT_DATABASE_URL``.
    """

    model_config = SettingsConfigDict(
        env_prefix="NDFC_SOT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database (async) ─────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ndfc_sot"

    # ── Auth ─────────────────────────────────────────────────────
    # API Key — read from NDFC_SOT_API_KEY env var
    # Supports comma-separated list: "KEY1,KEY2"
    API_KEYS: list[str] = ["dev-api-key-change-in-production"]

    @field_validator("API_KEYS", mode="before")
    @classmethod
    def parse_api_keys(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    # ── NDFC Connection (optional) ───────────────────────────────
    NDFC_URL: Optional[str] = None
    NDFC_USERNAME: Optional[str] = None
    NDFC_PASSWORD: Optional[str] = None
    NDFC_VERIFY_SSL: bool = False

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "NDFC Source-of-Truth API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def sync_database_url(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "")


settings = Settings()
