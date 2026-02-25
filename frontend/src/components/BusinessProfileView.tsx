import type { BusinessProfile } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

interface Props {
  profile: BusinessProfile | null;
}

/** Parse a segment/geo map stored as JSON, normalising to decimal fractions.
 *  Handles three LLM output shapes:
 *  1. {"iPhone": 0.52, "Services": 0.22}  — already decimal, returned as-is
 *  2. {"iPhone": 52, "Services": 22}       — integers summing to ~100, divided by 100
 *  3. ["iPhone", "Services"]               — old list format, returns null (hidden)
 */
function parseSegmentMap(raw: string | null | undefined): Record<string, number> | null {
  if (!raw) return null;
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return null;
  }
  if (Array.isArray(parsed) || typeof parsed !== "object" || parsed === null) return null;

  const entries = Object.entries(parsed as Record<string, unknown>);
  if (entries.length === 0) return null;

  // Coerce all values to numbers, drop non-numeric entries
  const numeric: Record<string, number> = {};
  for (const [k, v] of entries) {
    const n = typeof v === "number" ? v : parseFloat(String(v));
    if (!isNaN(n)) numeric[k] = n;
  }
  if (Object.keys(numeric).length === 0) return null;

  // Normalise: if values sum to > 5, assume they are whole percentages (0-100)
  const sum = Object.values(numeric).reduce((a, b) => a + b, 0);
  if (sum > 5) {
    return Object.fromEntries(Object.entries(numeric).map(([k, v]) => [k, v / 100]));
  }
  return numeric;
}

export function BusinessProfileView({ profile }: Props) {
  if (!profile) {
    return (
      <Card>
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <svg className="mb-4 h-12 w-12 text-[var(--color-text-tertiary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
          <p className="text-[var(--color-text-secondary)]">No business profile generated yet.</p>
        </div>
      </Card>
    );
  }

  const businessSegments = parseSegmentMap(profile.key_products);
  const geographicMix = parseSegmentMap(profile.geographic_mix);
  // moat_sources is now a plain-text rationale string
  const moatRationale = typeof profile.moat_sources === "string" && !profile.moat_sources.startsWith("[")
    ? profile.moat_sources
    : null;

  const moatColor =
    profile.moat_assessment === "wide"
      ? "green"
      : profile.moat_assessment === "narrow"
        ? "amber"
        : "gray";

  return (
    <Card>
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600">
            <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)]">
              Business Profile <span className="text-[var(--color-text-tertiary)]">v{profile.version}</span>
            </h3>
            <p className="text-xs text-[var(--color-text-secondary)]">
              Updated {new Date(profile.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
        <Badge variant={moatColor} size="md">
          {profile.moat_assessment === "wide" && (
            <svg className="mr-1.5 h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          )}
          {profile.moat_assessment} moat
        </Badge>
      </div>

      <div className="space-y-5">
        <div className="rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 p-4 dark:from-violet-900/20 dark:to-purple-900/20">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-violet-700 dark:text-violet-400">
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
            </svg>
            Description
          </h4>
          <p className="text-sm leading-relaxed text-[var(--color-text-primary)]">{profile.description}</p>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-blue-50 to-cyan-50 p-4 dark:from-blue-900/20 dark:to-cyan-900/20">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-blue-700 dark:text-blue-400">
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z" />
              <path fillRule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clipRule="evenodd" />
            </svg>
            Business Model
          </h4>
          <p className="text-sm leading-relaxed text-[var(--color-text-primary)]">{profile.business_model}</p>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-amber-50 to-orange-50 p-4 dark:from-amber-900/20 dark:to-orange-900/20">
          <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-amber-700 dark:text-amber-400">
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
            </svg>
            Competitive Position
          </h4>
          <p className="text-sm leading-relaxed text-[var(--color-text-primary)]">{profile.competitive_position}</p>
        </div>

        {businessSegments && Object.keys(businessSegments).length > 0 && (
          <div>
            <h4 className="mb-3 text-sm font-semibold text-[var(--color-text-secondary)]">Business Segments</h4>
            <div className="space-y-2.5">
              {Object.entries(businessSegments)
                .sort(([, a], [, b]) => b - a)
                .map(([segment, pct]) => (
                  <div key={segment} className="flex items-center gap-3">
                    <span className="w-36 truncate text-sm text-[var(--color-text-primary)]">{segment}</span>
                    <div className="flex-1 overflow-hidden rounded-full bg-[var(--color-border-light)]">
                      <div
                        className="h-2 rounded-full bg-gradient-to-r from-violet-500 to-purple-500 transition-all duration-500"
                        style={{ width: `${Math.min(Math.round(pct * 100), 100)}%` }}
                      />
                    </div>
                    <span className="w-12 text-right text-sm font-medium text-[var(--color-text-secondary)]">
                      {Math.round(pct * 100)}%
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {geographicMix && Object.keys(geographicMix).length > 0 && (
          <div>
            <h4 className="mb-3 text-sm font-semibold text-[var(--color-text-secondary)]">Geographic Mix</h4>
            <div className="space-y-2.5">
              {Object.entries(geographicMix!).map(([region, pct]) => (
                <div key={region} className="flex items-center gap-3">
                  <span className="w-24 text-sm text-[var(--color-text-primary)]">{region}</span>
                  <div className="flex-1 overflow-hidden rounded-full bg-[var(--color-border-light)]">
                    <div
                      className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500"
                      style={{ width: `${Math.min(Math.round(pct * 100), 100)}%` }}
                    />
                  </div>
                  <span className="w-12 text-right text-sm font-medium text-[var(--color-text-secondary)]">
                    {Math.round(pct * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {moatRationale && (
          <div className="rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 p-4 dark:from-green-900/20 dark:to-emerald-900/20">
            <h4 className="mb-2 flex items-center gap-2 text-sm font-semibold text-green-700 dark:text-green-400">
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Moat Rationale
              <Badge variant={moatColor} size="sm" className="ml-1">{profile.moat_assessment}</Badge>
            </h4>
            <p className="text-sm leading-relaxed text-[var(--color-text-primary)]">{moatRationale}</p>
          </div>
        )}
      </div>
    </Card>
  );
}
