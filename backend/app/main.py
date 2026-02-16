from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import business_profiles, companies, documents, financials, health, quarterly_updates, thesis
from app.config import settings

app = FastAPI(title="Thesis Engine", version="0.1.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(companies.router, prefix="/api/v1")
app.include_router(financials.router, prefix="/api/v1")
app.include_router(thesis.router, prefix="/api/v1")
app.include_router(quarterly_updates.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(business_profiles.router, prefix="/api/v1")
