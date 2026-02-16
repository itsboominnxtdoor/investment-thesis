import type { Company } from "@/types";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";

interface CompanyCardProps {
  company: Company;
}

export function CompanyCard({ company }: CompanyCardProps) {
  return (
    <Card>
      <a href={`/companies/${company.ticker}`} className="block">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-lg font-semibold">{company.ticker}</h3>
            <p className="text-sm text-gray-600">{company.name}</p>
          </div>
          <Badge variant="gray">{company.exchange}</Badge>
        </div>
        <div className="mt-3 flex gap-2">
          <Badge>{company.sector}</Badge>
          <Badge variant="gray">{company.currency}</Badge>
        </div>
      </a>
    </Card>
  );
}
