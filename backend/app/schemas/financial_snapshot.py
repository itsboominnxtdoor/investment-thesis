from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class SegmentRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    name: str
    revenue: Decimal | None = None
    operating_income: Decimal | None = None
    revenue_pct: Decimal | None = None


class FinancialSnapshotRead(BaseModel):
    model_config = {"from_attributes": True}

    id: UUID
    company_id: UUID
    fiscal_year: int
    fiscal_quarter: int
    currency: str

    revenue: Decimal | None = None
    cost_of_revenue: Decimal | None = None
    gross_profit: Decimal | None = None
    operating_income: Decimal | None = None
    net_income: Decimal | None = None
    ebitda: Decimal | None = None
    eps_diluted: Decimal | None = None
    shares_outstanding: Decimal | None = None

    total_assets: Decimal | None = None
    total_liabilities: Decimal | None = None
    total_equity: Decimal | None = None
    cash_and_equivalents: Decimal | None = None
    total_debt: Decimal | None = None

    operating_cash_flow: Decimal | None = None
    capital_expenditures: Decimal | None = None
    free_cash_flow: Decimal | None = None

    gross_margin: Decimal | None = None
    operating_margin: Decimal | None = None
    net_margin: Decimal | None = None
    roe: Decimal | None = None
    debt_to_equity: Decimal | None = None

    segments: list[SegmentRead] = []
    created_at: datetime


class FinancialSnapshotList(BaseModel):
    items: list[FinancialSnapshotRead]
    total: int
    page: int
    per_page: int


class StockQuoteRead(BaseModel):
    symbol: str
    price: float
    change: float
    change_pct: float
    prev_close: float
    latest_trading_day: str
