import json
import logging
import sys
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import business_profiles, companies, documents, financials, health, quarterly_updates, thesis
from app.config import settings


# ---- Structured Logging ----

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging():
    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root.handlers = [handler]


setup_logging()
logger = logging.getLogger(__name__)


# ---- Rate Limiting ----

limiter = Limiter(key_func=get_remote_address)


# ---- App ----

app = FastAPI(title="Thesis Engine", version="0.1.0", docs_url="/docs", redoc_url="/redoc", timeout=300)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Request logging middleware ----

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration_ms, 1),
            },
        )
        return response
    except Exception as e:
        duration_ms = (time.time() - start) * 1000
        logger.exception(
            "request_error",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": round(duration_ms, 1),
            },
        )
        raise


# ---- Routes ----

app.include_router(health.router)
app.include_router(companies.router, prefix="/api/v1")
app.include_router(financials.router, prefix="/api/v1")
app.include_router(thesis.router, prefix="/api/v1")
app.include_router(quarterly_updates.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(business_profiles.router, prefix="/api/v1")
