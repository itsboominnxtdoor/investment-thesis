import { formatCurrency } from "@/lib/format";
import { safeJsonParse } from "@/lib/utils";
import type { ThesisVersion } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";
import { ThesisIntegrityBadge } from "./ThesisIntegrityBadge";

interface Props {
  thesis: ThesisVersion | null;
}

function CaseCard({
  title,
  content,
  target,
  color,
  icon
}: {
  title: string;
  content: string;
  target: number | string | null;
  color: "green" | "gray" | "red";
  icon: React.ReactNode;
}) {
  const colorClasses = {
    green: "from-green-500/10 to-emerald-500/10 border-green-500/20",
    gray: "from-gray-500/10 to-slate-500/10 border-gray-500/20",
    red: "from-red-500/10 to-rose-500/10 border-red-500/20",
  };

  const titleColors = {
    green: "text-green-600 dark:text-green-400",
    gray: "text-gray-600 dark:text-gray-400",
    red: "text-red-600 dark:text-red-400",
  };

  return (
    <div className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br p-5 ${colorClasses[color]}`}>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={`text-xl ${titleColors[color]}`}>{icon}</span>
          <h4 className={`font-semibold ${titleColors[color]}`}>{title}</h4>
        </div>
        {target && (
          <span className={`rounded-full px-3 py-1 text-sm font-semibold ${
            color === "green" ? "bg-green-500 text-white" :
            color === "red" ? "bg-red-500 text-white" :
            "bg-gray-500 text-white"
          }`}>
            {formatCurrency(typeof target === "number" ? target : parseFloat(target))}
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed text-[var(--color-text-secondary)]">{content}</p>
    </div>
  );
}

export function ThesisCard({ thesis }: Props) {
  if (!thesis) {
    return (
      <Card>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="mb-4 h-12 w-12 text-[var(--color-text-tertiary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-[var(--color-text-secondary)]">No thesis generated yet.</p>
        </div>
      </Card>
    );
  }

  const keyDrivers = safeJsonParse<string[]>(thesis.key_drivers, []);
  const keyRisks = safeJsonParse<string[]>(thesis.key_risks, []);
  const catalysts = safeJsonParse<string[]>(thesis.catalysts, []);

  return (
    <Card>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
              Investment Thesis <span className="text-[var(--color-text-tertiary)]">v{thesis.version}</span>
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Generated {new Date(thesis.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <ThesisIntegrityBadge score={thesis.thesis_integrity_score} />
      </div>

      {/* Three scenarios */}
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <CaseCard
          title="Bull Case"
          content={thesis.bull_case}
          target={thesis.bull_target}
          color="green"
          icon={
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          }
        />
        <CaseCard
          title="Base Case"
          content={thesis.base_case}
          target={thesis.base_target}
          color="gray"
          icon={
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
            </svg>
          }
        />
        <CaseCard
          title="Bear Case"
          content={thesis.bear_case}
          target={thesis.bear_target}
          color="red"
          icon={
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          }
        />
      </div>

      {/* Key Drivers, Risks, Catalysts */}
      {(keyDrivers.length > 0 || keyRisks.length > 0 || catalysts.length > 0) && (
        <div className="grid gap-4 md:grid-cols-3">
          {keyDrivers.length > 0 && (
            <div className="rounded-xl bg-blue-50 p-4 dark:bg-blue-900/20">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-blue-700 dark:text-blue-400">
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                Key Drivers
              </h4>
              <ul className="space-y-2">
                {keyDrivers.map((driver, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-blue-900 dark:text-blue-100">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"></span>
                    {driver}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {keyRisks.length > 0 && (
            <div className="rounded-xl bg-red-50 p-4 dark:bg-red-900/20">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-700 dark:text-red-400">
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Key Risks
              </h4>
              <ul className="space-y-2">
                {keyRisks.map((risk, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-red-900 dark:text-red-100">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-500"></span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {catalysts.length > 0 && (
            <div className="rounded-xl bg-green-50 p-4 dark:bg-green-900/20">
              <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-green-700 dark:text-green-400">
                <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                </svg>
                Catalysts
              </h4>
              <ul className="space-y-2">
                {catalysts.map((catalyst, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-green-900 dark:text-green-100">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-green-500"></span>
                    {catalyst}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Integrity Rationale */}
      {thesis.integrity_rationale && (
        <div className="mt-4 rounded-xl bg-[var(--color-border-light)] p-4 text-sm text-[var(--color-text-secondary)]">
          <strong className="text-[var(--color-text-primary)]">Integrity Rationale:</strong> {thesis.integrity_rationale}
        </div>
      )}

      {/* Drift Summary */}
      {thesis.drift_summary && (
        <div className="mt-3 flex items-center gap-2 rounded-xl bg-blue-50 p-3 text-sm text-blue-800 dark:bg-blue-900/20 dark:text-blue-200">
          <svg className="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span><strong>Drift:</strong> {thesis.drift_summary}</span>
          {thesis.conviction_direction && (
            <Badge variant={thesis.conviction_direction === "strengthened" ? "green" : thesis.conviction_direction === "weakened" ? "red" : "gray"} size="sm">
              {thesis.conviction_direction}
            </Badge>
          )}
        </div>
      )}
    </Card>
  );
}
