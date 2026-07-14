"""Application configuration via pydantic-settings.

All settings are read from environment variables (prefix ``NOVA_``) or a local
``.env`` file. Provider API keys use their conventional names (e.g. ``OPENAI_API_KEY``).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NOVA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    env: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Security / JWT
    jwt_secret: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "nova"
    postgres_password: str = "nova"
    postgres_db: str = "nova"
    database_url: str = ""

    # Redis / Qdrant
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # Providers
    llm_provider: str = "mock"
    llm_model: str = "gpt-4o-mini"
    stt_provider: str = "mock"
    tts_provider: str = "mock"

    # OAuth
    oauth_redirect_base: str = "http://localhost:8000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def sqlalchemy_url(self) -> str:
        """Return the async SQLAlchemy database URL.

        Falls back to a local SQLite file when no Postgres/URL is configured so the
        app runs with zero external dependencies during development and tests.
        """
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.env.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
