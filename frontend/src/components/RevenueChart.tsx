"use client";

import { formatCurrency, formatPercent, formatPeriod } from "@/lib/format";
import type { FinancialSnapshot } from "@/types";
import {
  CartesianGrid,
  Legend,
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

export function RevenueChart({ snapshots, currency = "USD" }: Props) {
  if (snapshots.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-center text-gray-500">
        No financial data available for charting.
      </div>
    );
  }

  // Sort chronologically (oldest first)
  const sorted = [...snapshots].sort((a, b) => {
    if (a.fiscal_year !== b.fiscal_year) return a.fiscal_year - b.fiscal_year;
    return a.fiscal_quarter - b.fiscal_quarter;
  });

  const chartData = sorted.map((s) => ({
    period: formatPeriod(s.fiscal_year, s.fiscal_quarter),
    revenue: s.revenue,
    netIncome: s.net_income,
    fcf: s.free_cash_flow,
  }));

  const marginData = sorted.map((s) => ({
    period: formatPeriod(s.fiscal_year, s.fiscal_quarter),
    grossMargin: s.gross_margin ? Number((s.gross_margin * 100).toFixed(1)) : null,
    operatingMargin: s.operating_margin ? Number((s.operating_margin * 100).toFixed(1)) : null,
    netMargin: s.net_margin ? Number((s.net_margin * 100).toFixed(1)) : null,
  }));

  const sym = currency === "CAD" ? "C$" : "$";
  const formatVal = (v: number | null) => {
    if (v === null || v === undefined) return "—";
    return formatCurrency(v, currency);
  };

  return (
    <div className="space-y-6">
      {/* Revenue / Net Income / FCF chart */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 text-sm font-medium text-gray-500">Revenue, Net Income & FCF</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="period" tick={{ fontSize: 12 }} />
            <YAxis
              tick={{ fontSize: 12 }}
              tickFormatter={(v) => formatVal(v)}
            />
            <Tooltip
              formatter={(value: number | undefined) => formatVal(value ?? null)}
              labelStyle={{ fontWeight: 600 }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="revenue"
              name="Revenue"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="netIncome"
              name="Net Income"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="fcf"
              name="Free Cash Flow"
              stroke="#8b5cf6"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Margin trends chart */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 text-sm font-medium text-gray-500">Margin Trends (%)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={marginData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="period" tick={{ fontSize: 12 }} />
            <YAxis
              tick={{ fontSize: 12 }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              formatter={(value: number | undefined) => `${value ?? 0}%`}
              labelStyle={{ fontWeight: 600 }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="grossMargin"
              name="Gross Margin"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="operatingMargin"
              name="Operating Margin"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
            <Line
              type="monotone"
              dataKey="netMargin"
              name="Net Margin"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 3 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
