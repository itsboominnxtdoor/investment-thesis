from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.dependencies import DBSession
from app.schemas.thesis_version import ThesisVersionList, ThesisVersionRead
from app.services.company_service import CompanyService
from app.services.financial_service import FinancialService
from app.services.llm_service import LLMService
from app.services.thesis_service import ThesisService

router = APIRouter(prefix="/companies/{company_id}/thesis", tags=["thesis"])


@router.get("", response_model=ThesisVersionList)
async def list_thesis_versions(
    db: DBSession,
    company_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
):
    service = ThesisService(db)
    items, total = await service.list_versions(company_id, page=page, per_page=per_page)
    return ThesisVersionList(items=items, total=total, page=page, per_page=per_page)


@router.get("/latest", response_model=ThesisVersionRead)
async def get_latest_thesis(db: DBSession, company_id: UUID):
    service = ThesisService(db)
    thesis = await service.get_latest(company_id)
    if not thesis:
        raise HTTPException(status_code=404, detail="No thesis versions found")
    return thesis


@router.get("/{version_id}", response_model=ThesisVersionRead)
async def get_thesis_version(db: DBSession, company_id: UUID, version_id: UUID):
    service = ThesisService(db)
    thesis = await service.get_by_id(version_id)
    if not thesis or thesis.company_id != company_id:
        raise HTTPException(status_code=404, detail="Thesis version not found")
    return thesis


@router.post("/generate", response_model=ThesisVersionRead)
async def generate_thesis(db: DBSession, company_id: UUID):
    """Generate a new thesis version using the LLM."""
    company_svc = CompanyService(db)
    company = await company_svc.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get latest financial snapshot
    fin_svc = FinancialService(db)
    snapshot = await fin_svc.get_latest(company_id)
    if not snapshot:
        raise HTTPException(
            status_code=400,
            detail="No financial data available. Ingest financials first.",
        )

    # Get latest business profile
    from sqlalchemy import select
    from app.models.business_profile import BusinessProfile

    bp_result = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.company_id == company_id)
        .order_by(BusinessProfile.version.desc())
        .limit(1)
    )
    profile = bp_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="No business profile available. Generate a business profile first.",
        )

    # Get prior thesis for drift tracking
    thesis_svc = ThesisService(db)
    prior_thesis = await thesis_svc.get_latest(company_id)

    # Build dicts for LLM
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
            "bull_case": prior_thesis.bull_case,
            "base_case": prior_thesis.base_case,
            "bear_case": prior_thesis.bear_case,
        }

    llm = LLMService()
    try:
        result = await llm.generate_thesis(
            company_data, snapshot_data, profile_data, prior_thesis_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

    result["llm_model_used"] = settings.LLM_MODEL

    thesis = await thesis_svc.create_version(
        company_id=company_id,
        snapshot_id=snapshot.id,
        thesis_data=result,
        prior_version=prior_thesis,
    )
    return thesis
