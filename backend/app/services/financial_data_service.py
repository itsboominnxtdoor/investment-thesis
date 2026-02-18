"""External financial data API service using Alpha Vantage (free, reliable)."""

import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Pulls structured financial data from Alpha Vantage (free tier available)."""

    def __init__(self):
        self.base_url = "https://www.alphavantage.co"
        # Free API key (get yours at https://www.alphavantage.co/support/#api-key)
        # For production, set ALPHA_VANTAGE_API_KEY in environment
        self.api_key = "demo"  # Demo key has limited calls

    @staticmethod
    def resolve_fmp_ticker(ticker: str, exchange: str | None = None) -> str:
        """Resolve ticker for Alpha Vantage."""
        if exchange == "TSX":
            base = ticker.removesuffix(".TO")
            return f"{base}.TO"
        return ticker

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

    async def _get(self, function: str, params: dict | None = None) -> dict:
        params = params or {}
        params["function"] = function
        params["apikey"] = self.api_key
        async with self._client() as client:
            resp = await client.get("/query", params=params)
            if resp.status_code == 429:
                raise RuntimeError("Alpha Vantage rate limit exceeded (5 calls/min, 500/day on free tier)")
            resp.raise_for_status()
            return resp.json()

    async def get_income_statement(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch income statement from Alpha Vantage."""
        try:
            if period == "quarterly":
                data = await self._get("INCOME_STATEMENT", {"symbol": ticker})
            else:
                data = await self._get("INCOME_STATEMENT", {"symbol": ticker})
            
            annual_reports = data.get("annualReports", [])
            quarterly_reports = data.get("quarterlyReports", [])
            
            reports = quarterly_reports if period == "quarterly" else annual_reports
            if not reports:
                logger.warning("No income statement data for %s", ticker)
                return []
            
            return [self._map_income_av(item) for item in reports[:4]]
        except Exception as e:
            logger.warning("Alpha Vantage income statement failed for %s: %s", ticker, e)
            return []

    async def get_balance_sheet(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch balance sheet from Alpha Vantage."""
        try:
            data = await self._get("BALANCE_SHEET", {"symbol": ticker})
            reports = data.get("quarterlyReports", []) if period == "quarterly" else data.get("annualReports", [])
            if not reports:
                return []
            return [self._map_balance_av(item) for item in reports[:4]]
        except Exception as e:
            logger.warning("Alpha Vantage balance sheet failed for %s: %s", ticker, e)
            return []

    async def get_cash_flow(self, ticker: str, period: str = "quarterly") -> list[dict]:
        """Fetch cash flow from Alpha Vantage."""
        try:
            data = await self._get("CASH_FLOW", {"symbol": ticker})
            reports = data.get("quarterlyReports", []) if period == "quarterly" else data.get("annualReports", [])
            if not reports:
                return []
            return [self._map_cashflow_av(item) for item in reports[:4]]
        except Exception as e:
            logger.warning("Alpha Vantage cash flow failed for %s: %s", ticker, e)
            return []

    async def get_segments(self, ticker: str) -> list[dict]:
        """Segment data not available in Alpha Vantage."""
        logger.warning("Segment data not available for %s", ticker)
        return []

    @staticmethod
    def _map_income_av(item: dict) -> dict:
        """Map Alpha Vantage income statement format."""
        def safe_int(val):
            try:
                return int(val) if val and val != "None" else None
            except:
                return None
        
        return {
            "date": item.get("fiscalDateEnding", ""),
            "period": "quarterly",
            "calendar_year": item.get("fiscalDateEnding", "")[:4] if item.get("fiscalDateEnding") else None,
            "revenue": safe_int(item.get("totalRevenue")),
            "cost_of_revenue": safe_int(item.get("costOfRevenue")),
            "gross_profit": safe_int(item.get("grossProfit")),
            "operating_income": safe_int(item.get("operatingIncome")),
            "net_income": safe_int(item.get("netIncome")),
            "ebitda": safe_int(item.get("ebitda")),
            "eps_diluted": item.get("eps"),
            "shares_outstanding": safe_int(item.get("weightedAverageShsOutDil")),
        }

    @staticmethod
    def _map_balance_av(item: dict) -> dict:
        """Map Alpha Vantage balance sheet format."""
        def safe_int(val):
            try:
                return int(val) if val and val != "None" else None
            except:
                return None
        
        return {
            "date": item.get("fiscalDateEnding", ""),
            "period": "quarterly",
            "calendar_year": item.get("fiscalDateEnding", "")[:4] if item.get("fiscalDateEnding") else None,
            "total_assets": safe_int(item.get("totalAssets")),
            "total_liabilities": safe_int(item.get("totalLiabilities")),
            "total_equity": safe_int(item.get("totalShareholderEquity")),
            "cash_and_equivalents": safe_int(item.get("cashAndShortTermInvestments")),
            "total_debt": safe_int(item.get("totalDebt")),
        }

    @staticmethod
    def _map_cashflow_av(item: dict) -> dict:
        """Map Alpha Vantage cash flow format."""
        def safe_int(val):
            try:
                return int(val) if val and val != "None" else None
            except:
                return None
        
        return {
            "date": item.get("fiscalDateEnding", ""),
            "period": "quarterly",
            "calendar_year": item.get("fiscalDateEnding", "")[:4] if item.get("fiscalDateEnding") else None,
            "operating_cash_flow": safe_int(item.get("operatingCashflow")),
            "capital_expenditures": safe_int(item.get("capitalExpenditures")),
            "free_cash_flow": safe_int(item.get("freeCashflow")),
        }
