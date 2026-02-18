"""Tests for CompanyService — CRUD, search, filtering."""

import pytest
import pytest_asyncio
from sqlalchemy import text

from app.models.company import Company
from app.services.company_service import CompanyService


@pytest_asyncio.fixture
async def seeded_db(db_session):
    """Seed test database with a few companies."""
    companies = [
        Company(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", sector="Technology", industry="Consumer Electronics", currency="USD", cik="0000320193", is_active=True),
        Company(ticker="MSFT", name="Microsoft Corporation", exchange="NASDAQ", sector="Technology", industry="Software - Infrastructure", currency="USD", cik="0000789019", is_active=True),
        Company(ticker="RY", name="Royal Bank of Canada", exchange="TSX", sector="Financials", industry="Banks - Diversified", currency="CAD", cik="0001000275", is_active=True),
        Company(ticker="INACTIVE", name="Inactive Corp", exchange="NYSE", sector="Technology", industry="Test", currency="USD", is_active=False),
    ]
    for c in companies:
        db_session.add(c)
    await db_session.flush()
    return db_session


@pytest.mark.asyncio
async def test_get_by_ticker(seeded_db):
    service = CompanyService(seeded_db)
    company = await service.get_by_ticker("AAPL")
    assert company is not None
    assert company.name == "Apple Inc."


@pytest.mark.asyncio
async def test_get_by_ticker_not_found(seeded_db):
    service = CompanyService(seeded_db)
    company = await service.get_by_ticker("NONEXIST")
    assert company is None


@pytest.mark.asyncio
async def test_get_by_id(seeded_db):
    service = CompanyService(seeded_db)
    apple = await service.get_by_ticker("AAPL")
    by_id = await service.get_by_id(apple.id)
    assert by_id is not None
    assert by_id.ticker == "AAPL"


@pytest.mark.asyncio
async def test_list_companies_pagination(seeded_db):
    service = CompanyService(seeded_db)
    items, total = await service.list_companies(page=1, per_page=2)
    assert total == 3  # Excludes inactive
    assert len(items) == 2


@pytest.mark.asyncio
async def test_list_companies_search(seeded_db):
    service = CompanyService(seeded_db)
    items, total = await service.list_companies(search="apple")
    assert total == 1
    assert items[0].ticker == "AAPL"


@pytest.mark.asyncio
async def test_list_companies_filter_sector(seeded_db):
    service = CompanyService(seeded_db)
    items, total = await service.list_companies(sector="Financials")
    assert total == 1
    assert items[0].ticker == "RY"


@pytest.mark.asyncio
async def test_list_companies_filter_exchange(seeded_db):
    service = CompanyService(seeded_db)
    items, total = await service.list_companies(exchange="TSX")
    assert total == 1
    assert items[0].exchange == "TSX"


@pytest.mark.asyncio
async def test_list_excludes_inactive(seeded_db):
    service = CompanyService(seeded_db)
    items, total = await service.list_companies()
    tickers = [c.ticker for c in items]
    assert "INACTIVE" not in tickers
