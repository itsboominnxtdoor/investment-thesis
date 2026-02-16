from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    company_id: UUID
    doc_type: str
    source: str
    source_url: str
    s3_key: str | None = None
    file_size_bytes: int | None = None
    filing_date: str | None = None
    created_at: datetime


class DocumentList(BaseModel):
    items: list[DocumentRead]
    total: int
    page: int
    per_page: int
