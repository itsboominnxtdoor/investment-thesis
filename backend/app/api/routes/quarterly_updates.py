from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import DBSession
from app.schemas.quarterly_update import QuarterlyUpdateList, QuarterlyUpdateRead
from app.services.company_service import CompanyService

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
    from app.models.quarterly_update import QuarterlyUpdate
    from sqlalchemy import func, select

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
    from app.models.quarterly_update import QuarterlyUpdate
    from sqlalchemy import select

    q = select(QuarterlyUpdate).where(
        QuarterlyUpdate.id == update_id, QuarterlyUpdate.company_id == company_id
    )
    result = await db.execute(q)
    update = result.scalar_one_or_none()
    if not update:
        raise HTTPException(status_code=404, detail="Quarterly update not found")
    return update
