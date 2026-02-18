"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const EXCHANGES = ["All Exchanges", "NYSE", "NASDAQ", "TSX"];

function ExchangeFilterInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const current = searchParams.get("exchange") ?? "";

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const params = new URLSearchParams(searchParams.toString());
    if (e.target.value) {
      params.set("exchange", e.target.value);
    } else {
      params.delete("exchange");
    }
    params.delete("page");
    router.push(`/?${params.toString()}`);
  }

  return (
    <div className="relative">
      <select
        value={current}
        onChange={handleChange}
        className="appearance-none rounded-full border border-[var(--color-border-light)] bg-[var(--color-surface)] py-2.5 pl-4 pr-10 text-sm text-[var(--color-text-primary)] transition-all duration-200 focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 hover:border-[var(--color-border)] cursor-pointer"
      >
        {EXCHANGES.map((exchange) => (
          <option key={exchange} value={exchange === "All Exchanges" ? "" : exchange}>
            {exchange}
          </option>
        ))}
      </select>
      <svg 
        className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" 
        fill="none" 
        viewBox="0 0 24 24" 
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
      </svg>
    </div>
  );
}

export function ExchangeFilter() {
  return (
    <Suspense>
      <ExchangeFilterInner />
    </Suspense>
  );
}
