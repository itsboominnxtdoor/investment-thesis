"""External financial data API service using Yahoo Finance (primary) and FMP (fallback)."""

import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Pulls structured financial data from Yahoo Finance (free) with FMP fallback."""

    def __init__(self):
        self.yahoo_base = "https://query1.finance.yahoo.com"
        self.fmp_base = settings.FMP_API_BASE_URL
        self.fmp_key = settings.FINANCIAL_DATA_API_KEY

    @staticmethod
    def resolve_fmp_ticker(ticker: str, exchange: str | None = None) -> str:
        """Resolve ticker for Yahoo Finance. TSX tickers need .TO suffix."""
        if exchange == "TSX":
            base = ticker.removesuffix(".TO")
            return f"{base}.TO"
        return ticker

    def _yahoo_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.yahoo_base,
            timeout=30.0,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        )

    def _fmp_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.fmp_base, timeout=30.0)

    async def _get_yahoo(self, path: str, params: dict | None = None) -> list | dict:
        async with self._yahoo_client() as client:
            resp = await client.get(path, params=params or {})
            if resp.status_code == 429:
                raise RuntimeError("Yahoo Finance rate limit exceeded")
            resp.raise_for_status()
            return resp.json()

    async def _get_fmp(self, path: str, params: dict | None = None) -> list | dict:
        if not self.fmp_key:
            raise ValueError("No FMP API key configured")
        params = params or {}
        params["apikey"] = self.fmp_key
        async with self._fmp_client() as client:
            resp = await client.get(path, params=params)
            if resp.status_code == 429:
                raise RuntimeError("FMP rate limit exceeded")
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "Error Message" in data:
                raise ValueError(f"FMP API error: {data['Error Message']}")
            return data

    async def get_income_statement(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch income statement - Yahoo primary, FMP fallback."""
        # Try Yahoo Finance first
        try:
            data = await self._get_yahoo(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "incomeStatementHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            statements = result.get("incomeStatementHistoryQuarterly", {}).get("incomeStatementHistory", [])
            if statements:
                return [self._map_income(item) for item in statements[:4]]
        except Exception as e:
            logger.warning("Yahoo income statement failed for %s: %s", ticker, e)

        # Fallback to FMP v4
        if self.fmp_key:
            try:
                await asyncio.sleep(0.5)  # Rate limit buffer
                data = await self._get_fmp(
                    f"/api/v4/income-statement/{ticker}",
                    {"period": period, "limit": 4}
                )
                if data and isinstance(data, list):
                    return [self._map_income(item) for item in data]
            except Exception as e:
                logger.warning("FMP income statement failed for %s: %s", ticker, e)

        return []

    async def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch balance sheet - Yahoo primary, FMP fallback."""
        try:
            data = await self._get_yahoo(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "balanceSheetHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            statements = result.get("balanceSheetHistoryQuarterly", {}).get("balanceSheetStatements", [])
            if statements:
                return [self._map_balance(item) for item in statements[:4]]
        except Exception as e:
            logger.warning("Yahoo balance sheet failed for %s: %s", ticker, e)

        # Fallback to FMP v4
        if self.fmp_key:
            try:
                await asyncio.sleep(0.5)
                data = await self._get_fmp(
                    f"/api/v4/balance-sheet-statement/{ticker}",
                    {"period": period, "limit": 4}
                )
                if data and isinstance(data, list):
                    return [self._map_balance(item) for item in data]
            except Exception as e:
                logger.warning("FMP balance sheet failed for %s: %s", ticker, e)

        return []

    async def get_cash_flow(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch cash flow - Yahoo primary, FMP fallback."""
        try:
            data = await self._get_yahoo(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "cashflowStatementHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            statements = result.get("cashflowStatementHistoryQuarterly", {}).get("cashflowStatements", [])
            if statements:
                return [self._map_cashflow(item) for item in statements[:4]]
        except Exception as e:
            logger.warning("Yahoo cash flow failed for %s: %s", ticker, e)

        # Fallback to FMP v4
        if self.fmp_key:
            try:
                await asyncio.sleep(0.5)
                data = await self._get_fmp(
                    f"/api/v4/cash-flow-statement/{ticker}",
                    {"period": period, "limit": 4}
                )
                if data and isinstance(data, list):
                    return [self._map_cashflow(item) for item in data]
            except Exception as e:
                logger.warning("FMP cash flow failed for %s: %s", ticker, e)

        return []

    async def get_segments(self, ticker: str) -> list[dict]:
        """Fetch segment data - Yahoo primary, FMP fallback."""
        try:
            data = await self._get_yahoo(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "segment"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            segments = result.get("segment", {}).get("segment", [])
            if segments:
                return [{"name": s.get("name", "Other"), "revenue": s.get("revenue", {}).get("raw", 0)} for s in segments]
        except Exception:
            logger.warning("Yahoo segments failed for %s", ticker)

        # Fallback to FMP
        if self.fmp_key:
            try:
                await asyncio.sleep(0.5)
                data = await self._get_fmp(
                    "/api/v4/revenue-product-segmentation",
                    {"symbol": ticker, "structure": "flat"}
                )
                if data and isinstance(data, list):
                    latest = data[0] if data else {}
                    return [{"name": k, "revenue": v} for k, v in latest.items() if k != "date"]
            except Exception:
                logger.warning("FMP segments failed for %s", ticker)

        return []

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
