import { FinancialSnapshotView } from "@/components/FinancialSnapshot";
import { QuarterlyTimeline } from "@/components/QuarterlyTimeline";
import { ThesisCard } from "@/components/ThesisCard";
import { Tabs } from "@/components/ui/Tabs";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default async function CompanyDetailPage({ params }: Props) {
  const { ticker } = await params;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{ticker.toUpperCase()}</h1>
        <p className="text-gray-500">Company details loading from API...</p>
      </div>

      <Tabs
        tabs={[
          {
            id: "overview",
            label: "Overview",
            content: (
              <div className="space-y-6">
                <section>
                  <h2 className="mb-3 text-lg font-semibold">Business Profile</h2>
                  <p className="text-gray-500">Business profile will appear here once data is loaded.</p>
                </section>
                <section>
                  <h2 className="mb-3 text-lg font-semibold">Latest Thesis</h2>
                  <ThesisCard thesis={null} />
                </section>
              </div>
            ),
          },
          {
            id: "financials",
            label: "Financials",
            content: (
              <div className="space-y-6">
                <h2 className="text-lg font-semibold">Financial Snapshots</h2>
                <FinancialSnapshotView snapshot={null} />
              </div>
            ),
          },
          {
            id: "thesis-history",
            label: "Thesis History",
            content: (
              <div>
                <h2 className="mb-3 text-lg font-semibold">All Thesis Versions</h2>
                <p className="text-gray-500">Thesis version history will be displayed here.</p>
              </div>
            ),
          },
          {
            id: "quarterly",
            label: "Quarterly Updates",
            content: <QuarterlyTimeline updates={[]} />,
          },
          {
            id: "documents",
            label: "Documents",
            content: (
              <div>
                <h2 className="mb-3 text-lg font-semibold">Filed Documents</h2>
                <p className="text-gray-500">Document list will appear here.</p>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
