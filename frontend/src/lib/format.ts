/**
 * Format a number as abbreviated currency (e.g. 1.2B, 340M, 12K).
 */
export function formatCurrency(value: number | string | null | undefined, currency = "USD"): string {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  
  const abs = Math.abs(num);
  const sign = num < 0 ? "-" : "";
  const sym = currency === "CAD" ? "C$" : "$";

  if (abs >= 1_000_000_000) return `${sign}${sym}${(abs / 1_000_000_000).toFixed(1)}B`;
  if (abs >= 1_000_000) return `${sign}${sym}${(abs / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `${sign}${sym}${(abs / 1_000).toFixed(1)}K`;
  return `${sign}${sym}${abs.toFixed(2)}`;
}

/**
 * Format a decimal ratio as a percentage string (e.g. 0.2534 -> "25.3%").
 */
export function formatPercent(value: number | string | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const num = typeof value === "string" ? parseFloat(value) : value;
  if (isNaN(num)) return "—";
  return `${(num * 100).toFixed(1)}%`;
}

/**
 * Format fiscal period label (e.g. "Q3 2025").
 */
export function formatPeriod(year: number, quarter: number): string {
  return `Q${quarter} ${year}`;
}

/**
 * Format a number with commas (e.g. 1234567 -> "1,234,567").
 */
export function formatNumber(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return value.toLocaleString("en-US");
}
