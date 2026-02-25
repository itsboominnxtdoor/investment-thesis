import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from app.dependencies import DBSession
from app.models.company import Company
from app.models.financial_snapshot import FinancialSnapshot
from app.models.thesis_version import ThesisVersion
from app.schemas.company import CompanyList, CompanyRead
from app.schemas.financial_snapshot import StockQuoteRead
from app.services.company_service import CompanyService
from app.services.financial_data_service import FinancialDataService
from app.services.financial_ingestion_service import FinancialIngestionService
from app.services.financial_service import FinancialService
from app.services.llm_service import LLMService
from app.services.market_sentiment_service import MarketSentimentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companies", tags=["companies"])


class DashboardStats(BaseModel):
    total_companies: int
    companies_with_financials: int
    companies_with_thesis: int
    sectors: dict[str, int]
    exchanges: dict[str, int]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: DBSession):
    """Get portfolio-level dashboard statistics."""
    total = (await db.execute(select(func.count(Company.id)).where(Company.is_active.is_(True)))).scalar_one()

    with_financials = (await db.execute(
        select(func.count(func.distinct(FinancialSnapshot.company_id)))
    )).scalar_one()

    with_thesis = (await db.execute(
        select(func.count(func.distinct(ThesisVersion.company_id)))
    )).scalar_one()

    sector_rows = (await db.execute(
        select(Company.sector, func.count(Company.id))
        .where(Company.is_active.is_(True))
        .group_by(Company.sector)
        .order_by(func.count(Company.id).desc())
    )).all()
    sectors = {row[0]: row[1] for row in sector_rows}

    exchange_rows = (await db.execute(
        select(Company.exchange, func.count(Company.id))
        .where(Company.is_active.is_(True))
        .group_by(Company.exchange)
        .order_by(func.count(Company.id).desc())
    )).all()
    exchanges = {row[0]: row[1] for row in exchange_rows}

    return DashboardStats(
        total_companies=total,
        companies_with_financials=with_financials,
        companies_with_thesis=with_thesis,
        sectors=sectors,
        exchanges=exchanges,
    )


@router.get("", response_model=CompanyList)
async def list_companies(
    db: DBSession,
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    search: str | None = None,
    sector: str | None = None,
    exchange: str | None = None,
):
    service = CompanyService(db)
    items, total = await service.list_companies(
        page=page, per_page=per_page, search=search, sector=sector, exchange=exchange
    )
    return CompanyList(items=items, total=total, page=page, per_page=per_page)


@router.get("/{company_id}", response_model=CompanyRead)
async def get_company(db: DBSession, company_id: UUID):
    """Get company details. Auto-ingests financials if missing."""
    service = CompanyService(db)
    company = await service.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Auto-ingest if no financials exist
    from sqlalchemy import select
    from app.models.financial_snapshot import FinancialSnapshot
    
    existing = await db.execute(
        select(FinancialSnapshot).where(
            FinancialSnapshot.company_id == company_id
        ).limit(1)
    )
    if not existing.scalar_one_or_none():
        # Trigger background ingestion (don't wait for response)
        logger.info("Auto-ingesting financials for %s", company.ticker)
        try:
            ingestion = FinancialIngestionService(db)
            snapshot = await ingestion.ingest_latest_financials(company_id)
            logger.info("Auto-ingest completed for %s", company.ticker)
        except Exception as e:
            logger.warning("Auto-ingest failed for %s: %s", company.ticker, e)
    
    return company


@router.get("/{company_id}/price", response_model=StockQuoteRead)
async def get_stock_price(db: DBSession, company_id: UUID):
    """Fetch live stock price for a company."""
    service = CompanyService(db)
    company = await service.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    fds = FinancialDataService()
    ticker = fds.resolve_fmp_ticker(company.ticker, company.exchange)
    quote = await fds.get_quote(ticker)
    if not quote:
        raise HTTPException(status_code=404, detail="Price unavailable")
    return StockQuoteRead(symbol=ticker, **quote)


@router.get("/ticker/{ticker}", response_model=CompanyRead)
async def get_company_by_ticker(db: DBSession, ticker: str):
    service = CompanyService(db)
    company = await service.get_by_ticker(ticker.upper())
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


class IngestResult(BaseModel):
    status: str
    detail: str


@router.post("/{company_id}/ingest", response_model=IngestResult)
async def ingest_company(db: DBSession, company_id: UUID):
    """Run the full ingestion pipeline for a single company synchronously.

    Steps: ingest financials -> generate business profile -> generate thesis.
    Use this as a fallback when Celery isn't running.
    """
    service = CompanyService(db)
    company = await service.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    steps_completed = []

    # Step 1: Ingest financials
    try:
        ingestion = FinancialIngestionService(db)
        snapshot = await ingestion.ingest_latest_financials(company_id)
        steps_completed.append("financials")
    except ValueError as e:
        snapshot = None
        steps_completed.append(f"financials:skipped ({e})")
    except Exception as e:
        logger.exception("Financial ingestion failed for %s", company.ticker)
        raise HTTPException(status_code=500, detail=f"Financial ingestion failed: {e}")

    # Step 2: Generate thesis (requires snapshot)
    if snapshot:
        try:
            llm = LLMService()
            fin_service = FinancialService(db)
            company_data = {
                "name": company.name,
                "ticker": company.ticker,
                "sector": company.sector,
                "industry": company.industry,
            }
            snapshot_data = {
                "revenue": str(snapshot.revenue) if snapshot.revenue else "N/A",
                "net_income": str(snapshot.net_income) if snapshot.net_income else "N/A",
                "ebitda": str(snapshot.ebitda) if snapshot.ebitda else "N/A",
                "eps_diluted": str(snapshot.eps_diluted) if snapshot.eps_diluted else "N/A",
                "gross_margin": str(snapshot.gross_margin) if snapshot.gross_margin else "N/A",
                "operating_margin": str(snapshot.operating_margin) if snapshot.operating_margin else "N/A",
                "free_cash_flow": str(snapshot.free_cash_flow) if snapshot.free_cash_flow else "N/A",
                "total_debt": str(snapshot.total_debt) if snapshot.total_debt else "N/A",
                "cash_and_equivalents": str(snapshot.cash_and_equivalents) if snapshot.cash_and_equivalents else "N/A",
                "debt_to_equity": str(snapshot.debt_to_equity) if snapshot.debt_to_equity else "N/A",
            }
            resolved_ticker = FinancialDataService().resolve_fmp_ticker(company.ticker, company.exchange)
            market_context = await MarketSentimentService().get_market_context(resolved_ticker)
            thesis_result = await llm.generate_thesis(company_data, snapshot_data, {}, market_context=market_context)
            steps_completed.append("thesis")
        except Exception as e:
            logger.exception("Thesis generation failed for %s", company.ticker)
            steps_completed.append(f"thesis:failed ({e})")

    return IngestResult(
        status="completed",
        detail=f"Pipeline steps: {', '.join(steps_completed)}",
    )


class BulkResult(BaseModel):
    dispatched: int
    errors: list[str]


@router.post("/bulk-ingest", response_model=BulkResult)
async def bulk_ingest(db: DBSession):
    """Ingest financials for all active companies (no Celery needed).
    
    This is a synchronous operation - may take 30-60 seconds for 40 companies.
    Each company: fetch FMP data → create snapshot → generate thesis.
    """
    result = await db.execute(
        select(Company).where(Company.is_active.is_(True))
    )
    companies = result.scalars().all()

    dispatched = 0
    errors: list[str] = []
    
    ingestion = FinancialIngestionService(db)
    llm = LLMService()
    fin_service = FinancialService(db)

    for company in companies:
        try:
            # Skip if already has financials
            existing = await db.execute(
                select(FinancialSnapshot).where(
                    FinancialSnapshot.company_id == company.id
                ).limit(1)
            )
            if existing.scalar_one_or_none():
                dispatched += 1
                continue
            
            # Ingest financials
            snapshot = await ingestion.ingest_latest_financials(company.id)
            
            # Generate thesis
            company_data = {
                "name": company.name,
                "ticker": company.ticker,
                "sector": company.sector,
                "industry": company.industry,
            }
            snapshot_data = {
                "revenue": str(snapshot.revenue) if snapshot.revenue else "N/A",
                "net_income": str(snapshot.net_income) if snapshot.net_income else "N/A",
                "ebitda": str(snapshot.ebitda) if snapshot.ebitda else "N/A",
                "eps_diluted": str(snapshot.eps_diluted) if snapshot.eps_diluted else "N/A",
                "gross_margin": str(snapshot.gross_margin) if snapshot.gross_margin else "N/A",
                "operating_margin": str(snapshot.operating_margin) if snapshot.operating_margin else "N/A",
                "free_cash_flow": str(snapshot.free_cash_flow) if snapshot.free_cash_flow else "N/A",
                "total_debt": str(snapshot.total_debt) if snapshot.total_debt else "N/A",
                "cash_and_equivalents": str(snapshot.cash_and_equivalents) if snapshot.cash_and_equivalents else "N/A",
                "debt_to_equity": str(snapshot.debt_to_equity) if snapshot.debt_to_equity else "N/A",
            }
            result_data = await llm.generate_thesis(company_data, snapshot_data, {})
            
            # Save thesis
            from app.models.thesis_version import ThesisVersion as TV
            from decimal import Decimal
            
            thesis = TV(
                company_id=company.id,
                snapshot_id=snapshot.id,
                version=1,
                bull_case=result_data.get("bull_case", ""),
                bull_target=Decimal(str(result_data["bull_target"])) if result_data.get("bull_target") else None,
                base_case=result_data.get("base_case", ""),
                base_target=Decimal(str(result_data["base_target"])) if result_data.get("base_target") else None,
                bear_case=result_data.get("bear_case", ""),
                bear_target=Decimal(str(result_data["bear_target"])) if result_data.get("bear_target") else None,
                key_drivers=result_data.get("key_drivers", "[]"),
                key_risks=result_data.get("key_risks", "[]"),
                catalysts=result_data.get("catalysts", "[]"),
                thesis_integrity_score=Decimal(str(result_data["thesis_integrity_score"])) if result_data.get("thesis_integrity_score") else None,
                integrity_rationale=result_data.get("integrity_rationale"),
                llm_model_used="llama-3.3-70b-versatile",
            )
            db.add(thesis)
            await db.commit()
            dispatched += 1
        except Exception as e:
            logger.exception("Failed to ingest %s", company.ticker)
            errors.append(f"{company.ticker}: {e}")
            await db.rollback()

    return BulkResult(dispatched=dispatched, errors=errors)


@router.post("/bulk-generate", response_model=BulkResult)
async def bulk_generate_theses(db: DBSession):
    """Generate theses for all companies that have financials but no thesis."""
    # Find companies with snapshots but no thesis
    companies_with_financials = (
        select(FinancialSnapshot.company_id).distinct()
    )
    companies_with_thesis = (
        select(ThesisVersion.company_id).distinct()
    )

    result = await db.execute(
        select(Company).where(
            Company.id.in_(companies_with_financials),
            Company.id.notin_(companies_with_thesis),
            Company.is_active.is_(True),
        )
    )
    companies = result.scalars().all()

    dispatched = 0
    errors: list[str] = []
    llm = LLMService()

    for company in companies:
        try:
            # Get latest snapshot
            snap_result = await db.execute(
                select(FinancialSnapshot)
                .where(FinancialSnapshot.company_id == company.id)
                .order_by(FinancialSnapshot.fiscal_year.desc(), FinancialSnapshot.fiscal_quarter.desc())
                .limit(1)
            )
            snapshot = snap_result.scalar_one_or_none()
            if not snapshot:
                continue

            company_data = {
                "name": company.name,
                "ticker": company.ticker,
                "sector": company.sector,
                "industry": company.industry,
            }
            snapshot_data = {
                "revenue": str(snapshot.revenue) if snapshot.revenue else "N/A",
                "net_income": str(snapshot.net_income) if snapshot.net_income else "N/A",
                "ebitda": str(snapshot.ebitda) if snapshot.ebitda else "N/A",
                "eps_diluted": str(snapshot.eps_diluted) if snapshot.eps_diluted else "N/A",
                "gross_margin": str(snapshot.gross_margin) if snapshot.gross_margin else "N/A",
                "operating_margin": str(snapshot.operating_margin) if snapshot.operating_margin else "N/A",
                "free_cash_flow": str(snapshot.free_cash_flow) if snapshot.free_cash_flow else "N/A",
                "total_debt": str(snapshot.total_debt) if snapshot.total_debt else "N/A",
                "cash_and_equivalents": str(snapshot.cash_and_equivalents) if snapshot.cash_and_equivalents else "N/A",
                "debt_to_equity": str(snapshot.debt_to_equity) if snapshot.debt_to_equity else "N/A",
            }

            result_data = await llm.generate_thesis(company_data, snapshot_data, {})
            from app.models.thesis_version import ThesisVersion as TV
            from decimal import Decimal

            thesis = TV(
                company_id=company.id,
                snapshot_id=snapshot.id,
                version=1,
                bull_case=result_data.get("bull_case", ""),
                bull_target=Decimal(str(result_data["bull_target"])) if result_data.get("bull_target") else None,
                base_case=result_data.get("base_case", ""),
                base_target=Decimal(str(result_data["base_target"])) if result_data.get("base_target") else None,
                bear_case=result_data.get("bear_case", ""),
                bear_target=Decimal(str(result_data["bear_target"])) if result_data.get("bear_target") else None,
                key_drivers=result_data.get("key_drivers", "[]"),
                key_risks=result_data.get("key_risks", "[]"),
                catalysts=result_data.get("catalysts", "[]"),
                thesis_integrity_score=Decimal(str(result_data["thesis_integrity_score"])) if result_data.get("thesis_integrity_score") else None,
                integrity_rationale=result_data.get("integrity_rationale"),
                llm_model_used="llama-3.3-70b-versatile",
            )
            db.add(thesis)
            await db.commit()
            dispatched += 1
        except Exception as e:
            logger.error("Failed to generate thesis for %s: %s", company.ticker, e)
            errors.append(f"{company.ticker}: {e}")

    return BulkResult(dispatched=dispatched, errors=errors)
