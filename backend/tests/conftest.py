"""Shared test fixtures for the thesis engine backend."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create the async engine and all tables once per session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Provide a transactional database session that rolls back after each test."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        await session.begin()
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture
async def test_client(db_session):
    """Provide an httpx AsyncClient wired to the FastAPI app with overridden DB."""
    from httpx import ASGITransport, AsyncClient

    from app.database import get_session
    from app.main import app

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ---- Mock fixtures for external services ----


@pytest.fixture
def mock_fmp():
    """Mock FinancialDataService to avoid real FMP API calls."""
    with patch("app.services.financial_data_service.FinancialDataService") as MockFMP:
        instance = MockFMP.return_value
        instance.get_income_statement = AsyncMock(return_value=[{
            "date": "2025-03-31",
            "period": "Q1",
            "calendar_year": "2025",
            "revenue": 100_000_000,
            "cost_of_revenue": 40_000_000,
            "gross_profit": 60_000_000,
            "operating_income": 30_000_000,
            "net_income": 25_000_000,
            "ebitda": 35_000_000,
            "eps_diluted": 2.50,
            "shares_outstanding": 10_000_000,
        }])
        instance.get_balance_sheet = AsyncMock(return_value=[{
            "date": "2025-03-31",
            "period": "Q1",
            "calendar_year": "2025",
            "total_assets": 500_000_000,
            "total_liabilities": 200_000_000,
            "total_equity": 300_000_000,
            "cash_and_equivalents": 50_000_000,
            "total_debt": 100_000_000,
        }])
        instance.get_cash_flow = AsyncMock(return_value=[{
            "date": "2025-03-31",
            "period": "Q1",
            "calendar_year": "2025",
            "operating_cash_flow": 40_000_000,
            "capital_expenditures": -10_000_000,
            "free_cash_flow": 30_000_000,
        }])
        instance.get_segments = AsyncMock(return_value=[
            {"name": "Products", "revenue": 70_000_000},
            {"name": "Services", "revenue": 30_000_000},
        ])
        instance.resolve_fmp_ticker = MagicMock(side_effect=lambda t, e=None: t)
        yield instance


@pytest.fixture
def mock_edgar():
    """Mock EdgarService to avoid real SEC API calls."""
    with patch("app.services.edgar_service.EdgarService") as MockEdgar:
        instance = MockEdgar.return_value
        instance.get_recent_filings = AsyncMock(return_value=[{
            "accession_number": "0000320193-25-000001",
            "filing_date": "2025-01-31",
            "form_type": "10-Q",
            "primary_document_url": "https://www.sec.gov/test.htm",
        }])
        instance.download_filing = AsyncMock(return_value=b"<html>Filing content</html>")
        instance.parse_filing_html = MagicMock(return_value="Parsed filing text content for LLM processing.")
        yield instance


@pytest.fixture
def mock_groq():
    """Mock LLMService to avoid real Groq API calls."""
    with patch("app.services.llm_service.LLMService") as MockLLM:
        instance = MockLLM.return_value
        instance.generate_business_profile = AsyncMock(return_value={
            "description": "Test company description",
            "business_model": "SaaS model",
            "competitive_position": "Market leader",
            "key_products": '["Product A", "Product B"]',
            "geographic_mix": '{"US": 60, "International": 40}',
            "moat_assessment": "wide",
            "moat_sources": '["Network effects", "Switching costs"]',
        })
        instance.generate_thesis = AsyncMock(return_value={
            "bull_case": "Strong growth ahead",
            "bull_target": 200.0,
            "base_case": "Steady performance",
            "base_target": 150.0,
            "bear_case": "Challenging headwinds",
            "bear_target": 100.0,
            "key_drivers": '["Revenue growth", "Margin expansion"]',
            "key_risks": '["Competition", "Regulation"]',
            "catalysts": '["New product launch"]',
            "thesis_integrity_score": 75,
            "integrity_rationale": "Well-supported thesis",
        })
        instance.generate_quarterly_summary = AsyncMock(return_value={
            "executive_summary": "Strong quarter with beat on revenue.",
            "key_changes": '["Revenue up 15% YoY", "Margin expansion"]',
            "guidance_update": "Raised full-year guidance.",
            "management_commentary": "Management remains optimistic.",
        })
        yield instance


@pytest.fixture
def mock_s3():
    """Mock StorageService to avoid real S3 calls."""
    with patch("app.services.storage_service.StorageService") as MockS3:
        instance = MockS3.return_value
        instance.upload_file = AsyncMock(return_value="companies/test/10-Q_2025-01-31.html")
        instance.download_file = AsyncMock(return_value=b"file content")
        instance.get_presigned_url = MagicMock(return_value="https://s3.example.com/presigned")
        yield instance
