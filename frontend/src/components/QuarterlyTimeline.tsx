import { formatPeriod } from "@/lib/format";
import type { QuarterlyUpdate } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

interface Props {
  updates: QuarterlyUpdate[];
}

export function QuarterlyTimeline({ updates }: Props) {
  if (updates.length === 0) {
    return (
      <Card>
        <p className="text-gray-500">No quarterly updates available yet.</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {updates.map((update) => (
        <Card key={update.id}>
          <div className="mb-2 flex items-center gap-3">
            <h3 className="font-semibold">
              {formatPeriod(update.fiscal_year, update.fiscal_quarter)}
            </h3>
            <Badge variant="gray">{update.filing_type}</Badge>
          </div>
          <p className="text-sm text-gray-700">{update.executive_summary}</p>
          {update.guidance_update && (
            <div className="mt-3 rounded bg-blue-50 p-3 text-sm text-blue-800">
              <strong>Guidance:</strong> {update.guidance_update}
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}
