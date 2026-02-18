import { Suspense } from "react";
import { CompanyTable } from "@/components/CompanyTable";
import { DashboardStats } from "@/components/DashboardStats";
import { ExchangeFilter } from "@/components/ExchangeFilter";
import { SearchBar } from "@/components/SearchBar";
import { SectorFilter } from "@/components/SectorFilter";

export default function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; sector?: string; exchange?: string; page?: string }>;
}) {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 px-8 py-12 sm:px-12">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-white blur-3xl"></div>
          <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-white blur-3xl"></div>
        </div>
        
        <div className="relative z-10">
          <h1 className="animate-fade-in-up text-4xl font-bold tracking-tight text-white sm:text-5xl">
            Market Intelligence, <br />
            <span className="text-white/80">Powered by AI</span>
          </h1>
          <p className="mt-4 max-w-xl text-lg text-white/70">
            Institutional-grade research on S&amp;P 500 and TSX companies. 
            Real-time thesis generation, drift tracking, and quarterly updates.
          </p>
          
          {/* Quick stats */}
          <div className="mt-8 flex flex-wrap gap-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-white">463+</div>
              <div className="mt-1 text-sm text-white/60">Companies Tracked</div>
            </div>
            <div className="h-12 w-px bg-white/20"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">24/7</div>
              <div className="mt-1 text-sm text-white/60">AI Analysis</div>
            </div>
            <div className="h-12 w-px bg-white/20"></div>
            <div className="text-center">
              <div className="text-3xl font-bold text-white">100%</div>
              <div className="mt-1 text-sm text-white/60">Data Coverage</div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <Suspense>
        <DashboardStats />
      </Suspense>

      {/* Filters */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-3">
          <SearchBar />
          <SectorFilter />
          <ExchangeFilter />
        </div>
        <div className="text-sm text-[var(--color-text-secondary)]">
          Showing companies across NYSE, NASDAQ, TSX and more
        </div>
      </div>

      {/* Company Table */}
      <CompanyTable searchParamsPromise={searchParams} />
    </div>
  );
}
