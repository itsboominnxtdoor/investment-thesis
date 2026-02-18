"""External financial data API service using Yahoo Finance."""

import logging

import httpx

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Pulls structured financial data from Yahoo Finance (free, no API key required)."""

    def __init__(self):
        self.base_url = "https://query1.finance.yahoo.com"

    @staticmethod
    def resolve_fmp_ticker(ticker: str, exchange: str | None = None) -> str:
        """Resolve ticker for Yahoo Finance. TSX tickers need .TO suffix."""
        if exchange == "TSX":
            base = ticker.removesuffix(".TO")
            return f"{base}.TO"
        return ticker

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=30.0, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    async def _get(self, path: str, params: dict | None = None) -> list | dict:
        async with self._client() as client:
            resp = await client.get(path, params=params or {})
            if resp.status_code == 429:
                raise RuntimeError("Yahoo Finance rate limit exceeded. Try again later.")
            resp.raise_for_status()
            return resp.json()

    async def get_income_statement(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch income statement from Yahoo Finance."""
        try:
            data = await self._get(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "incomeStatementHistory,incomeStatementHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            if period == "quarterly":
                statements = result.get("incomeStatementHistoryQuarterly", {}).get("incomeStatementHistory", [])
            else:
                statements = result.get("incomeStatementHistory", {}).get("incomeStatementHistory", [])
            return [self._map_income(item) for item in (statements[:4] if statements else [])]
        except Exception as e:
            logger.warning("Yahoo income statement failed for %s: %s", ticker, e)
            return []

    async def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch balance sheet from Yahoo Finance."""
        try:
            data = await self._get(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "balanceSheetHistory,balanceSheetHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            if period == "quarterly":
                statements = result.get("balanceSheetHistoryQuarterly", {}).get("balanceSheetStatements", [])
            else:
                statements = result.get("balanceSheetHistory", {}).get("balanceSheetStatements", [])
            return [self._map_balance(item) for item in (statements[:4] if statements else [])]
        except Exception as e:
            logger.warning("Yahoo balance sheet failed for %s: %s", ticker, e)
            return []

    async def get_cash_flow(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch cash flow from Yahoo Finance."""
        try:
            data = await self._get(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "cashflowStatementHistory,cashflowStatementHistoryQuarterly"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            if period == "quarterly":
                statements = result.get("cashflowStatementHistoryQuarterly", {}).get("cashflowStatements", [])
            else:
                statements = result.get("cashflowStatementHistory", {}).get("cashflowStatements", [])
            return [self._map_cashflow(item) for item in (statements[:4] if statements else [])]
        except Exception as e:
            logger.warning("Yahoo cash flow failed for %s: %s", ticker, e)
            return []

    async def get_segments(self, ticker: str) -> list[dict]:
        """Fetch segment data from Yahoo Finance."""
        try:
            data = await self._get(
                f"/v10/finance/quoteSummary/{ticker}",
                {"modules": "segment"}
            )
            result = data.get("quoteSummary", {}).get("result", [{}])[0]
            segments = result.get("segment", {}).get("segment", [])
            return [{"name": s.get("name", "Other"), "revenue": s.get("revenue", {}).get("raw", 0)} for s in (segments or [])]
        except Exception:
            logger.warning("Segments not available for %s", ticker)
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
