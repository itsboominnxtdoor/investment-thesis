from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QuarterlyUpdateRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    company_id: UUID
    snapshot_id: UUID
    thesis_version_id: UUID
    fiscal_year: int
    fiscal_quarter: int
    filing_type: str
    executive_summary: str
    key_changes: str
    guidance_update: str | None = None
    management_commentary: str | None = None
    created_at: datetime


class QuarterlyUpdateList(BaseModel):
    items: list[QuarterlyUpdateRead]
    total: int
    page: int
    per_page: int
