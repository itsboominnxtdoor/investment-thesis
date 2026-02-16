import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class BusinessProfile(Base, TimestampMixin):
    __tablename__ = "business_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    business_model: Mapped[str] = mapped_column(Text, nullable=False)
    competitive_position: Mapped[str] = mapped_column(Text, nullable=False)
    key_products: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text
    geographic_mix: Mapped[str] = mapped_column(Text, nullable=False)  # JSON object as text
    moat_assessment: Mapped[str] = mapped_column(String(50), nullable=False)
    moat_sources: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array as text

    company = relationship("Company", back_populates="business_profiles")
