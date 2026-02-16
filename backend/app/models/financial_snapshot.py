import uuid

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid


class FinancialSnapshot(Base, TimestampMixin):
    __tablename__ = "financial_snapshots"
    __table_args__ = (
        Index(
            "ix_snapshots_company_period",
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
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    fiscal_quarter: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-4
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    # Income statement
    revenue: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    cost_of_revenue: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    gross_profit: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    operating_income: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    net_income: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    ebitda: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    eps_diluted: Mapped[Numeric] = mapped_column(Numeric(12, 4), nullable=True)
    shares_outstanding: Mapped[Numeric] = mapped_column(Numeric(16, 0), nullable=True)

    # Balance sheet
    total_assets: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    total_liabilities: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    total_equity: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    cash_and_equivalents: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    total_debt: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)

    # Cash flow
    operating_cash_flow: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    capital_expenditures: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    free_cash_flow: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)

    # Margins & ratios
    gross_margin: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)
    operating_margin: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)
    net_margin: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)
    roe: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)
    debt_to_equity: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)

    company = relationship("Company", back_populates="financial_snapshots")
    segments: Mapped[list["Segment"]] = relationship(back_populates="snapshot")


class Segment(Base, TimestampMixin):
    __tablename__ = "segments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    revenue: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    operating_income: Mapped[Numeric] = mapped_column(Numeric(20, 2), nullable=True)
    revenue_pct: Mapped[Numeric] = mapped_column(Numeric(8, 4), nullable=True)

    snapshot = relationship("FinancialSnapshot", back_populates="segments")
