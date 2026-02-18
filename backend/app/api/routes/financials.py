from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.financial_snapshot import FinancialSnapshotList, FinancialSnapshotRead
from app.services.financial_ingestion_service import FinancialIngestionService
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
    
    # Auto-ingest if no snapshots exist
    if not items:
        try:
            ingestion = FinancialIngestionService(db)
            await ingestion.ingest_latest_financials(company_id)
            # Retry fetching
            items, total = await service.list_snapshots(company_id, page=page, per_page=per_page)
        except Exception as e:
            pass  # Return empty, user can retry
    
    return FinancialSnapshotList(items=items, total=total, page=page, per_page=per_page)


@router.get("/latest", response_model=FinancialSnapshotRead)
async def get_latest_snapshot(db: DBSession, company_id: UUID):
    service = FinancialService(db)
    snapshot = await service.get_latest(company_id)
    
    # Auto-ingest if no snapshot exists
    if not snapshot:
        try:
            ingestion = FinancialIngestionService(db)
            snapshot = await ingestion.ingest_latest_financials(company_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"No snapshot available: {e}")
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="No financial snapshots found")
    return snapshot


@router.post("/ingest", response_model=FinancialSnapshotRead)
async def ingest_financials(db: DBSession, company_id: UUID):
    """Fetch latest financials from FMP and store in database."""
    service = FinancialIngestionService(db)
    try:
        snapshot = await service.ingest_latest_financials(company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))
    return snapshot
