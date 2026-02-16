"""Service for ingesting financial data from FMP into the database."""

import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.financial_snapshot import FinancialSnapshot, Segment
from app.services.financial_data_service import FinancialDataService

logger = logging.getLogger(__name__)

QUARTER_MAP = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}


def _to_decimal(val) -> Decimal | None:
    if val is None:
        return None
    return Decimal(str(val))


def _safe_divide(num, denom) -> Decimal | None:
    if num is None or denom is None or denom == 0:
        return None
    return Decimal(str(num)) / Decimal(str(denom))


class FinancialIngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fmp = FinancialDataService()

    async def ingest_latest_financials(self, company_id: UUID) -> FinancialSnapshot:
        # Look up company
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise ValueError(f"Company {company_id} not found")

        ticker = company.ticker

        # Fetch all 4 data sources in parallel-ish (sequential for simplicity)
        income_data = await self.fmp.get_income_statement(ticker)
        balance_data = await self.fmp.get_balance_sheet(ticker)
        cashflow_data = await self.fmp.get_cash_flow(ticker)
        segments_data = await self.fmp.get_segments(ticker)

        if not income_data:
            raise ValueError(f"No income statement data available for {ticker}")

        # Use the most recent period
        inc = income_data[0]
        bal = balance_data[0] if balance_data else {}
        cf = cashflow_data[0] if cashflow_data else {}

        # Parse fiscal period
        period_str = inc.get("period", "Q1")
        calendar_year = inc.get("calendar_year")
        fiscal_quarter = QUARTER_MAP.get(period_str, 1)
        fiscal_year = int(calendar_year) if calendar_year else 2025

        # Check for existing snapshot at this period
        existing = await self.db.execute(
            select(FinancialSnapshot).where(
                FinancialSnapshot.company_id == company_id,
                FinancialSnapshot.fiscal_year == fiscal_year,
                FinancialSnapshot.fiscal_quarter == fiscal_quarter,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"Snapshot already exists for {ticker} Q{fiscal_quarter} {fiscal_year}"
            )

        # Compute derived margins
        revenue = inc.get("revenue")
        gross_profit = inc.get("gross_profit")
        operating_income = inc.get("operating_income")
        net_income = inc.get("net_income")
        total_equity = bal.get("total_equity")
        total_debt = bal.get("total_debt")

        gross_margin = _safe_divide(gross_profit, revenue)
        operating_margin = _safe_divide(operating_income, revenue)
        net_margin = _safe_divide(net_income, revenue)
        roe = _safe_divide(net_income, total_equity)
        debt_to_equity = _safe_divide(total_debt, total_equity)

        snapshot = FinancialSnapshot(
            company_id=company_id,
            fiscal_year=fiscal_year,
            fiscal_quarter=fiscal_quarter,
            currency=company.currency,
            # Income statement
            revenue=_to_decimal(revenue),
            cost_of_revenue=_to_decimal(inc.get("cost_of_revenue")),
            gross_profit=_to_decimal(gross_profit),
            operating_income=_to_decimal(operating_income),
            net_income=_to_decimal(net_income),
            ebitda=_to_decimal(inc.get("ebitda")),
            eps_diluted=_to_decimal(inc.get("eps_diluted")),
            shares_outstanding=_to_decimal(inc.get("shares_outstanding")),
            # Balance sheet
            total_assets=_to_decimal(bal.get("total_assets")),
            total_liabilities=_to_decimal(bal.get("total_liabilities")),
            total_equity=_to_decimal(total_equity),
            cash_and_equivalents=_to_decimal(bal.get("cash_and_equivalents")),
            total_debt=_to_decimal(total_debt),
            # Cash flow
            operating_cash_flow=_to_decimal(cf.get("operating_cash_flow")),
            capital_expenditures=_to_decimal(cf.get("capital_expenditures")),
            free_cash_flow=_to_decimal(cf.get("free_cash_flow")),
            # Derived ratios
            gross_margin=gross_margin,
            operating_margin=operating_margin,
            net_margin=net_margin,
            roe=roe,
            debt_to_equity=debt_to_equity,
        )
        self.db.add(snapshot)
        await self.db.flush()

        # Add segment records
        total_seg_revenue = sum(s.get("revenue", 0) or 0 for s in segments_data)
        for seg in segments_data:
            seg_rev = seg.get("revenue")
            rev_pct = _safe_divide(seg_rev, total_seg_revenue) if total_seg_revenue else None
            segment = Segment(
                snapshot_id=snapshot.id,
                name=seg["name"],
                revenue=_to_decimal(seg_rev),
                revenue_pct=rev_pct,
            )
            self.db.add(segment)

        await self.db.commit()
        logger.info("Ingested financials for %s Q%d %d", ticker, fiscal_quarter, fiscal_year)
        return snapshot
