# Backend Scripts

Utility scripts for the Thesis Engine backend.

## seed_companies.py

Populates the companies table with S&P 500 and TSX large-cap companies.

```bash
python scripts/seed_companies.py
```

This script:
- Inserts ~150 companies (US + Canada)
- Skips duplicates (safe to run multiple times)
- Includes CIK numbers for US companies (for EDGAR)
- TSX companies have `sedar_id` set to NULL (requires manual lookup or paid API)

### Companies Included

**US (S&P 500 sample)**
- Technology: AAPL, MSFT, GOOGL, AMZN, NVDA, META, etc.
- Financials: JPM, V, MA, BAC, GS, etc.
- Healthcare: UNH, JNJ, LLY, PFE, etc.
- Consumer: WMT, PG, KO, PEP, COST, etc.
- And more sectors...

**Canada (TSX)**
- Banks: RY, TD, BNS, BMO, CM, NA
- Energy: ENB, TRP, CNQ, SU, IMO, CVE
- Industrials: CNR, CP, AC
- Technology: SHOP, CSU, CGI
- And more...

## Adding Custom Companies

Edit `scripts/seed_companies.py` and add entries to the `COMPANIES` list:

```python
("TICKER", "Company Name", "EXCHANGE", "Sector", "Industry", "CURRENCY", "CIK")
```

- CIK is required for US companies (SEC EDGAR)
- Set CIK to `None` for Canadian companies
