import { formatCurrency, formatPercent, formatPeriod } from "@/lib/format";
import type { FinancialSnapshot } from "@/types";
import { Card } from "./ui/Card";

interface Props {
  snapshot: FinancialSnapshot | null;
}

export function FinancialSnapshotView({ snapshot }: Props) {
  if (!snapshot) {
    return (
      <Card>
        <p className="text-gray-500">No financial data available yet.</p>
      </Card>
    );
  }

  const period = formatPeriod(snapshot.fiscal_year, snapshot.fiscal_quarter);

  return (
    <Card>
      <h3 className="mb-4 text-lg font-semibold">{period} Financials</h3>

      <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
        <Metric label="Revenue" value={formatCurrency(snapshot.revenue, snapshot.currency)} />
        <Metric label="Net Income" value={formatCurrency(snapshot.net_income, snapshot.currency)} />
        <Metric label="EBITDA" value={formatCurrency(snapshot.ebitda, snapshot.currency)} />
        <Metric label="EPS (Diluted)" value={snapshot.eps_diluted?.toFixed(2) ?? "—"} />

        <Metric label="Gross Margin" value={formatPercent(snapshot.gross_margin)} />
        <Metric label="Operating Margin" value={formatPercent(snapshot.operating_margin)} />
        <Metric label="Net Margin" value={formatPercent(snapshot.net_margin)} />
        <Metric label="ROE" value={formatPercent(snapshot.roe)} />

        <Metric label="Free Cash Flow" value={formatCurrency(snapshot.free_cash_flow, snapshot.currency)} />
        <Metric label="Total Debt" value={formatCurrency(snapshot.total_debt, snapshot.currency)} />
        <Metric label="Cash" value={formatCurrency(snapshot.cash_and_equivalents, snapshot.currency)} />
        <Metric label="D/E Ratio" value={snapshot.debt_to_equity?.toFixed(2) ?? "—"} />
      </div>

      {snapshot.segments.length > 0 && (
        <div className="mt-6">
          <h4 className="mb-2 font-medium">Business Segments</h4>
          <div className="space-y-2">
            {snapshot.segments.map((seg) => (
              <div key={seg.id} className="flex items-center justify-between rounded bg-gray-50 px-3 py-2 text-sm">
                <span>{seg.name}</span>
                <span className="text-gray-600">
                  {formatCurrency(seg.revenue, snapshot.currency)}
                  {seg.revenue_pct !== null && ` (${formatPercent(seg.revenue_pct)})`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}
