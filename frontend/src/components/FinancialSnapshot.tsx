"use client";

import { useState } from "react";
import { formatCurrency, formatPercent, formatPeriod } from "@/lib/format";
import type { FinancialSnapshot } from "@/types";
import { Card } from "./ui/Card";

type SubTab = "income" | "balance" | "cashflow";

interface Props {
  snapshot: FinancialSnapshot | null;
}

function fmtShares(val: number | null | undefined): string {
  if (val == null) return "—";
  const n = typeof val === "string" ? parseFloat(val as unknown as string) : val;
  if (isNaN(n)) return "—";
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000) return `${(abs / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `${(abs / 1_000_000).toFixed(1)}M`;
  return n.toLocaleString("en-US");
}

function fmtEps(val: number | null | undefined): string {
  if (val == null) return "—";
  const n = typeof val === "string" ? parseFloat(val as unknown as string) : val;
  if (isNaN(n)) return "—";
  return `$${n.toFixed(2)}`;
}

function fmtRatio(val: number | null | undefined): string {
  if (val == null) return "—";
  const n = typeof val === "string" ? parseFloat(val as unknown as string) : val;
  if (isNaN(n)) return "—";
  return n.toFixed(2) + "x";
}

interface StatRowProps {
  label: string;
  value: string;
  muted?: boolean;
  even?: boolean;
}

function StatRow({ label, value, muted, even }: StatRowProps) {
  return (
    <div className={`flex items-center justify-between px-4 py-2.5 ${even ? "bg-gray-50/70 dark:bg-gray-800/30" : ""}`}>
      <span className={`text-sm ${muted ? "pl-4 text-gray-400 dark:text-gray-500" : "text-gray-700 dark:text-gray-300"}`}>
        {label}
      </span>
      <span className="text-sm font-semibold tabular-nums text-gray-900 dark:text-white">{value}</span>
    </div>
  );
}

export function FinancialSnapshotView({ snapshot }: Props) {
  const [tab, setTab] = useState<SubTab>("income");

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
  const cur = snapshot.currency;

  const tabs: { id: SubTab; label: string }[] = [
    { id: "income", label: "Income Statement" },
    { id: "balance", label: "Balance Sheet" },
    { id: "cashflow", label: "Cash Flow" },
  ];

  const incomeRows: StatRowProps[] = [
    { label: "Revenue", value: formatCurrency(snapshot.revenue, cur) },
    { label: "Cost of Revenue", value: formatCurrency(snapshot.cost_of_revenue, cur) },
    { label: "Gross Profit", value: formatCurrency(snapshot.gross_profit, cur) },
    { label: "Gross Margin", value: formatPercent(snapshot.gross_margin), muted: true },
    { label: "Operating Income", value: formatCurrency(snapshot.operating_income, cur) },
    { label: "Operating Margin", value: formatPercent(snapshot.operating_margin), muted: true },
    { label: "EBITDA", value: formatCurrency(snapshot.ebitda, cur) },
    { label: "Net Income", value: formatCurrency(snapshot.net_income, cur) },
    { label: "Net Margin", value: formatPercent(snapshot.net_margin), muted: true },
    { label: "EPS (Diluted)", value: fmtEps(snapshot.eps_diluted) },
    { label: "Shares Outstanding", value: fmtShares(snapshot.shares_outstanding) },
  ];

  const balanceRows: StatRowProps[] = [
    { label: "Total Assets", value: formatCurrency(snapshot.total_assets, cur) },
    { label: "Total Liabilities", value: formatCurrency(snapshot.total_liabilities, cur) },
    { label: "Total Equity", value: formatCurrency(snapshot.total_equity, cur) },
    { label: "Cash & Equivalents", value: formatCurrency(snapshot.cash_and_equivalents, cur) },
    { label: "Total Debt", value: formatCurrency(snapshot.total_debt, cur) },
    { label: "Debt / Equity", value: fmtRatio(snapshot.debt_to_equity), muted: true },
    { label: "ROE", value: formatPercent(snapshot.roe), muted: true },
  ];

  const cashflowRows: StatRowProps[] = [
    { label: "Operating Cash Flow", value: formatCurrency(snapshot.operating_cash_flow, cur) },
    { label: "Capital Expenditures", value: formatCurrency(snapshot.capital_expenditures, cur) },
    { label: "Free Cash Flow", value: formatCurrency(snapshot.free_cash_flow, cur) },
  ];

  const rows = tab === "income" ? incomeRows : tab === "balance" ? balanceRows : cashflowRows;

  return (
    <Card>
      {/* Header */}
      <div className="mb-5 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600">
          <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{period} Financials</h3>
          <p className="text-xs text-gray-500">Fiscal year {snapshot.fiscal_year}</p>
        </div>
      </div>

      {/* Pill switcher */}
      <div className="mb-4 flex gap-1.5 rounded-xl bg-gray-100 p-1 dark:bg-gray-800">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`flex-1 rounded-lg px-3 py-2 text-xs font-medium transition-all ${
              tab === t.id
                ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
                : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Statement rows */}
      <div className="overflow-hidden rounded-xl border border-gray-100 dark:border-gray-800">
        {rows.map((row, i) => (
          <StatRow key={row.label} {...row} even={i % 2 === 1} />
        ))}
      </div>

      {/* Business Segments */}
      {snapshot.segments.length > 0 && (
        <div className="mt-6">
          <h4 className="mb-3 text-sm font-semibold text-gray-700 dark:text-gray-300">Business Segments</h4>
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
                    <span className="ml-2 text-gray-400">({formatPercent(seg.revenue_pct)})</span>
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
