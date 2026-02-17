from pydantic import model_validator
from pydantic_settings import BaseSettings


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

    S3_BUCKET_NAME: str = "thesis-engine-docs"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    EDGAR_USER_AGENT: str = "ThesisEngine admin@example.com"
    FINANCIAL_DATA_API_KEY: str = ""
    FMP_API_BASE_URL: str = "https://financialmodelingprep.com"

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


settings = Settings()
