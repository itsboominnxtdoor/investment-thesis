from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    DATABASE_URL: str = "postgresql+asyncpg://thesis:thesis_dev@localhost:5432/thesis_engine"
    DATABASE_URL_SYNC: str = "postgresql://thesis:thesis_dev@localhost:5432/thesis_engine"
    REDIS_URL: str = "redis://localhost:6379/0"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"

    S3_BUCKET_NAME: str = "thesis-engine-docs"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    EDGAR_USER_AGENT: str = "ThesisEngine admin@example.com"
    FINANCIAL_DATA_API_KEY: str = ""
    FMP_API_BASE_URL: str = "https://financialmodelingprep.com"

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
