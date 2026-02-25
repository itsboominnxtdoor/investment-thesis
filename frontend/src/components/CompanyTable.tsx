import { listCompanies } from "@/lib/api-client";
import type { Company } from "@/types";
import { Badge } from "./ui/Badge";
import { Pagination } from "./Pagination";
import { WatchlistStar } from "./WatchlistStar";

interface Props {
  searchParamsPromise: Promise<{
    search?: string;
    sector?: string;
    exchange?: string;
    page?: string;
  }>;
}

const SECTOR_COLORS: Record<string, string> = {
  Technology: "from-blue-500 to-cyan-500",
  Financials: "from-green-500 to-emerald-500",
  Healthcare: "from-red-500 to-rose-500",
  "Consumer Cyclical": "from-orange-500 to-amber-500",
  "Consumer Defensive": "from-yellow-500 to-orange-500",
  Energy: "from-lime-500 to-green-500",
  Industrials: "from-slate-500 to-gray-500",
  "Communication Services": "from-purple-500 to-pink-500",
  "Real Estate": "from-indigo-500 to-blue-500",
  Utilities: "from-cyan-500 to-blue-500",
  "Basic Materials": "from-amber-600 to-yellow-600",
};

function CompanyRow({ company, rank }: { company: Company; rank: number }) {
  const dotColor = SECTOR_COLORS[company.sector] ?? "from-violet-500 to-purple-600";

  return (
    <div className="group relative flex items-center gap-3 border-b border-[var(--color-border-light)] px-4 py-3 transition-colors hover:bg-[var(--color-surface-elevated)]">
      {/* Rank */}
      <span className="w-7 shrink-0 text-right text-xs tabular-nums text-[var(--color-text-tertiary)]">{rank}</span>

      {/* Watchlist star */}
      <WatchlistStar companyId={company.id} ticker={company.ticker} />

      {/* Sector dot + Ticker */}
      <a href={`/companies/${company.ticker}`} className="absolute inset-0" aria-label={company.name} />
      <div className="w-24 shrink-0">
        <div className="flex items-center gap-2">
          <div className={`h-2 w-2 shrink-0 rounded-full bg-gradient-to-br ${dotColor}`} />
          <span className="text-sm font-bold text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-primary)]">
            {company.ticker}
          </span>
        </div>
        <span className="mt-0.5 block pl-4 text-[11px] text-[var(--color-text-tertiary)]">
          {company.exchange}
        </span>
      </div>

      {/* Company name */}
      <div className="min-w-0 flex-1">
        <span className="block truncate text-sm text-[var(--color-text-secondary)]">{company.name}</span>
      </div>

      {/* Sector */}
      <div className="hidden w-36 shrink-0 md:block">
        <span className="block truncate text-xs text-[var(--color-text-tertiary)]">{company.sector}</span>
      </div>

      {/* Industry */}
      <div className="hidden w-44 shrink-0 xl:block">
        <span className="block truncate text-xs text-[var(--color-text-tertiary)]">{company.industry}</span>
      </div>

      {/* Currency */}
      <div className="shrink-0">
        <Badge variant="gray" size="sm">{company.currency}</Badge>
      </div>

      {/* Arrow */}
      <svg
        className="h-4 w-4 shrink-0 text-[var(--color-text-tertiary)] opacity-0 transition-opacity group-hover:opacity-100"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </div>
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
      <div className="flex flex-col items-center justify-center rounded-2xl border border-amber-500/20 bg-amber-500/5 p-12 text-center">
        <svg className="mb-4 h-12 w-12 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-amber-400">{error}</p>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] p-12 text-center">
        <svg className="mb-4 h-12 w-12 text-[var(--color-text-tertiary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <p className="text-[var(--color-text-secondary)]">No companies found.</p>
      </div>
    );
  }

  const totalPages = Math.ceil(total / perPage);
  const startRank = (page - 1) * perPage;

  return (
    <div className="space-y-4">
      {/* Results header */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-[var(--color-text-tertiary)]">
          Showing{" "}
          <span className="font-semibold text-[var(--color-text-secondary)]">
            {startRank + 1}–{Math.min(startRank + companies.length, total)}
          </span>{" "}
          of{" "}
          <span className="font-semibold text-[var(--color-text-secondary)]">{total}</span> companies
        </p>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-2xl border border-[var(--color-border-light)]">
        {/* Header */}
        <div className="flex items-center gap-3 border-b border-[var(--color-border)] bg-[var(--color-surface-elevated)] px-4 py-2.5">
          <span className="w-7 shrink-0 text-right text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">#</span>
          <span className="w-4 shrink-0" /> {/* star placeholder */}
          <span className="w-24 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">Symbol</span>
          <span className="flex-1 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">Company</span>
          <span className="hidden w-36 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)] md:block">Sector</span>
          <span className="hidden w-44 shrink-0 text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)] xl:block">Industry</span>
          <span className="text-[10px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">CCY</span>
          <span className="w-4 shrink-0" /> {/* arrow placeholder */}
        </div>

        {/* Rows */}
        <div className="bg-[var(--color-surface)]">
          {companies.map((company, i) => (
            <CompanyRow key={company.id} company={company} rank={startRank + i + 1} />
          ))}
        </div>
      </div>

      <Pagination page={page} totalPages={totalPages} total={total} />
    </div>
  );
}
