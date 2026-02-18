"""Integration tests for /api/v1/companies endpoints."""

import pytest
import pytest_asyncio

from app.models.company import Company


@pytest_asyncio.fixture
async def seeded_companies(db_session):
    """Seed a few companies for testing."""
    companies = [
        Company(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ", sector="Technology", industry="Consumer Electronics", currency="USD", cik="0000320193", is_active=True),
        Company(ticker="MSFT", name="Microsoft Corporation", exchange="NASDAQ", sector="Technology", industry="Software", currency="USD", is_active=True),
        Company(ticker="RY", name="Royal Bank of Canada", exchange="TSX", sector="Financials", industry="Banks", currency="CAD", is_active=True),
    ]
    for c in companies:
        db_session.add(c)
    await db_session.flush()
    return companies


@pytest.mark.asyncio
async def test_list_companies(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_companies_search(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies?search=apple")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_list_companies_filter_exchange(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies?exchange=TSX")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_get_company_by_ticker(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies/ticker/AAPL")
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "AAPL"
    assert data["name"] == "Apple Inc."


@pytest.mark.asyncio
async def test_get_company_by_ticker_not_found(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies/ticker/NONEXIST")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_company_by_id(test_client, seeded_companies):
    # Get ID first
    resp = await test_client.get("/api/v1/companies/ticker/AAPL")
    company_id = resp.json()["id"]

    resp = await test_client.get(f"/api/v1/companies/{company_id}")
    assert resp.status_code == 200
    assert resp.json()["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_dashboard_stats(test_client, seeded_companies):
    resp = await test_client.get("/api/v1/companies/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_companies"] == 3
    assert "Technology" in data["sectors"]
    assert "TSX" in data["exchanges"]
