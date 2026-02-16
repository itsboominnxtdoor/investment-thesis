"""Seed the companies table with a universe of S&P 500 large-caps and select TSX names."""

import asyncio

from sqlalchemy import text

from app.database import async_session_factory

COMPANIES = [
    # Technology
    ("AAPL", "Apple Inc.", "NASDAQ", "Technology", "Consumer Electronics", "USD", "0000320193"),
    ("MSFT", "Microsoft Corporation", "NASDAQ", "Technology", "Software - Infrastructure", "USD", "0000789019"),
    ("GOOGL", "Alphabet Inc.", "NASDAQ", "Technology", "Internet Content & Information", "USD", "0001652044"),
    ("AMZN", "Amazon.com Inc.", "NASDAQ", "Technology", "Internet Retail", "USD", "0001018724"),
    ("NVDA", "NVIDIA Corporation", "NASDAQ", "Technology", "Semiconductors", "USD", "0001045810"),
    ("META", "Meta Platforms Inc.", "NASDAQ", "Technology", "Internet Content & Information", "USD", "0001326801"),
    ("TSM", "Taiwan Semiconductor Manufacturing", "NYSE", "Technology", "Semiconductors", "USD", "0001046179"),
    ("AVGO", "Broadcom Inc.", "NASDAQ", "Technology", "Semiconductors", "USD", "0001649338"),
    ("CRM", "Salesforce Inc.", "NYSE", "Technology", "Software - Application", "USD", "0001108524"),
    ("ORCL", "Oracle Corporation", "NYSE", "Technology", "Software - Infrastructure", "USD", "0001341439"),
    # Financials
    ("JPM", "JPMorgan Chase & Co.", "NYSE", "Financials", "Banks - Diversified", "USD", "0000019617"),
    ("V", "Visa Inc.", "NYSE", "Financials", "Credit Services", "USD", "0001403161"),
    ("MA", "Mastercard Incorporated", "NYSE", "Financials", "Credit Services", "USD", "0001141391"),
    ("BAC", "Bank of America Corporation", "NYSE", "Financials", "Banks - Diversified", "USD", "0000070858"),
    ("GS", "Goldman Sachs Group Inc.", "NYSE", "Financials", "Capital Markets", "USD", "0000886982"),
    # Healthcare
    ("UNH", "UnitedHealth Group Inc.", "NYSE", "Healthcare", "Healthcare Plans", "USD", "0000731766"),
    ("JNJ", "Johnson & Johnson", "NYSE", "Healthcare", "Drug Manufacturers", "USD", "0000200406"),
    ("LLY", "Eli Lilly and Company", "NYSE", "Healthcare", "Drug Manufacturers", "USD", "0000059478"),
    ("PFE", "Pfizer Inc.", "NYSE", "Healthcare", "Drug Manufacturers", "USD", "0000078003"),
    ("ABBV", "AbbVie Inc.", "NYSE", "Healthcare", "Drug Manufacturers", "USD", "0001551152"),
    # Consumer
    ("WMT", "Walmart Inc.", "NYSE", "Consumer Defensive", "Discount Stores", "USD", "0000104169"),
    ("PG", "Procter & Gamble Company", "NYSE", "Consumer Defensive", "Household Products", "USD", "0000080424"),
    ("KO", "Coca-Cola Company", "NYSE", "Consumer Defensive", "Beverages", "USD", "0000021344"),
    ("PEP", "PepsiCo Inc.", "NYSE", "Consumer Defensive", "Beverages", "USD", "0000077476"),
    ("COST", "Costco Wholesale Corporation", "NASDAQ", "Consumer Defensive", "Discount Stores", "USD", "0000909832"),
    # Industrials
    ("CAT", "Caterpillar Inc.", "NYSE", "Industrials", "Farm & Heavy Construction Machinery", "USD", "0000018230"),
    ("GE", "GE Aerospace", "NYSE", "Industrials", "Aerospace & Defense", "USD", "0000040554"),
    ("UNP", "Union Pacific Corporation", "NYSE", "Industrials", "Railroads", "USD", "0000100885"),
    ("HON", "Honeywell International Inc.", "NASDAQ", "Industrials", "Conglomerates", "USD", "0000773840"),
    # Energy
    ("XOM", "Exxon Mobil Corporation", "NYSE", "Energy", "Oil & Gas Integrated", "USD", "0000034088"),
    ("CVX", "Chevron Corporation", "NYSE", "Energy", "Oil & Gas Integrated", "USD", "0000093410"),
    # Communication Services
    ("DIS", "Walt Disney Company", "NYSE", "Communication Services", "Entertainment", "USD", "0001744489"),
    ("NFLX", "Netflix Inc.", "NASDAQ", "Communication Services", "Entertainment", "USD", "0001065280"),
    # Real Estate
    ("AMT", "American Tower Corporation", "NYSE", "Real Estate", "REIT - Specialty", "USD", "0001053507"),
    # Utilities
    ("NEE", "NextEra Energy Inc.", "NYSE", "Utilities", "Utilities - Regulated Electric", "USD", "0000753308"),
    # TSX Companies (Canadian)
    ("RY", "Royal Bank of Canada", "TSX", "Financials", "Banks - Diversified", "CAD", None),
    ("TD", "Toronto-Dominion Bank", "TSX", "Financials", "Banks - Diversified", "CAD", None),
    ("SHOP", "Shopify Inc.", "TSX", "Technology", "Software - Application", "CAD", None),
    ("ENB", "Enbridge Inc.", "TSX", "Energy", "Oil & Gas Midstream", "CAD", None),
    ("CNR", "Canadian National Railway", "TSX", "Industrials", "Railroads", "CAD", None),
]


async def seed():
    async with async_session_factory() as session:
        for ticker, name, exchange, sector, industry, currency, cik in COMPANIES:
            await session.execute(
                text(
                    """
                    INSERT INTO companies (id, ticker, name, exchange, sector, industry, currency, cik, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), :ticker, :name, :exchange, :sector, :industry, :currency, :cik, true, now(), now())
                    ON CONFLICT (ticker) DO NOTHING
                    """
                ),
                {
                    "ticker": ticker,
                    "name": name,
                    "exchange": exchange,
                    "sector": sector,
                    "industry": industry,
                    "currency": currency,
                    "cik": cik,
                },
            )
        await session.commit()
    print(f"Seeded {len(COMPANIES)} companies (skipped duplicates).")


if __name__ == "__main__":
    asyncio.run(seed())
