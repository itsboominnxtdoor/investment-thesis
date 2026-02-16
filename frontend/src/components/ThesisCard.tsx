import { formatCurrency } from "@/lib/format";
import type { ThesisVersion } from "@/types";
import { Card } from "./ui/Card";
import { ThesisIntegrityBadge } from "./ThesisIntegrityBadge";

interface Props {
  thesis: ThesisVersion | null;
}

export function ThesisCard({ thesis }: Props) {
  if (!thesis) {
    return (
      <Card>
        <p className="text-gray-500">No thesis generated yet.</p>
      </Card>
    );
  }

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Investment Thesis v{thesis.version}</h3>
        <ThesisIntegrityBadge score={thesis.thesis_integrity_score} />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {/* Bull Case */}
        <div className="rounded-lg border-l-4 border-green-500 bg-green-50 p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="font-semibold text-green-800">Bull Case</h4>
            {thesis.bull_target && (
              <span className="text-sm font-medium text-green-700">
                {formatCurrency(thesis.bull_target)}
              </span>
            )}
          </div>
          <p className="text-sm text-green-900">{thesis.bull_case}</p>
        </div>

        {/* Base Case */}
        <div className="rounded-lg border-l-4 border-gray-400 bg-gray-50 p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="font-semibold text-gray-800">Base Case</h4>
            {thesis.base_target && (
              <span className="text-sm font-medium text-gray-700">
                {formatCurrency(thesis.base_target)}
              </span>
            )}
          </div>
          <p className="text-sm text-gray-900">{thesis.base_case}</p>
        </div>

        {/* Bear Case */}
        <div className="rounded-lg border-l-4 border-red-500 bg-red-50 p-4">
          <div className="mb-2 flex items-center justify-between">
            <h4 className="font-semibold text-red-800">Bear Case</h4>
            {thesis.bear_target && (
              <span className="text-sm font-medium text-red-700">
                {formatCurrency(thesis.bear_target)}
              </span>
            )}
          </div>
          <p className="text-sm text-red-900">{thesis.bear_case}</p>
        </div>
      </div>

      {thesis.drift_summary && (
        <div className="mt-4 rounded bg-blue-50 p-3 text-sm text-blue-800">
          <strong>Drift:</strong> {thesis.drift_summary}
          {thesis.conviction_direction && (
            <span className="ml-2 font-medium capitalize">({thesis.conviction_direction})</span>
          )}
        </div>
      )}
    </Card>
  );
}
