import { getDashboardStats } from "@/lib/api-client";

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

function StatPill({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] px-5 py-4">
      <span className="text-2xl font-black tabular-nums text-[var(--color-text-primary)]">{value}</span>
      <span className="mt-1 text-[11px] font-medium uppercase tracking-widest text-[var(--color-text-tertiary)]">{label}</span>
    </div>
  );
}

export async function DashboardStats() {
  let stats;
  try {
    stats = await getDashboardStats();
  } catch {
    return null;
  }

  const topSectors = Object.entries(stats.sectors)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8);

  const maxCount = topSectors[0]?.[1] ?? 1;

  const coveragePct =
    stats.total_companies > 0
      ? Math.round((stats.companies_with_financials / stats.total_companies) * 100)
      : 0;

  const thesisPct =
    stats.total_companies > 0
      ? Math.round((stats.companies_with_thesis / stats.total_companies) * 100)
      : 0;

  return (
    <div className="grid gap-4 lg:grid-cols-[auto_1fr]">
      {/* Left — key metrics */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-2 lg:gap-3">
        <StatPill label="Companies" value={stats.total_companies.toLocaleString()} />
        <StatPill label="With Financials" value={`${coveragePct}%`} />
        <StatPill label="With Thesis" value={`${thesisPct}%`} />
        <StatPill
          label="Top Exchange"
          value={Object.entries(stats.exchanges).sort(([, a], [, b]) => b - a)[0]?.[0] ?? "—"}
        />
      </div>

      {/* Right — sector breakdown */}
      <div className="rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] p-4">
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">
          Sector Breakdown
        </p>
        <div className="space-y-2">
          {topSectors.map(([sector, count]) => {
            const pct = Math.round((count / maxCount) * 100);
            const gradient = SECTOR_COLORS[sector] ?? "from-violet-500 to-purple-500";
            return (
              <div key={sector} className="flex items-center gap-3">
                <span className="w-36 shrink-0 truncate text-xs text-[var(--color-text-secondary)]">{sector}</span>
                <div className="flex-1 overflow-hidden rounded-full bg-[var(--color-border-light)]">
                  <div
                    className={`h-1.5 rounded-full bg-gradient-to-r ${gradient} transition-all duration-500`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="w-8 shrink-0 text-right text-xs tabular-nums text-[var(--color-text-tertiary)]">
                  {count}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
