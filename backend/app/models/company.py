import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.business_profile import BusinessProfile
    from app.models.document import Document
    from app.models.financial_snapshot import FinancialSnapshot
    from app.models.quarterly_update import QuarterlyUpdate
    from app.models.thesis_version import ThesisVersion


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    __table_args__ = (
        Index("ix_companies_ticker", "ticker", unique=True),
        Index("ix_companies_exchange_sector", "exchange", "sector"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    ticker: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    exchange: Mapped[str] = mapped_column(String(10), nullable=False)  # NYSE, NASDAQ, TSX
    sector: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)  # USD or CAD
    cik: Mapped[str | None] = mapped_column(String(20))  # SEC CIK for EDGAR
    sedar_id: Mapped[str | None] = mapped_column(String(20))  # SEDAR+ profile ID
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    financial_snapshots: Mapped[list["FinancialSnapshot"]] = relationship(back_populates="company")
    thesis_versions: Mapped[list["ThesisVersion"]] = relationship(back_populates="company")
    quarterly_updates: Mapped[list["QuarterlyUpdate"]] = relationship(back_populates="company")
    business_profiles: Mapped[list["BusinessProfile"]] = relationship(back_populates="company")
    documents: Mapped[list["Document"]] = relationship(back_populates="company")
