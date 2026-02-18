import { formatCurrency, formatPercent, formatPeriod } from "@/lib/format";
import type { FinancialSnapshot } from "@/types";
import { Card } from "./ui/Card";

interface Props {
  snapshot: FinancialSnapshot | null;
}

interface MetricProps {
  label: string;
  value: string;
  icon?: React.ReactNode;
}

function Metric({ label, value, icon }: MetricProps) {
  return (
    <div className="rounded-xl bg-gradient-to-br from-gray-50 to-gray-100 p-4 dark:from-gray-800/50 dark:to-gray-900/50">
      <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-gray-500">
        {icon && <span className="text-gray-400">{icon}</span>}
        {label}
      </div>
      <p className="text-lg font-semibold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
}

export function FinancialSnapshotView({ snapshot }: Props) {
  if (!snapshot) {
    return (
      <Card>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="mb-4 h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <p className="text-gray-500">No financial data available yet.</p>
        </div>
      </Card>
    );
  }

  const period = formatPeriod(snapshot.fiscal_year, snapshot.fiscal_quarter);

  return (
    <Card>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{period} Financials</h3>
            <p className="text-xs text-gray-500">Fiscal year {snapshot.fiscal_year}</p>
          </div>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric 
          label="Revenue" 
          value={formatCurrency(snapshot.revenue, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
              <path fillRule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="Net Income" 
          value={formatCurrency(snapshot.net_income, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12 7a1 1 0 110-2h4a1 1 0 011 1v4a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 11.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L10 10.586 14.293 6.293A1 1 0 0114 6h-2z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="EBITDA" 
          value={formatCurrency(snapshot.ebitda, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
              <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="EPS (Diluted)" 
          value={snapshot.eps_diluted?.toFixed(2) ?? "—"}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          }
        />

        <Metric 
          label="Gross Margin" 
          value={formatPercent(snapshot.gross_margin)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h7a1 1 0 100-2H3zM3 11a1 1 0 100 2h4a1 1 0 100-2H3z" />
            </svg>
          }
        />
        <Metric 
          label="Operating Margin" 
          value={formatPercent(snapshot.operating_margin)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3zM3 7a1 1 0 000 2h7a1 1 0 100-2H3z" />
            </svg>
          }
        />
        <Metric 
          label="Net Margin" 
          value={formatPercent(snapshot.net_margin)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M3 3a1 1 0 000 2h11a1 1 0 100-2H3z" />
            </svg>
          }
        />
        <Metric 
          label="ROE" 
          value={formatPercent(snapshot.roe)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M12 1.586l-4 4v12.828l4-4V1.586zM3.707 3.293A1 1 0 002 4v10a1 1 0 00.293.707L6 18.414V5.586L3.707 3.293zM17.707 5.293L14 1.586v12.828l2.293 2.293A1 1 0 0018 16V6a1 1 0 00-.293-.707z" clipRule="evenodd" />
            </svg>
          }
        />

        <Metric 
          label="Free Cash Flow" 
          value={formatCurrency(snapshot.free_cash_flow, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="Total Debt" 
          value={formatCurrency(snapshot.total_debt, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="Cash" 
          value={formatCurrency(snapshot.cash_and_equivalents, snapshot.currency)}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
              <path fillRule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clipRule="evenodd" />
            </svg>
          }
        />
        <Metric 
          label="D/E Ratio" 
          value={snapshot.debt_to_equity?.toFixed(2) ?? "—"}
          icon={
            <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 5.293a1 1 0 010 1.414L9.414 15l-1.707-1.707a1 1 0 011.414-1.414l.293.293 5.293-5.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          }
        />
      </div>

      {snapshot.segments.length > 0 && (
        <div className="mt-6">
          <h4 className="mb-3 text-sm font-semibold text-gray-700">Business Segments</h4>
          <div className="space-y-2">
            {snapshot.segments.map((seg) => (
              <div 
                key={seg.id} 
                className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3 text-sm dark:bg-gray-800/50"
              >
                <span className="font-medium text-gray-900 dark:text-white">{seg.name}</span>
                <span className="text-gray-600 dark:text-gray-400">
                  {formatCurrency(seg.revenue, snapshot.currency)}
                  {seg.revenue_pct !== null && (
                    <span className="ml-2 text-gray-400">
                      ({formatPercent(seg.revenue_pct)})
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
