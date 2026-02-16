import { listCompanies } from "@/lib/api-client";
import type { Company } from "@/types";
import { Badge } from "./ui/Badge";

interface Props {
  searchParamsPromise: Promise<{
    search?: string;
    sector?: string;
    exchange?: string;
    page?: string;
  }>;
}

export async function CompanyTable({ searchParamsPromise }: Props) {
  const searchParams = await searchParamsPromise;
  let companies: Company[] = [];
  let total = 0;
  let error: string | null = null;
  const page = Number(searchParams.page) || 1;

  try {
    const data = await listCompanies({
      page,
      search: searchParams.search,
      sector: searchParams.sector,
      exchange: searchParams.exchange,
    });
    companies = data.items;
    total = data.total;
  } catch {
    error = "Unable to load companies. Is the backend running?";
  }

  if (error) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 text-center text-amber-800">
        {error}
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-center text-gray-500">
        No companies found. Add companies via the ingestion pipeline.
      </div>
    );
  }

  return (
    <div>
      <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-gray-50 text-xs uppercase text-gray-500">
            <tr>
              <th className="px-4 py-3">Ticker</th>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Exchange</th>
              <th className="px-4 py-3">Sector</th>
              <th className="px-4 py-3">Currency</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {companies.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <a href={`/companies/${c.ticker}`} className="font-medium text-blue-600 hover:underline">
                    {c.ticker}
                  </a>
                </td>
                <td className="px-4 py-3">{c.name}</td>
                <td className="px-4 py-3">
                  <Badge variant="gray">{c.exchange}</Badge>
                </td>
                <td className="px-4 py-3">{c.sector}</td>
                <td className="px-4 py-3">{c.currency}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-3 text-sm text-gray-500">
        Showing {companies.length} of {total} companies (page {page})
      </p>
    </div>
  );
}
