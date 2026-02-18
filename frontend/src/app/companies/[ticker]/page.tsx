import { BusinessProfileView } from "@/components/BusinessProfileView";
import { FinancialSnapshotView } from "@/components/FinancialSnapshot";
import { QuarterlyTimeline } from "@/components/QuarterlyTimeline";
import { RevenueChart } from "@/components/RevenueChart";
import { ThesisCard } from "@/components/ThesisCard";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Tabs } from "@/components/ui/Tabs";
import {
  getBusinessProfile,
  getCompanyByTicker,
  getLatestFinancials,
  getLatestThesis,
  listDocuments,
  listFinancials,
  listQuarterlyUpdates,
  listThesisVersions,
} from "@/lib/api-client";

interface Props {
  params: Promise<{ ticker: string }>;
}

function ConvictionBadge({ direction }: { direction: string | null }) {
  if (!direction) return null;
  const colors: Record<string, string> = {
    strengthened: "bg-green-500/10 text-green-600 dark:bg-green-500/20 dark:text-green-400",
    weakened: "bg-red-500/10 text-red-600 dark:bg-red-500/20 dark:text-red-400",
    unchanged: "bg-gray-500/10 text-gray-600 dark:bg-gray-500/20 dark:text-gray-400",
  };
  const arrows: Record<string, string> = {
    strengthened: "↑",
    weakened: "↓",
    unchanged: "→",
  };
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${colors[direction] ?? colors.unchanged}`}>
      <span className="text-sm">{arrows[direction] ?? ""}</span> {direction}
    </span>
  );
}

export default async function CompanyDetailPage({ params }: Props) {
  const { ticker } = await params;

  let company;
  try {
    company = await getCompanyByTicker(ticker);
  } catch {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center py-12 text-center">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-red-500 to-rose-600 shadow-lg">
          <svg className="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-gray-900">Company Not Found</h1>
        <p className="mt-2 text-gray-500">No company with ticker &quot;{ticker.toUpperCase()}&quot; was found.</p>
        <a href="/" className="mt-6 rounded-full bg-gray-900 px-6 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800">
          ← Back to Dashboard
        </a>
      </div>
    );
  }

  // Parallel fetch - catch errors individually so partial data still renders
  const [financials, thesis, profile, quarterlyData, thesisHistory, documentsData, allFinancials] =
    await Promise.all([
      getLatestFinancials(company.id).catch(() => null),
      getLatestThesis(company.id).catch(() => null),
      getBusinessProfile(company.id).catch(() => null),
      listQuarterlyUpdates(company.id).catch(() => null),
      listThesisVersions(company.id).catch(() => null),
      listDocuments(company.id).catch(() => null),
      listFinancials(company.id, { per_page: 20 }).catch(() => null),
    ]);

  const snapshotsList = allFinancials?.items ?? [];

  return (
    <div>
      {/* Company Header */}
      <div className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-gray-50 to-gray-100 p-6 dark:from-gray-800 dark:to-gray-900">
        <div className="flex flex-wrap items-center gap-4">
          {/* Company Logo/Initial */}
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 shadow-md shadow-amber-500/30">
            <span className="text-2xl font-bold text-white">{company.name.charAt(0).toUpperCase()}</span>
          </div>

          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{company.name}</h1>
              <Badge variant="purple" size="md">{company.ticker}</Badge>
              <Badge variant="gray" size="md">{company.exchange}</Badge>
            </div>
            <p className="mt-1.5 flex flex-wrap items-center gap-2 text-sm text-gray-500">
              <span>{company.sector}</span>
              <span className="text-gray-300">•</span>
              <span>{company.industry}</span>
              <span className="text-gray-300">•</span>
              <span>{company.currency}</span>
            </p>
          </div>

          {/* Quick actions */}
          <div className="hidden sm:block">
            <a
              href={`https://finance.yahoo.com/quote/${company.ticker}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:shadow-md dark:bg-gray-800 dark:text-gray-300"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              View on Yahoo
            </a>
          </div>
        </div>
      </div>

      <Tabs
        tabs={[
          {
            id: "overview",
            label: "Overview",
            content: (
              <div className="space-y-6">
                <section>
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600">
                      <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900">Business Profile</h2>
                  </div>
                  <BusinessProfileView profile={profile} />
                </section>
                <section>
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-orange-500">
                      <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <h2 className="text-lg font-semibold text-gray-900">Investment Thesis</h2>
                  </div>
                  <ThesisCard thesis={thesis} />
                </section>
              </div>
            ),
          },
          {
            id: "financials",
            label: "Financials",
            content: (
              <div className="space-y-6">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-green-500 to-emerald-600">
                    <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">Financial Snapshots</h2>
                </div>
                {snapshotsList.length > 1 && (
                  <RevenueChart snapshots={snapshotsList} currency={company.currency} />
                )}
                <FinancialSnapshotView snapshot={financials} />
              </div>
            ),
          },
          {
            id: "thesis-history",
            label: "Thesis History",
            content: (
              <div>
                <h2 className="mb-3 text-lg font-semibold">Thesis Drift Timeline</h2>
                {thesisHistory && thesisHistory.items.length > 0 ? (
                  <div className="space-y-4">
                    {/* Conviction direction timeline */}
                    {thesisHistory.items.length > 1 && (
                      <Card>
                        <h3 className="mb-3 text-sm font-medium text-gray-500">Conviction Direction</h3>
                        <div className="flex items-center gap-2 overflow-x-auto pb-2">
                          {[...thesisHistory.items].reverse().map((tv, i) => (
                            <div key={tv.id} className="flex items-center gap-2">
                              <div className="flex flex-col items-center">
                                <span className="text-xs font-medium text-gray-600">v{tv.version}</span>
                                <div className={`mt-1 h-3 w-3 rounded-full ${
                                  tv.conviction_direction === "strengthened" ? "bg-green-500" :
                                  tv.conviction_direction === "weakened" ? "bg-red-500" :
                                  "bg-gray-300"
                                }`} />
                                {tv.thesis_integrity_score !== null && (
                                  <span className="mt-1 text-[10px] text-gray-400">{tv.thesis_integrity_score}</span>
                                )}
                              </div>
                              {i < thesisHistory.items.length - 1 && (
                                <div className="h-px w-8 bg-gray-200" />
                              )}
                            </div>
                          ))}
                        </div>
                      </Card>
                    )}
                    {/* Full thesis cards */}
                    {thesisHistory.items.map((tv) => (
                      <div key={tv.id}>
                        {tv.conviction_direction && (
                          <div className="mb-1 flex items-center gap-2">
                            <ConvictionBadge direction={tv.conviction_direction} />
                            {tv.drift_summary && (
                              <span className="text-xs text-gray-400 truncate max-w-md">{tv.drift_summary}</span>
                            )}
                          </div>
                        )}
                        <ThesisCard thesis={tv} />
                      </div>
                    ))}
                  </div>
                ) : (
                  <Card>
                    <p className="text-gray-500">No thesis versions available.</p>
                  </Card>
                )}
              </div>
            ),
          },
          {
            id: "quarterly",
            label: "Quarterly",
            content: (
              <div className="space-y-4">
                <h2 className="text-lg font-semibold">Quarterly Updates</h2>
                <QuarterlyTimeline
                  updates={quarterlyData?.items ?? []}
                  snapshots={snapshotsList}
                />
              </div>
            ),
          },
          {
            id: "documents",
            label: "Documents",
            content: (
              <div>
                <h2 className="mb-3 text-lg font-semibold">Filed Documents</h2>
                {documentsData && documentsData.items.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                      <thead>
                        <tr className="border-b text-gray-500">
                          <th className="pb-2 font-medium">Type</th>
                          <th className="pb-2 font-medium">Source</th>
                          <th className="pb-2 font-medium">Filing Date</th>
                          <th className="pb-2 font-medium">Link</th>
                        </tr>
                      </thead>
                      <tbody>
                        {documentsData.items.map((doc) => (
                          <tr key={doc.id} className="border-b">
                            <td className="py-2">
                              <Badge variant="default">{doc.doc_type}</Badge>
                            </td>
                            <td className="py-2 capitalize">{doc.source}</td>
                            <td className="py-2">{doc.filing_date ?? "N/A"}</td>
                            <td className="py-2">
                              {doc.source_url && (
                                <a
                                  href={doc.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-600 hover:underline"
                                >
                                  View
                                </a>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <Card>
                    <p className="text-gray-500">No documents available.</p>
                  </Card>
                )}
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
