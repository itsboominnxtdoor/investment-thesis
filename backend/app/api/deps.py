"""FastAPI dependencies for authentication and authorization."""

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str | None = Security(api_key_header)) -> str | None:
    """Verify API key from X-API-Key header.

    If no API_KEYS are configured, auth is disabled (open access).
    """
    if not settings.API_KEYS:
        return None  # Auth disabled

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    if api_key not in settings.API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key")

    return api_key
