"""Tests for FinancialDataService — FMP response mapping, ticker suffix logic."""

import pytest

from app.services.financial_data_service import FinancialDataService


class TestResolveFmpTicker:
    def test_us_ticker_unchanged(self):
        assert FinancialDataService.resolve_fmp_ticker("AAPL", "NASDAQ") == "AAPL"
        assert FinancialDataService.resolve_fmp_ticker("JPM", "NYSE") == "JPM"

    def test_tsx_ticker_gets_to_suffix(self):
        assert FinancialDataService.resolve_fmp_ticker("RY", "TSX") == "RY.TO"
        assert FinancialDataService.resolve_fmp_ticker("SHOP", "TSX") == "SHOP.TO"

    def test_tsx_ticker_no_double_suffix(self):
        assert FinancialDataService.resolve_fmp_ticker("T.TO", "TSX") == "T.TO"

    def test_tsx_unit_trust_suffix(self):
        assert FinancialDataService.resolve_fmp_ticker("CAR.UN", "TSX") == "CAR-UN.TO"

    def test_tsx_class_b_suffix(self):
        assert FinancialDataService.resolve_fmp_ticker("RCI.B", "TSX") == "RCI-B.TO"

    def test_no_exchange_returns_as_is(self):
        assert FinancialDataService.resolve_fmp_ticker("MSFT") == "MSFT"
        assert FinancialDataService.resolve_fmp_ticker("MSFT", None) == "MSFT"


class TestMapIncome:
    def test_maps_all_fields(self):
        raw = {
            "date": "2025-03-31",
            "period": "Q1",
            "calendarYear": "2025",
            "revenue": 100_000_000,
            "costOfRevenue": 40_000_000,
            "grossProfit": 60_000_000,
            "operatingIncome": 30_000_000,
            "netIncome": 25_000_000,
            "ebitda": 35_000_000,
            "epsdiluted": 2.50,
            "weightedAverageShsOutDil": 10_000_000,
        }
        result = FinancialDataService._map_income(raw)
        assert result["revenue"] == 100_000_000
        assert result["net_income"] == 25_000_000
        assert result["eps_diluted"] == 2.50
        assert result["calendar_year"] == "2025"
        assert result["period"] == "Q1"

    def test_handles_missing_fields(self):
        result = FinancialDataService._map_income({})
        assert result["revenue"] is None
        assert result["net_income"] is None


class TestMapBalance:
    def test_maps_all_fields(self):
        raw = {
            "date": "2025-03-31",
            "period": "Q1",
            "calendarYear": "2025",
            "totalAssets": 500_000_000,
            "totalLiabilities": 200_000_000,
            "totalStockholdersEquity": 300_000_000,
            "cashAndCashEquivalents": 50_000_000,
            "totalDebt": 100_000_000,
        }
        result = FinancialDataService._map_balance(raw)
        assert result["total_assets"] == 500_000_000
        assert result["total_equity"] == 300_000_000


class TestMapCashflow:
    def test_maps_all_fields(self):
        raw = {
            "date": "2025-03-31",
            "period": "Q1",
            "calendarYear": "2025",
            "operatingCashFlow": 40_000_000,
            "capitalExpenditure": -10_000_000,
            "freeCashFlow": 30_000_000,
        }
        result = FinancialDataService._map_cashflow(raw)
        assert result["operating_cash_flow"] == 40_000_000
        assert result["free_cash_flow"] == 30_000_000
