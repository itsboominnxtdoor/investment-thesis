interface StatProps {
  label: string;
  value: string | number | null;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  className?: string;
  icon?: React.ReactNode;
}

export function Stat({ label, value, trend, trendValue, className = "", icon }: StatProps) {
  return (
    <div className={`group relative overflow-hidden rounded-2xl bg-[var(--color-surface)] p-6 shadow-sm transition-all duration-300 hover:shadow-md ${className}`}>
      {/* Gradient border effect */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-violet-500/10 to-purple-500/10 opacity-0 transition-opacity group-hover:opacity-100"></div>
      
      <div className="relative">
        <div className="flex items-start justify-between">
          <dt className="text-sm font-medium text-[var(--color-text-secondary)]">{label}</dt>
          {icon && <span className="text-[var(--color-text-tertiary)]">{icon}</span>}
        </div>
        <dd className="mt-3 flex items-baseline justify-between">
          <span className="text-3xl font-semibold tracking-tight text-[var(--color-text-primary)]">
            {value ?? "—"}
          </span>
          {trend && trendValue && (
            <span className={`flex items-center text-sm font-medium ${
              trend === "up" ? "text-green-500" :
              trend === "down" ? "text-red-500" :
              "text-[var(--color-text-secondary)]"
            }`}>
              {trend === "up" && (
                <svg className="mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {trend === "down" && (
                <svg className="mr-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {trendValue}
            </span>
          )}
        </dd>
      </div>
    </div>
  );
}

interface StatGridProps {
  children: React.ReactNode;
  columns?: 2 | 3 | 4;
  className?: string;
}

export function StatGrid({ children, columns = 4, className = "" }: StatGridProps) {
  return (
    <div className={`grid gap-4 sm:grid-cols-2 lg:grid-cols-4 ${className}`}>
      {children}
    </div>
  );
}
