"""External financial data API service using Financial Modeling Prep (FMP)."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Pulls structured financial data from FMP (income statement, balance sheet, cash flow)."""

    def __init__(self):
        self.api_key = settings.FINANCIAL_DATA_API_KEY
        self.base_url = settings.FMP_API_BASE_URL

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def _get(self, path: str, params: dict | None = None) -> list | dict:
        params = params or {}
        params["apikey"] = self.api_key
        async with self._client() as client:
            resp = await client.get(path, params=params)
            if resp.status_code == 429:
                raise RuntimeError("FMP rate limit exceeded. Try again later.")
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "Error Message" in data:
                raise ValueError(f"FMP API error: {data['Error Message']}")
            return data

    async def get_income_statement(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch income statement data from FMP."""
        data = await self._get(
            f"/api/v3/income-statement/{ticker}",
            {"period": period, "limit": 4},
        )
        if not data:
            return []
        return [self._map_income(item) for item in data]

    async def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch balance sheet data from FMP."""
        data = await self._get(
            f"/api/v3/balance-sheet-statement/{ticker}",
            {"period": period, "limit": 4},
        )
        if not data:
            return []
        return [self._map_balance(item) for item in data]

    async def get_cash_flow(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch cash flow statement data from FMP."""
        data = await self._get(
            f"/api/v3/cash-flow-statement/{ticker}",
            {"period": period, "limit": 4},
        )
        if not data:
            return []
        return [self._map_cashflow(item) for item in data]

    async def get_segments(self, ticker: str) -> list[dict]:
        """Fetch revenue product segmentation from FMP v4."""
        try:
            data = await self._get(
                "/api/v4/revenue-product-segmentation",
                {"symbol": ticker, "structure": "flat"},
            )
        except Exception:
            logger.warning("Segments not available for %s", ticker)
            return []
        if not data:
            return []
        # FMP returns a list of dicts, each with a date key and segment data
        # Take the most recent period
        latest = data[0] if data else {}
        segments = []
        for key, value in latest.items():
            if key in ("date",):
                continue
            segments.append({"name": key, "revenue": value})
        return segments

    @staticmethod
    def _map_income(item: dict) -> dict:
        return {
            "date": item.get("date"),
            "period": item.get("period"),
            "calendar_year": item.get("calendarYear"),
            "revenue": item.get("revenue"),
            "cost_of_revenue": item.get("costOfRevenue"),
            "gross_profit": item.get("grossProfit"),
            "operating_income": item.get("operatingIncome"),
            "net_income": item.get("netIncome"),
            "ebitda": item.get("ebitda"),
            "eps_diluted": item.get("epsdiluted"),
            "shares_outstanding": item.get("weightedAverageShsOutDil"),
        }

    @staticmethod
    def _map_balance(item: dict) -> dict:
        return {
            "date": item.get("date"),
            "period": item.get("period"),
            "calendar_year": item.get("calendarYear"),
            "total_assets": item.get("totalAssets"),
            "total_liabilities": item.get("totalLiabilities"),
            "total_equity": item.get("totalStockholdersEquity"),
            "cash_and_equivalents": item.get("cashAndCashEquivalents"),
            "total_debt": item.get("totalDebt"),
        }

    @staticmethod
    def _map_cashflow(item: dict) -> dict:
        return {
            "date": item.get("date"),
            "period": item.get("period"),
            "calendar_year": item.get("calendarYear"),
            "operating_cash_flow": item.get("operatingCashFlow"),
            "capital_expenditures": item.get("capitalExpenditure"),
            "free_cash_flow": item.get("freeCashFlow"),
        }
