import uuid

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class ThesisVersion(Base, TimestampMixin):
    __tablename__ = "thesis_versions"
    __table_args__ = (
        Index("ix_thesis_company_version", "company_id", "version", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    # Three-scenario thesis
    bull_case: Mapped[str] = mapped_column(Text, nullable=False)
    bull_target: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)
    base_case: Mapped[str] = mapped_column(Text, nullable=False)
    base_target: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)
    bear_case: Mapped[str] = mapped_column(Text, nullable=False)
    bear_target: Mapped[Numeric] = mapped_column(Numeric(12, 2), nullable=True)

    # Key drivers & risks
    key_drivers: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    key_risks: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    catalysts: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array

    # Integrity scoring
    thesis_integrity_score: Mapped[Numeric] = mapped_column(Numeric(4, 1), nullable=True)
    integrity_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Drift tracking
    prior_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("thesis_versions.id", ondelete="RESTRICT"), nullable=True
    )
    drift_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    conviction_direction: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # strengthened, weakened, unchanged

    llm_model_used: Mapped[str] = mapped_column(String(100), nullable=False)

    company = relationship("Company", back_populates="thesis_versions")
    snapshot = relationship("FinancialSnapshot")
    prior_version = relationship("ThesisVersion", remote_side="ThesisVersion.id")
