from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import DBSession
from app.models.business_profile import BusinessProfile
from app.schemas.business_profile import BusinessProfileRead
from app.services.company_service import CompanyService
from app.services.edgar_service import EdgarService
from app.services.llm_service import LLMService

router = APIRouter(prefix="/companies/{company_id}/business-profile", tags=["business-profiles"])


@router.get("", response_model=BusinessProfileRead)
async def get_business_profile(db: DBSession, company_id: UUID):
    """Get the latest business profile. Auto-generates if missing."""
    result = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.company_id == company_id)
        .order_by(BusinessProfile.version.desc())
        .limit(1)
    )
    profile = result.scalar_one_or_none()
    
    # Auto-generate if no profile exists
    if not profile:
        from app.services.company_service import CompanyService
        from app.services.edgar_service import EdgarService
        from app.services.llm_service import LLMService
        
        company_svc = CompanyService(db)
        company = await company_svc.get_by_id(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Try to get filing text from EDGAR
        filing_text = ""
        if company.cik:
            edgar = EdgarService()
            try:
                filings = await edgar.get_recent_filings(company.cik, "10-K")
                if not filings:
                    filings = await edgar.get_recent_filings(company.cik, "10-Q")
                if filings:
                    content = await edgar.download_filing(filings[0]["primary_document_url"])
                    filing_text = edgar.parse_filing_html(content)
            except Exception:
                filing_text = ""

        if not filing_text:
            filing_text = (
                f"{company.name} ({company.ticker}) is a {company.industry} company "
                f"in the {company.sector} sector, listed on {company.exchange}."
            )

        company_data = {
            "name": company.name,
            "ticker": company.ticker,
            "exchange": company.exchange,
            "sector": company.sector,
            "industry": company.industry,
        }

        llm = LLMService()
        try:
            result = await llm.generate_business_profile(company_data, filing_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

        next_version = 1
        profile = BusinessProfile(
            company_id=company_id,
            version=next_version,
            description=result["description"],
            business_model=result["business_model"],
            competitive_position=result["competitive_position"],
            key_products=result["key_products"],
            geographic_mix=result["geographic_mix"],
            moat_assessment=result["moat_assessment"],
            moat_sources=result["moat_sources"],
        )
        db.add(profile)
        await db.commit()
    
    return profile


@router.post("/generate", response_model=BusinessProfileRead)
async def generate_business_profile(db: DBSession, company_id: UUID):
    """Generate a business profile using LLM + EDGAR filings."""
    company_svc = CompanyService(db)
    company = await company_svc.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Try to get filing text from EDGAR
    filing_text = ""
    if company.cik:
        edgar = EdgarService()
        try:
            filings = await edgar.get_recent_filings(company.cik, "10-K")
            if not filings:
                filings = await edgar.get_recent_filings(company.cik, "10-Q")
            if filings:
                content = await edgar.download_filing(filings[0]["primary_document_url"])
                filing_text = edgar.parse_filing_html(content)
        except Exception:
            filing_text = ""

    if not filing_text:
        # Fallback: use basic company info as context
        filing_text = (
            f"{company.name} ({company.ticker}) is a {company.industry} company "
            f"in the {company.sector} sector, listed on {company.exchange}."
        )

    company_data = {
        "name": company.name,
        "ticker": company.ticker,
        "exchange": company.exchange,
        "sector": company.sector,
        "industry": company.industry,
    }

    llm = LLMService()
    try:
        result = await llm.generate_business_profile(company_data, filing_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM generation failed: {e}")

    # Determine next version
    latest = await db.execute(
        select(BusinessProfile)
        .where(BusinessProfile.company_id == company_id)
        .order_by(BusinessProfile.version.desc())
        .limit(1)
    )
    existing = latest.scalar_one_or_none()
    next_version = (existing.version + 1) if existing else 1

    profile = BusinessProfile(
        company_id=company_id,
        version=next_version,
        description=result["description"],
        business_model=result["business_model"],
        competitive_position=result["competitive_position"],
        key_products=result["key_products"],
        geographic_mix=result["geographic_mix"],
        moat_assessment=result["moat_assessment"],
        moat_sources=result["moat_sources"],
    )
    db.add(profile)
    await db.commit()
    return profile
