from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CompanyRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    ticker: str
    name: str
    exchange: str
    sector: str
    industry: str
    currency: str
    cik: str | None = None
    sedar_id: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyList(BaseModel):
    items: list[CompanyRead]
    total: int
    page: int
    per_page: int
