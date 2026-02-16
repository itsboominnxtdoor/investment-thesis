"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

interface Props {
  companyId: string;
  action: "thesis" | "profile" | "financials";
  label: string;
}

const ACTION_URLS: Record<Props["action"], (id: string) => string> = {
  thesis: (id) => `/api/v1/companies/${id}/thesis/generate`,
  profile: (id) => `/api/v1/companies/${id}/business-profile/generate`,
  financials: (id) => `/api/v1/companies/${id}/financials/ingest`,
};

export function GenerateButton({ companyId, action, label }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "";

  async function handleClick() {
    setLoading(true);
    setError(null);
    try {
      const url = `${apiBase}${ACTION_URLS[action](companyId)}`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Request failed (${res.status})`);
      }
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={loading}
        className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Generating..." : label}
      </button>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </div>
  );
}
