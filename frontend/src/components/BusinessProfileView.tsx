import type { BusinessProfile } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

interface Props {
  profile: BusinessProfile | null;
}

function safeParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}

export function BusinessProfileView({ profile }: Props) {
  if (!profile) {
    return (
      <Card>
        <p className="text-gray-500">No business profile generated yet.</p>
      </Card>
    );
  }

  const keyProducts = safeParse<string[]>(profile.key_products, []);
  const geographicMix = safeParse<Record<string, number>>(profile.geographic_mix, {});
  const moatSources = safeParse<string[]>(profile.moat_sources, []);

  const moatColor =
    profile.moat_assessment === "wide"
      ? "green"
      : profile.moat_assessment === "narrow"
        ? "yellow"
        : "gray";

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Business Profile v{profile.version}</h3>
        <Badge variant={moatColor}>{profile.moat_assessment} moat</Badge>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="mb-1 text-sm font-medium text-gray-500">Description</h4>
          <p className="text-sm text-gray-800">{profile.description}</p>
        </div>

        <div>
          <h4 className="mb-1 text-sm font-medium text-gray-500">Business Model</h4>
          <p className="text-sm text-gray-800">{profile.business_model}</p>
        </div>

        <div>
          <h4 className="mb-1 text-sm font-medium text-gray-500">Competitive Position</h4>
          <p className="text-sm text-gray-800">{profile.competitive_position}</p>
        </div>

        {keyProducts.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-medium text-gray-500">Key Products & Services</h4>
            <div className="flex flex-wrap gap-2">
              {keyProducts.map((product) => (
                <Badge key={product} variant="blue">
                  {product}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {Object.keys(geographicMix).length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-medium text-gray-500">Geographic Mix</h4>
            <div className="space-y-1">
              {Object.entries(geographicMix).map(([region, pct]) => (
                <div key={region} className="flex items-center justify-between text-sm">
                  <span>{region}</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 rounded-full bg-gray-200">
                      <div
                        className="h-2 rounded-full bg-blue-500"
                        style={{ width: `${Math.round(pct * 100)}%` }}
                      />
                    </div>
                    <span className="w-12 text-right text-gray-600">
                      {Math.round(pct * 100)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {moatSources.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-medium text-gray-500">Moat Sources</h4>
            <div className="flex flex-wrap gap-2">
              {moatSources.map((source) => (
                <Badge key={source} variant="green">
                  {source}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
