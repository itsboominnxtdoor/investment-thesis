# Thesis Engine

AI-powered institutional stock research platform covering S&P 500 and TSX large caps.

## Product Overview

Thesis Engine synthesizes business models from SEC/SEDAR filings, generates structured Bull/Base/Bear investment cases, updates quarterly after earnings, and tracks thesis drift over time. It does **NOT** provide buy/sell recommendations.

### Key Features

- **Business Model Analysis**: AI-synthesized revenue drivers, cost structure, competitive positioning
- **Three-Scenario Thesis**: Bull, Base, and Bear cases with key drivers and risks
- **Thesis Integrity Score**: 0-10 rating of how well-supported the thesis is by data
- **Quarterly Updates**: Automatic drift tracking and thesis evolution
- **Coverage**: S&P 500 (US) and TSX large caps (Canada)

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 22+
- Groq API key (for LLM)
- Financial Modeling Prep API key (for financial data)

### 1. Start Infrastructure

```bash
docker compose up -d
```

This starts:
- PostgreSQL 16 (database)
- Redis 7 (Celery broker)

### 2. Configure Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `GROQ_API_KEY` - Get from https://console.groq.com
- `FINANCIAL_DATA_API_KEY` - Get from https://financialmodelingprep.com
- `EDGAR_USER_AGENT` - Format: "YourAppName your@email.com"

### 3. Install Backend Dependencies

```bash
pip install -e ".[dev]"
alembic upgrade head
```

### 4. Seed Companies

```bash
python scripts/seed_companies.py
```

This populates ~150 S&P 500 and TSX companies.

### 5. Start Backend

```bash
uvicorn app.main:app --reload
```

API available at http://localhost:8000  
Swagger docs at http://localhost:8000/docs

### 6. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at http://localhost:3000

---

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Next.js   │────▶│  FastAPI    │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend   │     │  Database   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐     ┌─────────────┐
                    │   Celery    │────▶│    Redis    │
                    │  Task Queue │     │   Broker    │
                    └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐     ┌─────────────┐
                    │  Groq LLM   │     │    FMP API  │
                    │  (Llama 3)  │     │ (Financials)│
                    └─────────────┘     └─────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15 + React 19 + Tailwind CSS 4 |
| Backend | FastAPI + SQLAlchemy 2.0 + AsyncPG |
| Database | PostgreSQL 16 |
| Task Queue | Celery 5 + Redis 7 |
| LLM | Groq (Llama 3 70B) |
| Financial Data | Financial Modeling Prep (FMP) |
| Filings | SEC EDGAR (US), SEDAR+ (Canada) |
| Storage | S3-compatible (optional) |

---

## API Endpoints

### Companies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies` | List all companies |
| GET | `/api/v1/companies/{id}` | Get company by ID |
| GET | `/api/v1/companies/ticker/{ticker}` | Get company by ticker |

### Financials

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/financials` | List financial snapshots |
| GET | `/api/v1/companies/{id}/financials/latest` | Get latest snapshot |
| POST | `/api/v1/companies/{id}/financials/ingest` | Ingest from FMP API |

### Business Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/business-profile` | Get latest profile |
| POST | `/api/v1/companies/{id}/business-profile/generate` | Generate via LLM |

### Thesis

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/thesis` | List thesis versions |
| GET | `/api/v1/companies/{id}/thesis/latest` | Get latest thesis |
| POST | `/api/v1/companies/{id}/thesis/generate` | Generate via LLM |

### Quarterly Updates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/quarterly-updates` | List updates |
| POST | `/api/v1/companies/{id}/quarterly-updates/generate` | Generate via LLM |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/companies/{id}/documents` | List filed documents |
| POST | `/api/v1/companies/{id}/documents/ingest` | Ingest from EDGAR/SEDAR |

---

## Database Schema

### Core Tables

- **companies** - Company metadata (ticker, exchange, sector, CIK, SEDAR ID)
- **financial_snapshots** - Immutable quarterly financial data
- **segments** - Revenue breakdown by business segment
- **business_profiles** - AI-generated business model analysis (versioned)
- **thesis_versions** - AI-generated investment thesis (versioned, immutable)
- **quarterly_updates** - Executive summaries of quarterly changes
- **documents** - Filed documents metadata (10-K, 10-Q, AIF, MD&A)

### Key Design Principles

1. **Immutability**: Financial snapshots and thesis versions are never modified
2. **Versioning**: Each quarterly refresh creates new records
3. **Native Currency**: USD for US companies, CAD for Canadian (no conversion)
4. **Audit Trail**: Prior version links enable drift tracking

---

## Celery Tasks

### Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| `check_for_new_filings` | Hourly | Scan EDGAR/SEDAR for new filings |
| `process_company_filing` | On-demand | 7-step ingestion pipeline |

### Ingestion Pipeline Steps

1. Download filing from EDGAR/SEDAR+
2. Upload raw document to S3
3. Pull structured financial data from FMP
4. Create financial snapshot record
5. Generate/update business profile via LLM
6. Generate new thesis version via LLM
7. Create quarterly update record

---

## Usage Guide

### Adding a New Company

1. Company must be in the database (auto-seeded for S&P 500/TSX)
2. Click "Ingest Financials" to pull data from FMP
3. Click "Generate Profile" to create business model analysis
4. Click "Generate Thesis" to create investment thesis

### Quarterly Refresh Workflow

When a company files a new 10-Q or 10-K:

1. Celery detects new filing (hourly check)
2. Pipeline automatically processes the filing
3. New financial snapshot is created
4. Thesis is regenerated with drift tracking
5. Quarterly update summarizes key changes

### Manual Generation

All generation endpoints can be triggered manually via the UI or API.

---

## Development

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Style

```bash
# Backend
ruff check .
ruff format .

# Frontend
npm run lint
npm run format
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Production Deployment

### Railway (Backend)

1. Connect GitHub repository
2. Set environment variables
3. Deploy from `backend/Dockerfile`
4. Attach PostgreSQL database

### Vercel (Frontend)

1. Connect GitHub repository
2. Set `API_BACKEND_URL` to Railway URL
3. Deploy

### Environment Variables

See `backend/.env.example` and `frontend/.env.local.example` for all required variables.

---

## Limitations (MVP)

- SEDAR+ integration requires paid API for production use
- S3 storage is optional (documents can be referenced by URL only)
- No real-time alerts or notifications
- No community features or collaboration
- No price targets or trading signals

---

## License

MIT

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
