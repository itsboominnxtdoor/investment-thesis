from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.financial_snapshot import FinancialSnapshotList, FinancialSnapshotRead
from app.services.financial_service import FinancialService

router = APIRouter(prefix="/companies/{company_id}/financials", tags=["financials"])


@router.get("", response_model=FinancialSnapshotList)
async def list_snapshots(
    db: DBSession,
    company_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
):
    service = FinancialService(db)
    items, total = await service.list_snapshots(company_id, page=page, per_page=per_page)
    return FinancialSnapshotList(items=items, total=total, page=page, per_page=per_page)


@router.get("/latest", response_model=FinancialSnapshotRead)
async def get_latest_snapshot(db: DBSession, company_id: UUID):
    service = FinancialService(db)
    snapshot = await service.get_latest(company_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No financial snapshots found")
    return snapshot
