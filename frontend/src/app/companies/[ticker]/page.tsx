import { BusinessProfileView } from "@/components/BusinessProfileView";
import { FinancialSnapshotView } from "@/components/FinancialSnapshot";
import { GenerateButton } from "@/components/GenerateThesisButton";
import { QuarterlyTimeline } from "@/components/QuarterlyTimeline";
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
  listQuarterlyUpdates,
  listThesisVersions,
} from "@/lib/api-client";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default async function CompanyDetailPage({ params }: Props) {
  const { ticker } = await params;

  let company;
  try {
    company = await getCompanyByTicker(ticker);
  } catch {
    return (
      <div className="py-12 text-center">
        <h1 className="text-2xl font-bold">Company Not Found</h1>
        <p className="mt-2 text-gray-500">No company with ticker &quot;{ticker.toUpperCase()}&quot; was found.</p>
      </div>
    );
  }

  // Parallel fetch - catch errors individually so partial data still renders
  const [financials, thesis, profile, quarterlyData, thesisHistory, documentsData] =
    await Promise.all([
      getLatestFinancials(company.id).catch(() => null),
      getLatestThesis(company.id).catch(() => null),
      getBusinessProfile(company.id).catch(() => null),
      listQuarterlyUpdates(company.id).catch(() => null),
      listThesisVersions(company.id).catch(() => null),
      listDocuments(company.id).catch(() => null),
    ]);

  return (
    <div>
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">{company.name}</h1>
          <Badge variant="default">{company.ticker}</Badge>
          <Badge variant="gray">{company.exchange}</Badge>
        </div>
        <p className="mt-1 text-gray-500">
          {company.sector} &middot; {company.industry} &middot; {company.currency}
        </p>
      </div>

      <Tabs
        tabs={[
          {
            id: "overview",
            label: "Overview",
            content: (
              <div className="space-y-6">
                <section>
                  <div className="mb-3 flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Business Profile</h2>
                    <GenerateButton
                      companyId={company.id}
                      action="profile"
                      label={profile ? "Regenerate Profile" : "Generate Profile"}
                    />
                  </div>
                  <BusinessProfileView profile={profile} />
                </section>
                <section>
                  <div className="mb-3 flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Latest Thesis</h2>
                    <GenerateButton
                      companyId={company.id}
                      action="thesis"
                      label={thesis ? "Regenerate Thesis" : "Generate Thesis"}
                    />
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
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold">Financial Snapshots</h2>
                  <GenerateButton
                    companyId={company.id}
                    action="financials"
                    label={financials ? "Ingest Latest" : "Ingest Financials"}
                  />
                </div>
                <FinancialSnapshotView snapshot={financials} />
              </div>
            ),
          },
          {
            id: "thesis-history",
            label: "Thesis History",
            content: (
              <div>
                <h2 className="mb-3 text-lg font-semibold">All Thesis Versions</h2>
                {thesisHistory && thesisHistory.items.length > 0 ? (
                  <div className="space-y-4">
                    {thesisHistory.items.map((tv) => (
                      <ThesisCard key={tv.id} thesis={tv} />
                    ))}
                  </div>
                ) : (
                  <Card>
                    <p className="text-gray-500">No thesis versions yet. Generate one from the Overview tab.</p>
                  </Card>
                )}
              </div>
            ),
          },
          {
            id: "quarterly",
            label: "Quarterly Updates",
            content: <QuarterlyTimeline updates={quarterlyData?.items ?? []} />,
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
                    <p className="text-gray-500">No documents available yet.</p>
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
