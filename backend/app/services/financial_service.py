from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.financial_snapshot import FinancialSnapshot


class FinancialService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest(self, company_id: UUID) -> FinancialSnapshot | None:
        q = (
            select(FinancialSnapshot)
            .options(selectinload(FinancialSnapshot.segments))
            .where(FinancialSnapshot.company_id == company_id)
            .order_by(
                FinancialSnapshot.fiscal_year.desc(),
                FinancialSnapshot.fiscal_quarter.desc(),
            )
            .limit(1)
        )
        result = await self.db.execute(q)
        return result.scalar_one_or_none()

    async def list_snapshots(
        self, company_id: UUID, page: int = 1, per_page: int = 10
    ) -> tuple[list[FinancialSnapshot], int]:
        count_q = (
            select(func.count()).where(FinancialSnapshot.company_id == company_id)
        )
        total = (await self.db.execute(count_q)).scalar_one()

        q = (
            select(FinancialSnapshot)
            .options(selectinload(FinancialSnapshot.segments))
            .where(FinancialSnapshot.company_id == company_id)
            .order_by(
                FinancialSnapshot.fiscal_year.desc(),
                FinancialSnapshot.fiscal_quarter.desc(),
            )
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(q)
        items = list(result.scalars().unique().all())
        return items, total
