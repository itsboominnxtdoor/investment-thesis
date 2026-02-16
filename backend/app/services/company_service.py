from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, company_id: UUID) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_by_ticker(self, ticker: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.ticker == ticker))
        return result.scalar_one_or_none()

    async def list_companies(
        self,
        page: int = 1,
        per_page: int = 25,
        search: str | None = None,
        sector: str | None = None,
        exchange: str | None = None,
    ) -> tuple[list[Company], int]:
        conditions = [Company.is_active.is_(True)]

        if search:
            pattern = f"%{search}%"
            conditions.append(
                (Company.ticker.ilike(pattern)) | (Company.name.ilike(pattern))
            )
        if sector:
            conditions.append(Company.sector == sector)
        if exchange:
            conditions.append(Company.exchange == exchange)

        count_q = select(func.count()).select_from(Company).where(*conditions)
        total = (await self.db.execute(count_q)).scalar_one()

        q = (
            select(Company)
            .where(*conditions)
            .order_by(Company.ticker)
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        return items, total
