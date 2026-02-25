"use client";

import { formatCurrency, formatPeriod } from "@/lib/format";
import type { FinancialSnapshot } from "@/types";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Props {
  snapshots: FinancialSnapshot[];
  currency?: string;
}

function DarkTooltip({
  active,
  payload,
  label,
  formatter,
}: {
  active?: boolean;
  payload?: { name: string; value: number; color: string }[];
  label?: string;
  formatter?: (v: number) => string;
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface-elevated)] p-3 shadow-2xl">
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-[var(--color-text-tertiary)]">{label}</p>
      {payload.map((entry) => (
        <div key={entry.name} className="flex items-center gap-2 py-0.5 text-xs">
          <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: entry.color }} />
          <span className="text-[var(--color-text-tertiary)]">{entry.name}</span>
          <span className="ml-auto pl-4 font-semibold text-[var(--color-text-primary)]">
            {formatter ? formatter(entry.value) : entry.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function LegendDot({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-full" style={{ background: color }} />
      <span className="text-[11px] text-[var(--color-text-tertiary)]">{label}</span>
    </div>
  );
}

export function RevenueChart({ snapshots, currency = "USD" }: Props) {
  if (snapshots.length < 2) return null;

  const sorted = [...snapshots].sort((a, b) => {
    if (a.fiscal_year !== b.fiscal_year) return a.fiscal_year - b.fiscal_year;
    return a.fiscal_quarter - b.fiscal_quarter;
  });

  const sym = currency === "CAD" ? "C$" : "$";

  const revenueData = sorted.map((s) => ({
    period: formatPeriod(s.fiscal_year, s.fiscal_quarter),
    Revenue: s.revenue ? Math.round(Number(s.revenue) / 1_000_000) : null,
    "Net Income": s.net_income ? Math.round(Number(s.net_income) / 1_000_000) : null,
    FCF: s.free_cash_flow ? Math.round(Number(s.free_cash_flow) / 1_000_000) : null,
  }));

  const marginData = sorted.map((s) => ({
    period: formatPeriod(s.fiscal_year, s.fiscal_quarter),
    Gross: s.gross_margin ? Number((Number(s.gross_margin) * 100).toFixed(1)) : null,
    Operating: s.operating_margin ? Number((Number(s.operating_margin) * 100).toFixed(1)) : null,
    Net: s.net_margin ? Number((Number(s.net_margin) * 100).toFixed(1)) : null,
  }));

  const axisStyle = { fontSize: 11, fill: "var(--color-text-tertiary)" };
  const grid = "var(--color-border-light)";

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Revenue / Income / FCF */}
      <div className="rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] p-5">
        <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">
          Revenue & Profitability ({sym}M)
        </h3>
        <ResponsiveContainer width="100%" height={210}>
          <AreaChart data={revenueData} margin={{ top: 8, right: 4, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="gRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gNI" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gFCF" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={grid} vertical={false} />
            <XAxis dataKey="period" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis
              tick={axisStyle}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${sym}${v}M`}
              width={52}
            />
            <Tooltip
              content={(props) => (
                <DarkTooltip
                  {...(props as unknown as Parameters<typeof DarkTooltip>[0])}
                  formatter={(v) => `${sym}${v.toLocaleString()}M`}
                />
              )}
            />
            <Area type="monotone" dataKey="Revenue" stroke="#f59e0b" strokeWidth={2} fill="url(#gRev)" dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
            <Area type="monotone" dataKey="Net Income" stroke="#10b981" strokeWidth={2} fill="url(#gNI)" dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
            <Area type="monotone" dataKey="FCF" stroke="#8b5cf6" strokeWidth={2} fill="url(#gFCF)" dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
          </AreaChart>
        </ResponsiveContainer>
        <div className="mt-3 flex items-center gap-4">
          <LegendDot color="#f59e0b" label="Revenue" />
          <LegendDot color="#10b981" label="Net Income" />
          <LegendDot color="#8b5cf6" label="FCF" />
        </div>
      </div>

      {/* Margin trends */}
      <div className="rounded-2xl border border-[var(--color-border-light)] bg-[var(--color-surface)] p-5">
        <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-[var(--color-text-tertiary)]">
          Margin Trends (%)
        </h3>
        <ResponsiveContainer width="100%" height={210}>
          <LineChart data={marginData} margin={{ top: 8, right: 4, bottom: 0, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={grid} vertical={false} />
            <XAxis dataKey="period" tick={axisStyle} axisLine={false} tickLine={false} />
            <YAxis
              tick={axisStyle}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
              width={36}
            />
            <Tooltip
              content={(props) => (
                <DarkTooltip
                  {...(props as unknown as Parameters<typeof DarkTooltip>[0])}
                  formatter={(v) => `${v.toFixed(1)}%`}
                />
              )}
            />
            <Line type="monotone" dataKey="Gross" stroke="#3b82f6" strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
            <Line type="monotone" dataKey="Operating" stroke="#f59e0b" strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
            <Line type="monotone" dataKey="Net" stroke="#10b981" strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
          </LineChart>
        </ResponsiveContainer>
        <div className="mt-3 flex items-center gap-4">
          <LegendDot color="#3b82f6" label="Gross" />
          <LegendDot color="#f59e0b" label="Operating" />
          <LegendDot color="#10b981" label="Net" />
        </div>
      </div>
    </div>
  );
}
