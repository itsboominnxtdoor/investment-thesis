import type {
  BusinessProfile,
  Company,
  Document,
  FinancialSnapshot,
  PaginatedResponse,
  QuarterlyUpdate,
  ThesisVersion,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

// Dashboard Stats
export interface DashboardStats {
  total_companies: number;
  companies_with_financials: number;
  companies_with_thesis: number;
  sectors: Record<string, number>;
  exchanges: Record<string, number>;
}

export function getDashboardStats() {
  return fetchJSON<DashboardStats>("/api/v1/companies/stats");
}

// Companies
export function listCompanies(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  sector?: string;
  exchange?: string;
}) {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.per_page) sp.set("per_page", String(params.per_page));
  if (params?.search) sp.set("search", params.search);
  if (params?.sector) sp.set("sector", params.sector);
  if (params?.exchange) sp.set("exchange", params.exchange);
  const qs = sp.toString();
  return fetchJSON<PaginatedResponse<Company>>(`/api/v1/companies${qs ? `?${qs}` : ""}`);
}

export function getCompany(id: string) {
  return fetchJSON<Company>(`/api/v1/companies/${id}`);
}

export function getCompanyByTicker(ticker: string) {
  return fetchJSON<Company>(`/api/v1/companies/ticker/${ticker}`);
}

// Financials
export function listFinancials(companyId: string, params?: { page?: number; per_page?: number }) {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.per_page) sp.set("per_page", String(params.per_page));
  const qs = sp.toString();
  return fetchJSON<PaginatedResponse<FinancialSnapshot>>(
    `/api/v1/companies/${companyId}/financials${qs ? `?${qs}` : ""}`
  );
}

export function getLatestFinancials(companyId: string) {
  return fetchJSON<FinancialSnapshot>(`/api/v1/companies/${companyId}/financials/latest`);
}

export function ingestFinancials(companyId: string) {
  return fetchJSON<FinancialSnapshot>(`/api/v1/companies/${companyId}/financials/ingest`, {
    method: "POST",
  });
}

// Thesis
export function listThesisVersions(companyId: string, params?: { page?: number; per_page?: number }) {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.per_page) sp.set("per_page", String(params.per_page));
  const qs = sp.toString();
  return fetchJSON<PaginatedResponse<ThesisVersion>>(
    `/api/v1/companies/${companyId}/thesis${qs ? `?${qs}` : ""}`
  );
}

export function getLatestThesis(companyId: string) {
  return fetchJSON<ThesisVersion>(`/api/v1/companies/${companyId}/thesis/latest`);
}

export function generateThesis(companyId: string) {
  return fetchJSON<ThesisVersion>(`/api/v1/companies/${companyId}/thesis/generate`, {
    method: "POST",
  });
}

// Business Profiles
export function getBusinessProfile(companyId: string) {
  return fetchJSON<BusinessProfile>(`/api/v1/companies/${companyId}/business-profile`);
}

export function generateBusinessProfile(companyId: string) {
  return fetchJSON<BusinessProfile>(`/api/v1/companies/${companyId}/business-profile/generate`, {
    method: "POST",
  });
}

// Quarterly Updates
export function listQuarterlyUpdates(companyId: string, params?: { page?: number; per_page?: number }) {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.per_page) sp.set("per_page", String(params.per_page));
  const qs = sp.toString();
  return fetchJSON<PaginatedResponse<QuarterlyUpdate>>(
    `/api/v1/companies/${companyId}/quarterly-updates${qs ? `?${qs}` : ""}`
  );
}

export function generateQuarterlyUpdate(companyId: string) {
  return fetchJSON<QuarterlyUpdate>(`/api/v1/companies/${companyId}/quarterly-updates/generate`, {
    method: "POST",
  });
}

// Documents
export function listDocuments(companyId: string, params?: { page?: number; doc_type?: string }) {
  const sp = new URLSearchParams();
  if (params?.page) sp.set("page", String(params.page));
  if (params?.doc_type) sp.set("doc_type", params.doc_type);
  const qs = sp.toString();
  return fetchJSON<PaginatedResponse<Document>>(
    `/api/v1/companies/${companyId}/documents${qs ? `?${qs}` : ""}`
  );
}
