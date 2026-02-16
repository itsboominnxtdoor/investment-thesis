from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.thesis_version import ThesisVersionList, ThesisVersionRead
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
