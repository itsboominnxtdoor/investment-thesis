# Thesis Engine

AI-powered institutional stock research platform covering S&P 500 and TSX large caps.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 22+

### Infrastructure
```bash
docker compose up -d
```
This starts PostgreSQL 16 and Redis 7.

### Backend
```bash
cd backend
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```
API available at http://localhost:8000 — Swagger docs at http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App available at http://localhost:3000

## Architecture

- **Backend**: FastAPI + SQLAlchemy 2.0 + Celery + Redis
- **Frontend**: Next.js 15 + React 19 + Tailwind CSS 4
- **Database**: PostgreSQL 16
- **Task Queue**: Celery with Redis broker
- **AI**: Anthropic Claude for thesis generation

## Key Design Decisions

- Financial numbers stored as `Numeric` (never Float)
- Financial snapshots and thesis versions are **immutable** (append-only)
- Currency stays native (USD/CAD) — no conversion
- LLM prompts explicitly prohibit buy/sell/hold recommendations
- Each quarterly refresh creates a new snapshot + thesis version + quarterly update
