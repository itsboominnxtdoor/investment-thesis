"""External financial data API service for pulling structured financial data."""

from app.config import settings


class FinancialDataService:
    """Pulls structured financial data (income statement, balance sheet, cash flow)."""

    def __init__(self):
        self.api_key = settings.FINANCIAL_DATA_API_KEY

    async def get_income_statement(self, ticker: str, period: str = "quarterly") -> dict:
        """Fetch income statement data."""
        raise NotImplementedError("Financial data API not yet implemented")

    async def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> dict:
        """Fetch balance sheet data."""
        raise NotImplementedError("Financial data API not yet implemented")

    async def get_cash_flow(self, ticker: str, period: str = "quarterly") -> dict:
        """Fetch cash flow statement data."""
        raise NotImplementedError("Financial data API not yet implemented")

    async def get_segments(self, ticker: str) -> list[dict]:
        """Fetch business segment breakdown."""
        raise NotImplementedError("Financial data API not yet implemented")
