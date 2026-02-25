"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "drft_watchlist";

function getWatchlist(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? new Set(JSON.parse(raw) as string[]) : new Set();
  } catch {
    return new Set();
  }
}

function saveWatchlist(ids: Set<string>) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]));
}

interface Props {
  companyId: string;
  ticker: string;
}

export function WatchlistStar({ companyId, ticker }: Props) {
  const [watching, setWatching] = useState(false);

  useEffect(() => {
    setWatching(getWatchlist().has(companyId));
  }, [companyId]);

  function toggle(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    const wl = getWatchlist();
    if (wl.has(companyId)) {
      wl.delete(companyId);
    } else {
      wl.add(companyId);
    }
    saveWatchlist(wl);
    setWatching(wl.has(companyId));
  }

  return (
    <button
      onClick={toggle}
      className="relative z-10 shrink-0 rounded p-0.5 transition-colors hover:text-amber-400"
      title={watching ? `Remove ${ticker} from watchlist` : `Add ${ticker} to watchlist`}
    >
      <svg
        className="h-4 w-4 transition-all duration-150"
        fill={watching ? "#f59e0b" : "none"}
        viewBox="0 0 24 24"
        stroke={watching ? "#f59e0b" : "currentColor"}
        strokeWidth={1.5}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
        />
      </svg>
    </button>
  );
}
