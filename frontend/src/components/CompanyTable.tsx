import { listCompanies } from "@/lib/api-client";
import type { Company } from "@/types";
import { Badge } from "./ui/Badge";
import { Pagination } from "./Pagination";
import type { ReactNode } from "react";

interface Props {
  searchParamsPromise: Promise<{
    search?: string;
    sector?: string;
    exchange?: string;
    page?: string;
  }>;
}

/**
 * Sector icon mapping - each sector gets a unique icon and color
 */
const SECTOR_ICONS: Record<string, { icon: ReactNode; colors: string }> = {
  // Technology
  Technology: {
    colors: "from-blue-500 to-cyan-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
  },
  // Financials
  Financials: {
    colors: "from-green-500 to-emerald-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
  },
  // Healthcare
  Healthcare: {
    colors: "from-red-500 to-rose-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
      </svg>
    ),
  },
  // Consumer Cyclical
  "Consumer Cyclical": {
    colors: "from-orange-500 to-amber-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
      </svg>
    ),
  },
  // Consumer Defensive
  "Consumer Defensive": {
    colors: "from-yellow-500 to-orange-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
  },
  // Energy
  Energy: {
    colors: "from-lime-500 to-green-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
  },
  // Industrials
  Industrials: {
    colors: "from-slate-500 to-gray-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
  },
  // Communication Services
  "Communication Services": {
    colors: "from-purple-500 to-pink-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
  },
  // Real Estate
  "Real Estate": {
    colors: "from-indigo-500 to-blue-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
      </svg>
    ),
  },
  // Utilities
  Utilities: {
    colors: "from-cyan-500 to-blue-500",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
      </svg>
    ),
  },
  // Basic Materials
  "Basic Materials": {
    colors: "from-amber-600 to-yellow-600",
    icon: (
      <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
      </svg>
    ),
  },
};

/**
 * Fallback icon for unknown sectors
 */
function DefaultSectorIcon() {
  return (
    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  );
}

function SectorIcon({ sector }: { sector: string }) {
  const sectorData = SECTOR_ICONS[sector] || { colors: "from-violet-500 to-purple-600", icon: <DefaultSectorIcon /> };
  return (
    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${sectorData.colors} shadow-lg`}>
      {sectorData.icon}
    </div>
  );
}

function CompanyCard({ company }: { company: Company }) {
  return (
    <a
      href={`/companies/${company.ticker}`}
      className="group relative overflow-hidden rounded-2xl bg-[var(--color-surface)] border border-[var(--color-border-light)] p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:border-[var(--color-border)]"
    >
      {/* Gradient accent on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 to-purple-500/5 opacity-0 transition-opacity group-hover:opacity-100"></div>

      <div className="relative flex items-start gap-4">
        {/* Sector Icon */}
        <SectorIcon sector={company.sector} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-[var(--color-text-primary)] group-hover:text-[var(--color-primary)] transition-colors">
              {company.ticker}
            </h3>
            <Badge variant="gray" size="sm">{company.exchange}</Badge>
          </div>
          <p className="mt-0.5 truncate text-sm text-[var(--color-text-secondary)]">
            {company.name}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge variant="purple" size="sm">{company.sector}</Badge>
            <Badge variant="gray" size="sm">{company.currency}</Badge>
          </div>
        </div>

        {/* Arrow indicator */}
        <svg
          className="h-5 w-5 text-[var(--color-text-tertiary)] opacity-0 transition-all duration-300 group-hover:opacity-100 group-hover:translate-x-1"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </a>
  );
}

export async function CompanyTable({ searchParamsPromise }: Props) {
  const searchParams = await searchParamsPromise;
  let companies: Company[] = [];
  let total = 0;
  let error: string | null = null;
  const page = Number(searchParams.page) || 1;
  const perPage = 25;

  try {
    const data = await listCompanies({
      page,
      per_page: perPage,
      search: searchParams.search,
      sector: searchParams.sector,
      exchange: searchParams.exchange,
    });
    companies = data.items;
    total = data.total;
  } catch {
    error = "Unable to load companies. Is the backend running?";
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-amber-200 bg-amber-50 p-12 text-center dark:border-amber-900/50 dark:bg-amber-900/20">
        <svg className="mb-4 h-12 w-12 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-amber-800 dark:text-amber-200">{error}</p>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] p-12 text-center">
        <svg className="mb-4 h-12 w-12 text-[var(--color-text-tertiary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <p className="text-[var(--color-text-secondary)]">No companies found. Add companies via the ingestion pipeline.</p>
      </div>
    );
  }

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      {/* Results header */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--color-text-secondary)]">
          Showing <span className="font-medium text-[var(--color-text-primary)]">{companies.length}</span> of{" "}
          <span className="font-medium text-[var(--color-text-primary)]">{total}</span> companies
        </p>
      </div>
      
      {/* Grid layout */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {companies.map((company) => (
          <CompanyCard key={company.id} company={company} />
        ))}
      </div>
      
      <Pagination page={page} totalPages={totalPages} total={total} />
    </div>
  );
}
