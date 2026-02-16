from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class BusinessProfileRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    company_id: UUID
    version: int
    description: str
    business_model: str
    competitive_position: str
    key_products: str
    geographic_mix: str
    moat_assessment: str
    moat_sources: str
    created_at: datetime
