from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ThesisVersionRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    company_id: UUID
    snapshot_id: UUID
    version: int

    bull_case: str
    bull_target: Decimal | None = None
    base_case: str
    base_target: Decimal | None = None
    bear_case: str
    bear_target: Decimal | None = None

    key_drivers: str
    key_risks: str
    catalysts: str

    thesis_integrity_score: Decimal | None = None
    integrity_rationale: str | None = None

    prior_version_id: UUID | None = None
    drift_summary: str | None = None
    conviction_direction: str | None = None

    llm_model_used: str
    created_at: datetime


class ThesisVersionList(BaseModel):
    items: list[ThesisVersionRead]
    total: int
    page: int
    per_page: int
