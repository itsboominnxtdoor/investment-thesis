import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from app.dependencies import DBSession
from app.models.quarterly_update import QuarterlyUpdate
from app.schemas.quarterly_update import QuarterlyUpdateList, QuarterlyUpdateRead
from app.services.company_service import CompanyService
from app.services.edgar_service import EdgarService
from app.services.llm_service import LLMService
from app.services.sedar_service import SedarService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies/{company_id}/quarterly-updates", tags=["quarterly-updates"]
)


@router.get("", response_model=QuarterlyUpdateList)
async def list_quarterly_updates(
    db: DBSession,
    company_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
):
    count_q = select(func.count()).where(QuarterlyUpdate.company_id == company_id)
    total = (await db.execute(count_q)).scalar_one()

    q = (
        select(QuarterlyUpdate)
        .where(QuarterlyUpdate.company_id == company_id)
        .order_by(QuarterlyUpdate.fiscal_year.desc(), QuarterlyUpdate.fiscal_quarter.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    result = await db.execute(q)
    items = list(result.scalars().all())
    return QuarterlyUpdateList(items=items, total=total, page=page, per_page=per_page)


@router.get("/{update_id}", response_model=QuarterlyUpdateRead)
async def get_quarterly_update(db: DBSession, company_id: UUID, update_id: UUID):
    q = select(QuarterlyUpdate).where(
        QuarterlyUpdate.id == update_id, QuarterlyUpdate.company_id == company_id
    )
    result = await db.execute(q)
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Quarterly update not found")
    return update


@router.post("/generate", response_model=QuarterlyUpdateRead)
async def generate_quarterly_update(db: DBSession, company_id: UUID):
    """Generate a quarterly update using LLM based on latest filing and financials."""
    from sqlalchemy import func

    from app.models.business_profile import BusinessProfile
    from app.models.financial_snapshot import FinancialSnapshot
    from app.models.thesis_version import ThesisVersion

    company_svc = CompanyService(db)
    company = await company_svc.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get latest financial snapshot
    fin_result = await db.execute(
        select(FinancialSnapshot)
        .where(FinancialSnapshot.company_id == company_id)
        .order_by(
            FinancialSnapshot.fiscal_year.desc(),
            FinancialSnapshot.fiscal_quarter.desc(),
        )
        .limit(1)
    )
    snapshot = fin_result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(
            status_code=400,
            detail="No financial snapshot available. Ingest financials first.",
        )

    # Get latest thesis version
    thesis_result = await db.execute(
        select(ThesisVersion)
        .where(ThesisVersion.company_id == company_id)
        .order_by(ThesisVersion.version.desc())
        .limit(1)
    )
    thesis = thesis_result.scalar_one_or_none()
    if not thesis:
        raise HTTPException(
            status_code=400,
            detail="No thesis version available. Generate thesis first.",
        )

    # Check if quarterly update already exists for this period
    existing = await db.execute(
        select(QuarterlyUpdate).where(
            QuarterlyUpdate.company_id == company_id,
            QuarterlyUpdate.fiscal_year == snapshot.fiscal_year,
            QuarterlyUpdate.fiscal_quarter == snapshot.fiscal_quarter,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Quarterly update already exists for Q{snapshot.fiscal_quarter} {snapshot.fiscal_year}",
        )

    # Try to get filing text from EDGAR or SEDAR+
    filing_text = ""
    filing_type = "10-Q"
    source = "edgar"

    if company.cik:
        edgar = EdgarService()
        try:
            filings = await edgar.get_recent_filings(company.cik, "10-Q")
            if not filings:
                filings = await edgar.get_recent_filings(company.cik, "10-K")
                filing_type = "10-K"
            if filings:
                content = await edgar.download_filing(filings[0]["primary_document_url"])
                filing_text = edgar.parse_filing_html(content)
        except Exception as e:
            logger.warning("Failed to retrieve EDGAR filing for %s: %s", company.ticker, e)

    if not filing_text and company.exchange == "TSX":
        sedar = SedarService()
        try:
            filings = await sedar.get_recent_filings(company.name, "10-Q")
            filing_type = "MD&A"
            source = "sedar"
        except Exception as e:
            logger.warning("Failed to retrieve SEDAR+ filing for %s: %s", company.ticker, e)

    if not filing_text:
        # Fallback: use basic company info as context
        filing_text = (
            f"{company.name} ({company.ticker}) is a {company.industry} company "
            f"in the {company.sector} sector, listed on {company.exchange}."
        )

    # Get prior quarter snapshot for comparison
    prior_snapshot = None
    prior_result = await db.execute(
        select(FinancialSnapshot)
        .where(
            FinancialSnapshot.company_id == company_id,
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
    prior = prior_result.scalar_one_or_none()
    if prior:
        prior_snapshot = {
            "revenue": str(prior.revenue) if prior.revenue else "N/A",
            "net_income": str(prior.net_income) if prior.net_income else "N/A",
            "eps_diluted": str(prior.eps_diluted) if prior.eps_diluted else "N/A",
        }

    # Generate quarterly summary via LLM
    llm = LLMService()
    try:
        result = await llm.generate_quarterly_summary(filing_text, prior_snapshot)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

    # Create quarterly update record
    update = QuarterlyUpdate(
        company_id=company_id,
        snapshot_id=snapshot.id,
        thesis_version_id=thesis.id,
        fiscal_year=snapshot.fiscal_year,
        fiscal_quarter=snapshot.fiscal_quarter,
        filing_type=filing_type,
        executive_summary=result.get("executive_summary", ""),
        key_changes=result.get("key_changes", "[]"),
        guidance_update=result.get("guidance_update"),
        management_commentary=result.get("management_commentary"),
    )
    db.add(update)
    await db.commit()
    return update
