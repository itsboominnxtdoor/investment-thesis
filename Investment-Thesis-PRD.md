# Thesis Engine – Product Requirements Document (MVP)

0. Engineering Role Definitions
🧠 Claude — Senior Developer (Architecture & AI Systems Lead)

Owns:

System architecture

Database schema design

Backend structure

LLM orchestration

Filing ingestion logic

Prompt design

Data integrity rules

Code reviews

Final merges to main branch

Claude makes architectural decisions.
Claude writes complex backend logic.
Claude defines contracts that Qwen must follow.

⚙️ Qwen — Junior Developer (Implementation & UI Execution)

Owns:

Frontend implementation

API route wiring

CRUD endpoints

UI components

Styling

Basic data fetching logic

Writing tests

Implementing Claude-defined interfaces

Qwen does NOT:

Redesign schema

Modify architecture

Change LLM prompt structure

Alter ingestion logic without Claude approval

## 1. Product Overview

Thesis Engine is an AI-powered institutional-style stock research platform covering:

- S&P 500 (full)
- TSX large caps (initially top 100–200, expandable)

It:
- Synthesizes business models from filings
- Generates structured Bull / Base / Bear cases
- Updates quarterly after earnings
- Tracks thesis drift over time
- Does NOT provide buy/sell recommendations

Primary goal: eliminate friction of reading 10-Ks, 10-Qs, AIFs, and MD&As while maintaining institutional rigor.

---

## 2. Scope (MVP)

**Coverage**
- S&P 500
- TSX large caps

**Update Frequency**
- Quarterly (triggered by new filing)

**Non-Goals**
- Real-time alerts
- News sentiment scraping
- Community features
- Price targets
- Trading signals

---

## 3. Core Company Page Structure

### 1. Business Model Overview (Annual Refresh)
- Revenue drivers
- Segment breakdown
- Cost structure
- Capital intensity
- Competitive positioning
- Strategic roadmap

### 2. Financial Snapshot (Structured Data Only)
- Revenue (5Y)
- Segment revenue
- Gross margin
- Operating margin
- FCF
- Net debt
- Share count
- EPS
- Guidance (if available)

### 3. Bull / Base / Bear Cases
- Growth assumptions
- Margin trajectory
- Capital allocation logic
- Thesis-breaking conditions

### 4. Thesis Integrity Score (0–10)

### 5. Quarterly Update Log
- What changed
- Segment acceleration/deceleration
- Margin movement
- Guidance change
- Impact on thesis
- Archived versions

---

## 4. Filing Sources

### United States
- 10-K
- 10-Q
- Investor presentations
- Earnings releases

### Canada
- AIF
- Annual + Quarterly MD&A
- Financial statements
- Investor presentations
- Earnings releases

System must support SEC (EDGAR) and SEDAR+ ingestion.

---

## 5. AI Behavior Requirements

- Interprets structured inputs only
- Never invents numbers
- No financial advice language
- Deterministic structured format
- Institutional analytical tone

**LLM Responsibilities**
- Business model synthesis
- Bull/Base/Bear generation
- Quarterly delta interpretation
- Thesis drift analysis

LLM must not calculate or extract numeric tables.

---

## 6. Technical Stack

### Frontend
- Next.js
- TailwindCSS

### Backend
- FastAPI (Python)

### Database
- PostgreSQL (Supabase recommended)

### Storage
- S3-compatible (filings + parsed text)

### LLM
- Claude API (Opus tier)

### Financial Data
- Structured financial data API (US + Canada)

### Background Jobs
- Cron or Celery
- Quarterly ingestion pipeline:
  1. Detect new filing
  2. Pull structured financial data
  3. Extract key text sections
  4. Generate thesis update
  5. Store new thesis version

### Hosting
- Vercel (frontend)
- Railway / Render (backend)

---

## 7. Data Models (Postgres)

### companies
- id (uuid, pk)
- ticker
- exchange (NYSE, NASDAQ, TSX)
- name
- sector
- industry
- currency (USD, CAD)
- market_cap
- is_active
- created_at

---

### financial_snapshots
- id (uuid, pk)
- company_id (fk)
- fiscal_year
- fiscal_quarter (0 = annual)
- period_end_date
- revenue
- gross_profit
- operating_income
- net_income
- free_cash_flow
- gross_margin
- operating_margin
- net_debt
- total_debt
- cash
- shares_outstanding
- eps
- guidance_revenue (nullable)
- guidance_eps (nullable)
- created_at

---

### segments
- id (uuid, pk)
- financial_snapshot_id (fk)
- segment_name
- revenue
- operating_income (nullable)
- created_at

---

### business_profiles (Annual Layer)
- id (uuid, pk)
- company_id (fk)
- fiscal_year
- revenue_drivers (text)
- cost_structure (text)
- capital_intensity (text)
- competitive_positioning (text)
- strategic_roadmap (text)
- created_at

---

### thesis_versions
- id (uuid, pk)
- company_id (fk)
- financial_snapshot_id (fk)
- version_type (ANNUAL, QUARTERLY)
- bull_case (text)
- base_case (text)
- bear_case (text)
- thesis_integrity_score (0–10)
- thesis_drift_summary (text)
- created_at

---

### quarterly_updates
- id (uuid, pk)
- company_id (fk)
- financial_snapshot_id (fk)
- what_changed (text)
- segment_changes (text)
- margin_changes (text)
- guidance_changes (text)
- impact_on_thesis (text)
- created_at

---

### documents
- id (uuid, pk)
- company_id (fk)
- document_type (10K, 10Q, AIF, MD&A, INVESTOR_DECK, PRESS_RELEASE)
- fiscal_year
- fiscal_quarter
- file_url
- parsed_text
- created_at

---

## 8. Architectural Rules

1. Financial numbers are immutable.
2. Thesis versions are immutable (no overwrites).
3. Each quarterly refresh creates:
   - New financial_snapshot
   - New thesis_version
   - New quarterly_update
4. All prior versions remain stored.
5. Currency remains native (USD/CAD) in MVP.

---

## 9. Success Criteria

- Reduces filing reading time materially
- Output quality ≈ junior equity analyst memo
- Zero hallucinated financial data
- Becomes core weekly research workflow
