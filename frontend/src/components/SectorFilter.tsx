"use client";

import { useRouter, useSearchParams } from "next/navigation";

const SECTORS = [
  "All Sectors",
  "Technology",
  "Healthcare",
  "Financials",
  "Consumer Discretionary",
  "Consumer Staples",
  "Energy",
  "Industrials",
  "Materials",
  "Real Estate",
  "Utilities",
  "Communication Services",
];

export function SectorFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("sector") ?? "";

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const params = new URLSearchParams(searchParams.toString());
    if (e.target.value) {
      params.set("sector", e.target.value);
    } else {
      params.delete("sector");
    }
    params.delete("page");
    router.push(`/?${params.toString()}`);
  }

  return (
    <select
      value={current}
      onChange={handleChange}
      className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
    >
      {SECTORS.map((sector) => (
        <option key={sector} value={sector === "All Sectors" ? "" : sector}>
          {sector}
        </option>
      ))}
    </select>
  );
}
