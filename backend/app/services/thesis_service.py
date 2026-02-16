from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.thesis_version import ThesisVersion


class ThesisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, version_id: UUID) -> ThesisVersion | None:
        result = await self.db.execute(
            select(ThesisVersion).where(ThesisVersion.id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_latest(self, company_id: UUID) -> ThesisVersion | None:
        q = (
            select(ThesisVersion)
            .where(ThesisVersion.company_id == company_id)
            .order_by(ThesisVersion.version.desc())
            .limit(1)
        )
        result = await self.db.execute(q)
        return result.scalar_one_or_none()

    async def list_versions(
        self, company_id: UUID, page: int = 1, per_page: int = 10
    ) -> tuple[list[ThesisVersion], int]:
        count_q = select(func.count()).where(ThesisVersion.company_id == company_id)
        total = (await self.db.execute(count_q)).scalar_one()

        q = (
            select(ThesisVersion)
            .where(ThesisVersion.company_id == company_id)
            .order_by(ThesisVersion.version.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        return items, total
