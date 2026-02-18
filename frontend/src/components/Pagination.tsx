"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";

interface Props {
  page: number;
  totalPages: number;
  total: number;
}

function PaginationInner({ page, totalPages, total }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();

  function goToPage(newPage: number) {
    const params = new URLSearchParams(searchParams.toString());
    if (newPage <= 1) {
      params.delete("page");
    } else {
      params.set("page", String(newPage));
    }
    router.push(`/?${params.toString()}`);
  }

  return (
    <div className="flex items-center justify-between">
      <p className="text-sm text-[var(--color-text-secondary)]">
        Showing <span className="font-medium text-[var(--color-text-primary)]">{total}</span> results
      </p>
      <div className="flex items-center gap-2">
        <button
          onClick={() => goToPage(page - 1)}
          disabled={page <= 1}
          className="inline-flex items-center gap-1.5 rounded-full border border-[var(--color-border-light)] bg-[var(--color-surface)] px-4 py-2 text-sm font-medium text-[var(--color-text-primary)] transition-all duration-200 hover:bg-[var(--color-surface-elevated)] hover:border-[var(--color-border)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Previous
        </button>
        <span className="rounded-full bg-[var(--color-border-light)] px-4 py-2 text-sm font-medium text-[var(--color-text-primary)]">
          {page} / {totalPages}
        </span>
        <button
          onClick={() => goToPage(page + 1)}
          disabled={page >= totalPages}
          className="inline-flex items-center gap-1.5 rounded-full border border-[var(--color-border-light)] bg-[var(--color-surface)] px-4 py-2 text-sm font-medium text-[var(--color-text-primary)] transition-all duration-200 hover:bg-[var(--color-surface-elevated)] hover:border-[var(--color-border)] disabled:cursor-not-allowed disabled:opacity-40"
        >
          Next
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export function Pagination(props: Props) {
  return (
    <Suspense>
      <PaginationInner {...props} />
    </Suspense>
  );
}
