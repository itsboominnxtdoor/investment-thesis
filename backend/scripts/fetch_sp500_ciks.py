"""Fetch CIK numbers for S&P 500 companies from SEC's company_tickers.json.

Usage:
    python -m scripts.fetch_sp500_ciks

Outputs a Python dict mapping ticker -> CIK (zero-padded to 10 digits).
Useful for updating seed_companies.py with accurate CIK values.
"""

import httpx

SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
USER_AGENT = "ThesisEngine admin@example.com"


def fetch_cik_map() -> dict[str, str]:
    """Pull SEC company_tickers.json and return {ticker: padded_cik}."""
    resp = httpx.get(
        SEC_TICKERS_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
    )
    resp.raise_for_status()
    data = resp.json()

    cik_map: dict[str, str] = {}
    for entry in data.values():
        ticker = entry["ticker"]
        cik = str(entry["cik_str"]).zfill(10)
        cik_map[ticker] = cik
    return cik_map


def main():
    cik_map = fetch_cik_map()
    print(f"Fetched {len(cik_map)} tickers from SEC")

    # Print a sample for known S&P 500 names
    sample_tickers = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM",
        "V", "UNH", "XOM", "JNJ", "WMT", "PG", "MA", "HD", "CVX",
    ]
    print("\nSample CIKs:")
    for t in sample_tickers:
        cik = cik_map.get(t, "NOT FOUND")
        print(f"  {t:8s} -> {cik}")

    print(f"\nTotal unique tickers: {len(cik_map)}")
    return cik_map


if __name__ == "__main__":
    main()
