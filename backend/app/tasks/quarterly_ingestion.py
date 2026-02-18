"""Quarterly ingestion pipeline — 7-step process for each company filing.

Steps:
1. Download filing from EDGAR/SEDAR+
2. Upload raw document to S3
3. Pull structured financial data from API
4. Create financial snapshot
5. Generate/update business profile via LLM
6. Generate new thesis version via LLM
7. Create quarterly update record
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select

from app.database import async_session_factory
from app.models.company import Company
from app.models.document import Document
from app.models.financial_snapshot import FinancialSnapshot, Segment
from app.models.thesis_version import ThesisVersion
from app.models.quarterly_update import QuarterlyUpdate
from app.models.business_profile import BusinessProfile
from app.services.edgar_service import EdgarService
from app.services.sedar_service import SedarService
from app.services.financial_data_service import FinancialDataService
from app.services.llm_service import LLMService
from app.services.storage_service import StorageService
from app.config import settings
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

QUARTER_MAP = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}


def _to_decimal(val) -> Decimal | None:
    """Convert value to Decimal safely."""
    if val is None:
        return None
    return Decimal(str(val))


def _safe_divide(num, denom) -> Decimal | None:
    """Divide two numbers safely, returning None on error."""
    if num is None or denom is None or denom == 0:
        return None
    return Decimal(str(num)) / Decimal(str(denom))


@celery_app.task(name="app.tasks.quarterly_ingestion.check_for_new_filings")
def check_for_new_filings():
    """Hourly beat task: check all active companies for new filings.
    
    For each company with a new filing detected, dispatches
    process_company_filing as a separate task.
    """
    logger.info("Checking for new filings across all active companies")
    
    async def _check():
        async with async_session_factory() as session:
            # Get all active companies
            result = await session.execute(
                select(Company).where(Company.is_active.is_(True))
            )
            companies = result.scalars().all()
            
            for company in companies:
                filings = []
                
                # Check EDGAR for US companies
                if company.cik:
                    edgar = EdgarService()
                    try:
                        filings.extend(await edgar.get_recent_filings(company.cik, "10-Q"))
                        filings.extend(await edgar.get_recent_filings(company.cik, "10-K"))
                    except Exception as e:
                        logger.warning("Failed to check EDGAR for %s: %s", company.ticker, e)
                
                # Check SEDAR+ for Canadian companies (TSX)
                if company.exchange == "TSX":
                    sedar = SedarService()
                    try:
                        sedar_filings = await sedar.get_recent_filings(company.name)
                        filings.extend(sedar_filings)
                    except Exception as e:
                        logger.warning("Failed to check SEDAR+ for %s: %s", company.ticker, e)
                
                # Dispatch processing task for each new filing
                for filing in filings:
                    # Check if we already have this document
                    existing = await session.execute(
                        select(Document).where(
                            Document.company_id == company.id,
                            Document.source_url == filing.get("primary_document_url", filing.get("url", "")),
                        )
                    )
                    if not existing.scalar_one_or_none():
                        logger.info("Dispatching processing task for %s filing", company.ticker)
                        process_company_filing.delay(str(company.id), filing)
    
    asyncio.run(_check())


@celery_app.task(
    name="app.tasks.quarterly_ingestion.process_company_filing",
    bind=True,
    max_retries=3,
    default_retry_delay=300,
)
def process_company_filing(self, company_id: str, filing_info: dict):
    """Process a single company's new filing through the 7-step pipeline.
    
    Args:
        company_id: UUID of the company
        filing_info: Dict with filing metadata (type, url, date, etc.)
    """
    logger.info("Processing filing for company %s: %s", company_id, filing_info.get("form_type", filing_info.get("type")))
    
    try:
        # Run the async pipeline
        asyncio.run(_run_pipeline(UUID(company_id), filing_info))
        logger.info("Successfully processed filing for company %s", company_id)
    except Exception as exc:
        logger.exception("Failed to process filing for company %s", company_id)
        raise self.retry(exc=exc, countdown=300)


async def _run_pipeline(company_id: UUID, filing_info: dict):
    """Run the full 7-step ingestion pipeline."""
    async with async_session_factory() as session:
        # Get company
        result = await session.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise ValueError(f"Company {company_id} not found")
        
        # Step 1 & 2: Download and upload to S3
        doc = await _step_download_and_store(session, company, filing_info)
        
        # Step 3 & 4: Pull financial data and create snapshot
        snapshot = await _step_pull_financials_and_create_snapshot(session, company, filing_info)
        
        # Step 5: Generate/update business profile (only for annual filings)
        profile = await _step_generate_profile(session, company, snapshot, filing_info)
        
        # Step 6: Generate thesis version
        thesis = await _step_generate_thesis(session, company, snapshot, profile)
        
        # Step 7: Create quarterly update
        update = await _step_create_quarterly_update(session, company, snapshot, thesis, filing_info)
        
        await session.commit()
        
        return update


async def _step_download_and_store(session, company: Company, filing_info: dict) -> Document:
    """Step 1 & 2: Download filing and upload to S3, create document record."""
    source_url = filing_info.get("primary_document_url", filing_info.get("url", ""))
    source = "edgar" if company.cik else "sedar"
    doc_type = filing_info.get("form_type", filing_info.get("type", "Unknown"))
    filing_date = filing_info.get("filing_date")
    
    # Download the filing
    content = b""
    if company.cik:
        edgar = EdgarService()
        try:
            content = await edgar.download_filing(source_url)
        except Exception as e:
            logger.warning("Failed to download from EDGAR: %s", e)
    else:
        sedar = SedarService()
        try:
            content = await sedar.download_filing(source_url)
        except Exception as e:
            logger.warning("Failed to download from SEDAR+: %s", e)
    
    # Upload to S3 (optional - continue even if S3 fails)
    s3_key = None
    file_size = len(content) if content else None
    if content and settings.S3_BUCKET_NAME:
        storage = StorageService()
        try:
            s3_key = await storage.upload_file(
                bucket=settings.S3_BUCKET_NAME,
                key=f"companies/{company.id}/{doc_type}_{filing_date or 'unknown'}.html",
                content=content,
            )
        except Exception as e:
            logger.warning("Failed to upload to S3: %s", e)
    
    # Create document record
    doc = Document(
        company_id=company.id,
        doc_type=doc_type,
        source=source,
        source_url=source_url,
        s3_key=s3_key,
        file_size_bytes=file_size,
        filing_date=filing_date,
    )
    session.add(doc)
    return doc


async def _step_pull_financials_and_create_snapshot(
    session, company: Company, filing_info: dict
) -> FinancialSnapshot | None:
    """Step 3 & 4: Pull structured financial data and create snapshot."""
    fmp = FinancialDataService()
    fmp_ticker = fmp.resolve_fmp_ticker(company.ticker, company.exchange)

    try:
        # Fetch financial data from FMP
        income_data = await fmp.get_income_statement(fmp_ticker)
        balance_data = await fmp.get_balance_sheet(fmp_ticker)
        cashflow_data = await fmp.get_cash_flow(fmp_ticker)
        segments_data = await fmp.get_segments(fmp_ticker)
        
        if not income_data:
            logger.warning("No financial data available for %s", company.ticker)
            return None
        
        # Use most recent period
        inc = income_data[0]
        bal = balance_data[0] if balance_data else {}
        cf = cashflow_data[0] if cashflow_data else {}
        
        # Parse fiscal period
        period_str = inc.get("period", "Q1")
        calendar_year = inc.get("calendar_year")
        fiscal_quarter = QUARTER_MAP.get(period_str, 1)
        fiscal_year = int(calendar_year) if calendar_year else datetime.now().year
        
        # Check for existing snapshot
        existing = await session.execute(
            select(FinancialSnapshot).where(
                FinancialSnapshot.company_id == company.id,
                FinancialSnapshot.fiscal_year == fiscal_year,
                FinancialSnapshot.fiscal_quarter == fiscal_quarter,
            )
        )
        if existing.scalar_one_or_none():
            logger.info("Snapshot already exists for %s Q%d %d", company.ticker, fiscal_quarter, fiscal_year)
            return None
        
        # Compute derived metrics
        revenue = inc.get("revenue")
        gross_profit = inc.get("gross_profit")
        operating_income = inc.get("operating_income")
        net_income = inc.get("net_income")
        total_equity = bal.get("total_equity")
        total_debt = bal.get("total_debt")
        
        snapshot = FinancialSnapshot(
            company_id=company.id,
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            currency=company.currency,
            revenue=_to_decimal(revenue),
            cost_of_revenue=_to_decimal(inc.get("cost_of_revenue")),
            gross_profit=_to_decimal(gross_profit),
            operating_income=_to_decimal(operating_income),
            net_income=_to_decimal(net_income),
            ebitda=_to_decimal(inc.get("ebitda")),
            eps_diluted=_to_decimal(inc.get("eps_diluted")),
            shares_outstanding=_to_decimal(inc.get("shares_outstanding")),
            total_assets=_to_decimal(bal.get("total_assets")),
            total_liabilities=_to_decimal(bal.get("total_liabilities")),
            total_equity=_to_decimal(total_equity),
            cash_and_equivalents=_to_decimal(bal.get("cash_and_equivalents")),
            total_debt=_to_decimal(total_debt),
            operating_cash_flow=_to_decimal(cf.get("operating_cash_flow")),
            capital_expenditures=_to_decimal(cf.get("capital_expenditures")),
            free_cash_flow=_to_decimal(cf.get("free_cash_flow")),
            gross_margin=_safe_divide(gross_profit, revenue),
            operating_margin=_safe_divide(operating_income, revenue),
            net_margin=_safe_divide(net_income, revenue),
            roe=_safe_divide(net_income, total_equity),
            debt_to_equity=_safe_divide(total_debt, total_equity),
        )
        session.add(snapshot)
        await session.flush()
        
        # Add segment records
        if segments_data:
            total_seg_revenue = sum(s.get("revenue", 0) or 0 for s in segments_data)
            for seg in segments_data:
                seg_rev = seg.get("revenue")
                rev_pct = _safe_divide(seg_rev, total_seg_revenue) if total_seg_revenue else None
                segment = Segment(
                    snapshot_id=snapshot.id,
                    name=seg["name"],
                    revenue=_to_decimal(seg_rev),
                    revenue_pct=rev_pct,
                )
                session.add(segment)
        
        logger.info("Created financial snapshot for %s Q%d %d", company.ticker, fiscal_quarter, fiscal_year)
        return snapshot
        
    except Exception as e:
        logger.error("Failed to create financial snapshot for %s: %s", company.ticker, e)
        return None


async def _step_generate_profile(
    session, company: Company, snapshot: FinancialSnapshot | None, filing_info: dict
) -> BusinessProfile | None:
    """Step 5: Generate business profile from annual filing (10-K or AIF)."""
    doc_type = filing_info.get("form_type", filing_info.get("type", ""))
    
    # Only generate profile for annual filings
    if doc_type not in ["10-K", "AIF"]:
        return None
    
    # Get filing text for LLM
    filing_text = ""
    source_url = filing_info.get("primary_document_url", filing_info.get("url", ""))
    
    if company.cik:
        edgar = EdgarService()
        try:
            content = await edgar.download_filing(source_url)
            filing_text = edgar.parse_filing_html(content)
        except Exception as e:
            logger.warning("Failed to get filing text: %s", e)
    
    if not filing_text:
        filing_text = f"{company.name} ({company.ticker}) is a {company.industry} company in the {company.sector} sector."
    
    # Generate profile via LLM
    llm = LLMService()
    company_data = {
        "name": company.name,
        "ticker": company.ticker,
        "exchange": company.exchange,
        "sector": company.sector,
        "industry": company.industry,
    }
    
    try:
        result = await llm.generate_business_profile(company_data, filing_text)
    except Exception as e:
        logger.error("Failed to generate business profile: %s", e)
        return None
    
    # Determine next version
    existing = await session.execute(
        select(BusinessProfile)
        .where(BusinessProfile.company_id == company.id)
        .order_by(BusinessProfile.version.desc())
        .limit(1)
    )
    prev_profile = existing.scalar_one_or_none()
    next_version = (prev_profile.version + 1) if prev_profile else 1
    
    profile = BusinessProfile(
        company_id=company.id,
        version=next_version,
        description=result.get("description", ""),
        business_model=result.get("business_model", ""),
        competitive_position=result.get("competitive_position", ""),
        key_products=result.get("key_products", "[]"),
        geographic_mix=result.get("geographic_mix", "{}"),
        moat_assessment=result.get("moat_assessment", "none"),
        moat_sources=result.get("moat_sources", "[]"),
    )
    session.add(profile)
    logger.info("Generated business profile v%d for %s", next_version, company.ticker)
    return profile


async def _step_generate_thesis(
    session, company: Company, snapshot: FinancialSnapshot | None, profile: BusinessProfile | None
) -> ThesisVersion | None:
    """Step 6: Generate new thesis version."""
    if not snapshot:
        logger.warning("No snapshot available for thesis generation")
        return None
    
    # Get prior thesis for drift tracking
    existing = await session.execute(
        select(ThesisVersion)
        .where(ThesisVersion.company_id == company.id)
        .order_by(ThesisVersion.version.desc())
        .limit(1)
    )
    prior_thesis = existing.scalar_one_or_none()
    
    # Prepare data for LLM
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
    profile_data = {}
    if profile:
        profile_data = {
            "description": profile.description,
            "business_model": profile.business_model,
            "competitive_position": profile.competitive_position,
            "moat_assessment": profile.moat_assessment,
        }
    prior_thesis_data = None
    if prior_thesis:
        prior_thesis_data = {
            "version": prior_thesis.version,
            "bull_case": prior_thesis.bull_case[:500],
            "base_case": prior_thesis.base_case[:500],
            "bear_case": prior_thesis.bear_case[:500],
        }
    
    # Generate thesis via LLM
    llm = LLMService()
    try:
        result = await llm.generate_thesis(company_data, snapshot_data, profile_data, prior_thesis_data)
    except Exception as e:
        logger.error("Failed to generate thesis: %s", e)
        return None
    
    # Determine next version
    next_version = (prior_thesis.version + 1) if prior_thesis else 1
    
    thesis = ThesisVersion(
        company_id=company.id,
        snapshot_id=snapshot.id,
        version=next_version,
        bull_case=result.get("bull_case", ""),
        bull_target=_to_decimal(result.get("bull_target")),
        base_case=result.get("base_case", ""),
        base_target=_to_decimal(result.get("base_target")),
        bear_case=result.get("bear_case", ""),
        bear_target=_to_decimal(result.get("bear_target")),
        key_drivers=result.get("key_drivers", "[]"),
        key_risks=result.get("key_risks", "[]"),
        catalysts=result.get("catalysts", "[]"),
        thesis_integrity_score=_to_decimal(result.get("thesis_integrity_score")),
        integrity_rationale=result.get("integrity_rationale"),
        prior_version_id=prior_thesis.id if prior_thesis else None,
        drift_summary=result.get("drift_summary"),
        conviction_direction=result.get("conviction_direction"),
        llm_model_used=settings.LLM_MODEL,
    )
    session.add(thesis)
    logger.info("Generated thesis v%d for %s", next_version, company.ticker)
    return thesis


async def _step_create_quarterly_update(
    session, company: Company, snapshot: FinancialSnapshot | None, 
    thesis: ThesisVersion | None, filing_info: dict
) -> QuarterlyUpdate | None:
    """Step 7: Create quarterly update record."""
    if not snapshot or not thesis:
        logger.warning("Missing snapshot or thesis for quarterly update")
        return None
    
    # Check if update already exists
    existing = await session.execute(
        select(QuarterlyUpdate).where(
            QuarterlyUpdate.company_id == company.id,
            QuarterlyUpdate.fiscal_year == snapshot.fiscal_year,
            QuarterlyUpdate.fiscal_quarter == snapshot.fiscal_quarter,
        )
    )
    if existing.scalar_one_or_none():
        logger.info("Quarterly update already exists")
        return None
    
    # Get filing text for LLM
    filing_text = ""
    source_url = filing_info.get("primary_document_url", filing_info.get("url", ""))
    
    if company.cik:
        edgar = EdgarService()
        try:
            content = await edgar.download_filing(source_url)
            filing_text = edgar.parse_filing_html(content)
        except Exception as e:
            logger.warning("Failed to get filing text: %s", e)
    
    if not filing_text:
        filing_text = f"{company.name} ({company.ticker}) quarterly filing."
    
    # Get prior snapshot for comparison
    prior = await session.execute(
        select(FinancialSnapshot)
        .where(
            FinancialSnapshot.company_id == company.id,
            (FinancialSnapshot.fiscal_year < snapshot.fiscal_year)
            | (
                (FinancialSnapshot.fiscal_year == snapshot.fiscal_year)
                & (FinancialSnapshot.fiscal_quarter < snapshot.fiscal_quarter)
            ),
        )
        .order_by(
            FinancialSnapshot.fiscal_year.desc(),
            FinancialSnapshot.fiscal_quarter.desc(),
        )
        .limit(1)
    )
    prior_snapshot = prior.scalar_one_or_none()
    prior_snapshot_data = None
    if prior_snapshot:
        prior_snapshot_data = {
            "revenue": str(prior_snapshot.revenue) if prior_snapshot.revenue else "N/A",
            "net_income": str(prior_snapshot.net_income) if prior_snapshot.net_income else "N/A",
            "eps_diluted": str(prior_snapshot.eps_diluted) if prior_snapshot.eps_diluted else "N/A",
        }
    
    # Generate summary via LLM
    llm = LLMService()
    try:
        result = await llm.generate_quarterly_summary(filing_text, prior_snapshot_data)
    except Exception as e:
        logger.error("Failed to generate quarterly summary: %s", e)
        return None
    
    doc_type = filing_info.get("form_type", filing_info.get("type", "10-Q"))
    
    update = QuarterlyUpdate(
        company_id=company.id,
        snapshot_id=snapshot.id,
        thesis_version_id=thesis.id,
        fiscal_year=snapshot.fiscal_year,
        fiscal_quarter=snapshot.fiscal_quarter,
        filing_type=doc_type,
        executive_summary=result.get("executive_summary", ""),
        key_changes=result.get("key_changes", "[]"),
        guidance_update=result.get("guidance_update"),
        management_commentary=result.get("management_commentary"),
    )
    session.add(update)
    logger.info("Created quarterly update for %s Q%d %d", company.ticker, snapshot.fiscal_quarter, snapshot.fiscal_year)
    return update
