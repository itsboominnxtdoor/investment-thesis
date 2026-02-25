// Company — maps to CompanyRead (backend/app/schemas/company.py)
export interface Company {
  id: string;
  ticker: string;
  name: string;
  exchange: string;
  sector: string;
  industry: string;
  currency: string;
  cik: string | null;
  sedar_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Segment — maps to SegmentRead (backend/app/schemas/financial_snapshot.py)
export interface Segment {
  id: string;
  name: string;
  revenue: number | null;
  operating_income: number | null;
  revenue_pct: number | null;
}

// FinancialSnapshot — maps to FinancialSnapshotRead
export interface FinancialSnapshot {
  id: string;
  company_id: string;
  fiscal_year: number;
  fiscal_quarter: number;
  currency: string;
  revenue: number | null;
  cost_of_revenue: number | null;
  gross_profit: number | null;
  operating_income: number | null;
  net_income: number | null;
  ebitda: number | null;
  eps_diluted: number | null;
  shares_outstanding: number | null;
  total_assets: number | null;
  total_liabilities: number | null;
  total_equity: number | null;
  cash_and_equivalents: number | null;
  total_debt: number | null;
  operating_cash_flow: number | null;
  capital_expenditures: number | null;
  free_cash_flow: number | null;
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  roe: number | null;
  debt_to_equity: number | null;
  segments: Segment[];
  created_at: string;
}

// ThesisVersion — maps to ThesisVersionRead (backend/app/schemas/thesis_version.py)
export interface ThesisVersion {
  id: string;
  company_id: string;
  snapshot_id: string;
  version: number;
  bull_case: string;
  bull_target: number | null;
  base_case: string;
  base_target: number | null;
  bear_case: string;
  bear_target: number | null;
  key_drivers: string;       // JSON-encoded string[]
  key_risks: string;         // JSON-encoded string[]
  catalysts: string;         // JSON-encoded string[]
  thesis_integrity_score: number | null;
  integrity_rationale: string | null;
  prior_version_id: string | null;
  drift_summary: string | null;
  conviction_direction: string | null;
  llm_model_used: string;
  created_at: string;
}

// BusinessProfile — maps to BusinessProfileRead (backend/app/schemas/business_profile.py)
export interface BusinessProfile {
  id: string;
  company_id: string;
  version: number;
  description: string;
  business_model: string;
  competitive_position: string;
  key_products: string;      // JSON-encoded string[]
  geographic_mix: string;    // JSON-encoded Record<string, number>
  moat_assessment: string;
  moat_sources: string;      // JSON-encoded string[]
  created_at: string;
}

// QuarterlyUpdate — maps to QuarterlyUpdateRead (backend/app/schemas/quarterly_update.py)
export interface QuarterlyUpdate {
  id: string;
  company_id: string;
  snapshot_id: string;
  thesis_version_id: string;
  fiscal_year: number;
  fiscal_quarter: number;
  filing_type: string;
  executive_summary: string;
  key_changes: string;       // JSON-encoded string[]
  guidance_update: string | null;
  management_commentary: string | null;
  created_at: string;
}

// Document — maps to DocumentRead (backend/app/schemas/document.py)
export interface Document {
  id: string;
  company_id: string;
  doc_type: string;
  source: string;
  source_url: string;
  s3_key: string | null;
  file_size_bytes: number | null;
  filing_date: string | null;
  created_at: string;
}

// Generic paginated response used by all list endpoints
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// StockQuote — maps to StockQuoteRead (backend/app/schemas/financial_snapshot.py)
export interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  change_pct: number;
  prev_close: number;
  latest_trading_day: string;
}
