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
      {/* Hero Section - drft lightning theme */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-amber-500 via-orange-600 to-purple-700 px-8 py-12 sm:px-12 shadow-2xl shadow-amber-500/30">
        {/* Animated lightning background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-amber-300 blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-20 -left-20 h-64 w-64 rounded-full bg-purple-500 blur-3xl animate-pulse" style={{ animationDelay: '0.5s' }}></div>
          <div className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-orange-400 blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Speed lines decoration */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute left-0 top-1/4 h-0.5 w-32 bg-gradient-to-r from-transparent via-amber-300/30 to-transparent animate-shimmer"></div>
          <div className="absolute right-0 bottom-1/4 h-0.5 w-48 bg-gradient-to-r from-transparent via-amber-300/30 to-transparent animate-shimmer" style={{ animationDelay: '0.3s' }}></div>
        </div>

        <div className="relative z-10">
          {/* Lightning bolt icon */}
          <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-white/20 backdrop-blur-sm">
            <svg className="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
            </svg>
          </div>

          <h1 className="animate-fade-in-up text-5xl font-black tracking-tighter text-white sm:text-6xl">
            drft
          </h1>
          <p className="mt-4 max-w-2xl text-xl text-white/80 font-light">
            Lightning-fast equity research. <br />
            <span className="text-white/60">Institutional-grade thesis generation in seconds, not hours.</span>
          </p>

          {/* Speed stats */}
          <div className="mt-10 flex flex-wrap gap-10">
            <div className="text-center">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-amber-300" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
                <div className="text-4xl font-bold text-white">463+</div>
              </div>
              <div className="mt-2 text-sm text-white/60">Companies Tracked</div>
            </div>
            <div className="h-16 w-px bg-white/20"></div>
            <div className="text-center">
              <div className="flex items-center gap-2">
                <svg className="h-5 w-5 text-amber-300 animate-lightning" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
                <div className="text-4xl font-bold text-white">&lt;30s</div>
              </div>
              <div className="mt-2 text-sm text-white/60">Thesis Generation</div>
            </div>
            <div className="h-16 w-px bg-white/20"></div>
            <div className="text-center">
              <div className="text-4xl font-bold text-white">24/7</div>
              <div className="mt-2 text-sm text-white/60">AI Analysis</div>
            </div>
          </div>

          {/* Tagline */}
          <div className="mt-10 flex items-center gap-3 text-sm text-white/60">
            <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span>
            Speed meets insight. Built for investors who move fast.
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
          S&amp;P 500 • TSX 60 • NYSE • NASDAQ
        </div>
      </div>

      {/* Company Table */}
      <CompanyTable searchParamsPromise={searchParams} />
    </div>
  );
}
