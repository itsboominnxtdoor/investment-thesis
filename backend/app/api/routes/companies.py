from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.company import CompanyList, CompanyRead
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["companies"])


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
    service = CompanyService(db)
    company = await service.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/ticker/{ticker}", response_model=CompanyRead)
async def get_company_by_ticker(db: DBSession, ticker: str):
    service = CompanyService(db)
    company = await service.get_by_ticker(ticker.upper())
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
