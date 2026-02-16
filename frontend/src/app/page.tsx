import { CompanyTable } from "@/components/CompanyTable";
import { SearchBar } from "@/components/SearchBar";
import { SectorFilter } from "@/components/SectorFilter";

export default function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; sector?: string; exchange?: string; page?: string }>;
}) {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Company Coverage</h1>
      <div className="mb-6 flex flex-wrap items-center gap-4">
        <SearchBar />
        <SectorFilter />
      </div>
      <CompanyTable searchParamsPromise={searchParams} />
    </div>
  );
}
