import logging

from fastapi import APIRouter, status

from app.database import engine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check - returns ok if service is running."""
    return {"status": "ok"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness check - verifies database connectivity."""
    result = {"status": "ok", "checks": {}}
    
    # Check database connectivity
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        result["checks"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        result["checks"]["database"] = "failed"
        result["status"] = "degraded"
    
    return result
