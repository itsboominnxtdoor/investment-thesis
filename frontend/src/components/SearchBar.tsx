"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

function SearchBarInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [value, setValue] = useState(searchParams.get("search") ?? "");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set("search", value);
    } else {
      params.delete("search");
    }
    params.delete("page");
    router.push(`/?${params.toString()}`);
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="group relative flex items-center">
        <svg 
          className="absolute left-3 h-4 w-4 text-[var(--color-text-tertiary)] transition-colors group-focus-within:text-[var(--color-primary)]" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Search companies..."
          className="w-64 rounded-full border border-[var(--color-border-light)] bg-[var(--color-surface)] py-2.5 pl-10 pr-4 text-sm text-[var(--color-text-primary)] placeholder-[var(--color-text-tertiary)] transition-all duration-200 focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]/20 hover:border-[var(--color-border)]"
        />
      </div>
    </form>
  );
}

export function SearchBar() {
  return (
    <Suspense>
      <SearchBarInner />
    </Suspense>
  );
}
