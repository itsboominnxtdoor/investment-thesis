import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class QuarterlyUpdate(Base, TimestampMixin):
    __tablename__ = "quarterly_updates"
    __table_args__ = (
        Index(
            "ix_quarterly_company_period",
            "company_id",
            "fiscal_year",
            "fiscal_quarter",
            unique=True,
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False
    )
    thesis_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("thesis_versions.id", ondelete="RESTRICT"), nullable=False
    )

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    fiscal_quarter: Mapped[int] = mapped_column(Integer, nullable=False)
    filing_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 10-Q, 10-K, etc.

    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    key_changes: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    guidance_update: Mapped[str | None] = mapped_column(Text, nullable=True)
    management_commentary: Mapped[str | None] = mapped_column(Text, nullable=True)

    company = relationship("Company", back_populates="quarterly_updates")
    snapshot = relationship("FinancialSnapshot")
    thesis_version = relationship("ThesisVersion")
