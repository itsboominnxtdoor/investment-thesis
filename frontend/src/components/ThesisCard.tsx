import { safeJsonParse } from "@/lib/utils";
import type { ThesisVersion } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";
import { ThesisIntegrityBadge } from "./ThesisIntegrityBadge";

interface Props {
  thesis: ThesisVersion | null;
}

function fmt(val: number | null): string {
  if (val === null) return "—";
  return `$${val.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function CaseBlock({
  label,
  target,
  narrative,
  accent,
}: {
  label: string;
  target: number | null;
  narrative: string;
  accent: "bull" | "base" | "bear";
}) {
  const styles = {
    bull: {
      border: "border-green-500/25",
      bg: "bg-gradient-to-b from-green-500/8 to-transparent",
      labelText: "text-green-500",
      targetText: "text-green-400",
      dot: "bg-green-500",
    },
    base: {
      border: "border-[var(--color-border)]",
      bg: "bg-[var(--color-surface-elevated)]",
      labelText: "text-[var(--color-text-secondary)]",
      targetText: "text-[var(--color-text-primary)]",
      dot: "bg-[var(--color-text-tertiary)]",
    },
    bear: {
      border: "border-red-500/25",
      bg: "bg-gradient-to-b from-red-500/8 to-transparent",
      labelText: "text-red-500",
      targetText: "text-red-400",
      dot: "bg-red-500",
    },
  };

  const s = styles[accent];

  const icons = {
    bull: (
      <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
      </svg>
    ),
    base: (
      <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
      </svg>
    ),
    bear: (
      <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
      </svg>
    ),
  };

  return (
    <div className={`flex flex-col overflow-hidden rounded-2xl border ${s.border} ${s.bg}`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-inherit px-4 py-3">
        <span className={`flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest ${s.labelText}`}>
          <span className={`h-2 w-2 rounded-full ${s.dot}`} />
          {label}
          {icons[accent]}
        </span>
        <span className={`text-2xl font-black tabular-nums tracking-tight ${s.targetText}`}>
          {fmt(target)}
        </span>
      </div>
      {/* Narrative */}
      <p className="flex-1 px-4 py-4 text-sm leading-relaxed text-[var(--color-text-secondary)]">
        {narrative}
      </p>
    </div>
  );
}

function ListSection({
  title,
  items,
  accent,
}: {
  title: string;
  items: string[];
  accent: "blue" | "red" | "green";
}) {
  if (items.length === 0) return null;

  const styles = {
    blue: {
      bg: "bg-blue-500/8 border-blue-500/20",
      title: "text-blue-500",
      dot: "bg-blue-400",
      text: "text-[var(--color-text-secondary)]",
    },
    red: {
      bg: "bg-red-500/8 border-red-500/20",
      title: "text-red-500",
      dot: "bg-red-400",
      text: "text-[var(--color-text-secondary)]",
    },
    green: {
      bg: "bg-green-500/8 border-green-500/20",
      title: "text-green-500",
      dot: "bg-green-400",
      text: "text-[var(--color-text-secondary)]",
    },
  };

  const s = styles[accent];

  return (
    <div className={`rounded-xl border p-4 ${s.bg}`}>
      <h4 className={`mb-3 text-[11px] font-semibold uppercase tracking-widest ${s.title}`}>{title}</h4>
      <ul className="space-y-2">
        {items.map((item, i) => (
          <li key={i} className={`flex items-start gap-2 text-sm ${s.text}`}>
            <span className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${s.dot}`} />
            {item}
          </li>
        ))}
      </ul>
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
      {/* Header */}
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-purple-600">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
              Investment Thesis{" "}
              <span className="text-[var(--color-text-tertiary)]">v{thesis.version}</span>
            </h3>
            <p className="text-xs text-[var(--color-text-tertiary)]">
              Generated {new Date(thesis.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <ThesisIntegrityBadge score={thesis.thesis_integrity_score} />
      </div>

      {/* Scenarios — price targets are the hero */}
      <div className="mb-5 grid gap-3 md:grid-cols-3">
        <CaseBlock label="Bull Case" target={thesis.bull_target} narrative={thesis.bull_case} accent="bull" />
        <CaseBlock label="Base Case" target={thesis.base_target} narrative={thesis.base_case} accent="base" />
        <CaseBlock label="Bear Case" target={thesis.bear_target} narrative={thesis.bear_case} accent="bear" />
      </div>

      {/* Drivers / Risks / Catalysts */}
      {(keyDrivers.length > 0 || keyRisks.length > 0 || catalysts.length > 0) && (
        <div className="grid gap-3 md:grid-cols-3">
          <ListSection title="Key Drivers" items={keyDrivers} accent="blue" />
          <ListSection title="Key Risks" items={keyRisks} accent="red" />
          <ListSection title="Catalysts" items={catalysts} accent="green" />
        </div>
      )}

      {/* Integrity Rationale */}
      {thesis.integrity_rationale && (
        <div className="mt-4 rounded-xl border border-[var(--color-border-light)] bg-[var(--color-surface-elevated)] p-4 text-sm text-[var(--color-text-secondary)]">
          <span className="font-semibold text-[var(--color-text-primary)]">Integrity Rationale: </span>
          {thesis.integrity_rationale}
        </div>
      )}

      {/* Drift Summary */}
      {thesis.drift_summary && (
        <div className="mt-3 flex items-center gap-3 rounded-xl border border-blue-500/20 bg-blue-500/8 p-3 text-sm">
          <svg className="h-4 w-4 shrink-0 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <span className="text-[var(--color-text-secondary)]">
            <span className="font-semibold text-[var(--color-text-primary)]">Drift: </span>
            {thesis.drift_summary}
          </span>
          {thesis.conviction_direction && (
            <Badge
              variant={
                thesis.conviction_direction === "strengthened"
                  ? "green"
                  : thesis.conviction_direction === "weakened"
                  ? "red"
                  : "gray"
              }
              size="sm"
            >
              {thesis.conviction_direction}
            </Badge>
          )}
        </div>
      )}
    </Card>
  );
}
