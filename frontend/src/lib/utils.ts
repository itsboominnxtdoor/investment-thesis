/**
 * Parse a JSON string safely, returning fallback on error.
 */
export function safeJsonParse<T>(json: string | null | undefined, fallback: T): T {
  if (!json) return fallback;
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

/**
 * Clamp a number between min and max.
 */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

/**
 * Truncate text to max length, adding ellipsis if truncated.
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + "...";
}

/**
 * Format a date string to locale date.
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return "—";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/**
 * Format a date to relative time (e.g., "2 hours ago").
 */
export function formatRelativeTime(dateString: string | null | undefined): string {
  if (!dateString) return "—";
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return formatDate(dateString);
}

/**
 * Parse a moat assessment string to display format.
 */
export function formatMoat(moat: string): string {
  return moat.charAt(0).toUpperCase() + moat.slice(1);
}

/**
 * Get badge color for moat assessment.
 */
export function getMoatColor(moat: string): "green" | "yellow" | "gray" {
  switch (moat.toLowerCase()) {
    case "wide":
      return "green";
    case "narrow":
      return "yellow";
    default:
      return "gray";
  }
}

/**
 * Get badge color for conviction direction.
 */
export function getConvictionColor(conviction: string): "green" | "red" | "gray" {
  switch (conviction?.toLowerCase()) {
    case "strengthened":
      return "green";
    case "weakened":
      return "red";
    default:
      return "gray";
  }
}

/**
 * Calculate the midpoint of bull, base, bear targets.
 */
export function calculateMidpoint(
  bull: number | null,
  base: number | null,
  bear: number | null
): number | null {
  const values = [bull, base, bear].filter((v): v is number => v !== null);
  if (values.length === 0) return null;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * Get sector color for visualization.
 */
export function getSectorColor(sector: string): string {
  const colors: Record<string, string> = {
    Technology: "bg-blue-500",
    Financials: "bg-green-500",
    Healthcare: "bg-red-500",
    "Consumer Defensive": "bg-purple-500",
    "Consumer Cyclical": "bg-pink-500",
    Industrials: "bg-yellow-500",
    Energy: "bg-orange-500",
    "Communication Services": "bg-indigo-500",
    "Real Estate": "bg-cyan-500",
    Utilities: "bg-teal-500",
    Materials: "bg-lime-500",
  };
  return colors[sector] || "bg-gray-500";
}
