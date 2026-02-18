import { listCompanies } from "@/lib/api-client";
import type { Company } from "@/types";
import { Badge } from "./ui/Badge";
import { Pagination } from "./Pagination";

interface Props {
  searchParamsPromise: Promise<{
    search?: string;
    sector?: string;
    exchange?: string;
    page?: string;
  }>;
}

function CompanyLogo({ ticker, name }: { ticker: string; name: string }) {
  const colors = [
    "from-violet-500 to-purple-600",
    "from-blue-500 to-cyan-600",
    "from-green-500 to-emerald-600",
    "from-orange-500 to-amber-600",
    "from-red-500 to-rose-600",
    "from-pink-500 to-fuchsia-600",
    "from-indigo-500 to-blue-600",
    "from-teal-500 to-green-600",
  ];
  
  const colorIndex = ticker.charCodeAt(0) % colors.length;
  const initial = name.charAt(0).toUpperCase();
  
  return (
    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${colors[colorIndex]} shadow-sm`}>
      <span className="text-lg font-bold text-white">{initial}</span>
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
        <CompanyLogo ticker={company.ticker} name={company.name} />
        
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
