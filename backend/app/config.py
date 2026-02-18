import json
import os

from pydantic import model_validator
from pydantic_settings import BaseSettings


def _parse_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS from env var (JSON array or comma-separated string)."""
    raw = os.environ.get("CORS_ORIGINS", "")
    if not raw:
        return ["http://localhost:3000"]
    # Try JSON array first: '["https://example.com","http://localhost:3000"]'
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [s.strip() for s in parsed if s.strip()]
    except (json.JSONDecodeError, TypeError):
        pass
    # Fall back to comma-separated: "https://example.com,http://localhost:3000"
    return [s.strip() for s in raw.split(",") if s.strip()]


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    DATABASE_URL: str = "postgresql+asyncpg://thesis:thesis_dev@localhost:5432/thesis_engine"
    DATABASE_URL_SYNC: str = "postgresql://thesis:thesis_dev@localhost:5432/thesis_engine"

    @model_validator(mode="after")
    def _fix_database_urls(self):
        # Railway provides postgresql:// but asyncpg needs postgresql+asyncpg://
        if self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL_SYNC = self.DATABASE_URL
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        return self

    REDIS_URL: str = "redis://localhost:6379/0"

    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # Yahoo Finance (free, no API key needed)
    FINANCIAL_DATA_API_KEY: str = ""  # Not needed for Yahoo Finance
    FMP_API_BASE_URL: str = "https://financialmodelingprep.com"  # Legacy, kept for compatibility

    # S3 Storage (for filing documents)
    S3_BUCKET_NAME: str = "thesis-engine-docs"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # SEC EDGAR (required for US companies)
    EDGAR_USER_AGENT: str = "ThesisEngine admin@example.com"

    # Parsed from env: JSON array or comma-separated string
    # Set CORS_ORIGINS="*" to allow all origins (dev), or
    # CORS_ORIGINS="https://your-app.vercel.app,http://localhost:3000" for production
    CORS_ORIGINS: list[str] = _parse_cors_origins()

    # API key authentication (comma-separated list of valid keys)
    # Leave empty to disable auth (open access, fine for local dev)
    API_KEYS: list[str] = []

    @model_validator(mode="after")
    def _parse_api_keys(self):
        raw = os.environ.get("API_KEYS", "")
        if raw:
            self.API_KEYS = [k.strip() for k in raw.split(",") if k.strip()]
        return self

    # Logging
    LOG_FORMAT: str = "json"  # "json" for production, "text" for dev
    LOG_LEVEL: str = "INFO"


settings = Settings()
