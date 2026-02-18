import { formatCurrency, formatPercent, formatPeriod } from "@/lib/format";
import { safeJsonParse } from "@/lib/utils";
import type { FinancialSnapshot, QuarterlyUpdate } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

interface Props {
  updates: QuarterlyUpdate[];
  snapshots?: FinancialSnapshot[];
}

function RevenueChange({ current, previous }: { current: FinancialSnapshot | undefined; previous: FinancialSnapshot | undefined }) {
  if (!current?.revenue || !previous?.revenue) return null;
  const pctChange = ((current.revenue - previous.revenue) / Math.abs(previous.revenue)) * 100;
  const isPositive = pctChange >= 0;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
      isPositive ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
    }`}>
      <span>{isPositive ? "↑" : "↓"}</span>
      {Math.abs(pctChange).toFixed(1)}% rev
    </span>
  );
}

function MarginIndicator({ label, current, previous }: { label: string; current: number | null; previous: number | null }) {
  if (current === null || previous === null) return null;
  const diff = (current - previous) * 100;
  if (Math.abs(diff) < 0.1) return null;
  const isPositive = diff >= 0;
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
      isPositive ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
    }`}>
      {isPositive ? "↑" : "↓"} {label} {Math.abs(diff).toFixed(1)}pp
    </span>
  );
}

export function QuarterlyTimeline({ updates, snapshots = [] }: Props) {
  if (updates.length === 0) {
    return (
      <Card>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="mb-4 h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-gray-500">No quarterly updates available yet.</p>
        </div>
      </Card>
    );
  }

  const snapshotMap = new Map(snapshots.map((s) => [s.id, s]));
  const sortedSnapshots = [...snapshots].sort((a, b) => {
    if (a.fiscal_year !== b.fiscal_year) return a.fiscal_year - b.fiscal_year;
    return a.fiscal_quarter - b.fiscal_quarter;
  });

  function getPrevSnapshot(snapshotId: string): FinancialSnapshot | undefined {
    const idx = sortedSnapshots.findIndex((s) => s.id === snapshotId);
    return idx > 0 ? sortedSnapshots[idx - 1] : undefined;
  }

  return (
    <div className="relative space-y-4">
      {/* Timeline line */}
      <div className="absolute left-6 top-4 bottom-4 w-0.5 bg-gradient-to-b from-violet-500 via-purple-500 to-transparent"></div>
      
      {updates.map((update, index) => {
        const keyChanges = safeJsonParse<string[]>(update.key_changes, []);
        const currentSnapshot = snapshotMap.get(update.snapshot_id);
        const prevSnapshot = currentSnapshot ? getPrevSnapshot(currentSnapshot.id) : undefined;

        return (
          <div key={update.id} className="relative pl-14">
            {/* Timeline dot */}
            <div className="absolute left-0 top-5 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-md">
              <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            
            <Card className="transition-all duration-300 hover:shadow-md">
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <h3 className="text-lg font-semibold text-gray-900">
                  {formatPeriod(update.fiscal_year, update.fiscal_quarter)}
                </h3>
                <Badge variant="gray" size="sm">{update.filing_type}</Badge>
                {currentSnapshot && prevSnapshot && (
                  <>
                    <RevenueChange current={currentSnapshot} previous={prevSnapshot} />
                    <MarginIndicator label="GM" current={currentSnapshot.gross_margin} previous={prevSnapshot.gross_margin} />
                    <MarginIndicator label="OM" current={currentSnapshot.operating_margin} previous={prevSnapshot.operating_margin} />
                    <MarginIndicator label="NM" current={currentSnapshot.net_margin} previous={prevSnapshot.net_margin} />
                  </>
                )}
                {currentSnapshot?.revenue && (
                  <span className="text-xs text-gray-500">
                    Rev: {formatCurrency(currentSnapshot.revenue, currentSnapshot.currency)}
                  </span>
                )}
              </div>
              <p className="text-sm leading-relaxed text-gray-700">{update.executive_summary}</p>

              {keyChanges.length > 0 && (
                <div className="mt-4 rounded-xl bg-gradient-to-br from-blue-50 to-cyan-50 p-4 dark:from-blue-900/20 dark:to-cyan-900/20">
                  <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-blue-700 dark:text-blue-400">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                    Key Changes
                  </h4>
                  <ul className="space-y-1.5">
                    {keyChanges.map((change, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-blue-900 dark:text-blue-100">
                        <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"></span>
                        {change}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {update.guidance_update && (
                <div className="mt-3 rounded-xl bg-green-50 p-3 text-sm text-green-800 dark:bg-green-900/20 dark:text-green-200">
                  <strong>Guidance:</strong> {update.guidance_update}
                </div>
              )}

              {update.management_commentary && (
                <div className="mt-3 rounded-xl bg-gray-50 p-3 text-sm text-gray-700 dark:bg-gray-800/50 dark:text-gray-300">
                  <strong>Management Commentary:</strong> {update.management_commentary}
                </div>
              )}
            </Card>
          </div>
        );
      })}
    </div>
  );
}
