"use client";

import { useTrending } from "@/hooks/useTrending";
import TrendingCard from "./TrendingCard";

export default function TrendingGrid() {
  const { data, isLoading, error } = useTrending(12);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-44 bg-slate-100 dark:bg-slate-800/60 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
        <p className="text-amber-800 dark:text-amber-200 text-sm">
          Could not load trending data. Check that the API is running.
        </p>
      </div>
    );
  }

  const trending = data?.trending ?? [];

  if (trending.length === 0) {
    return (
      <div className="p-10 bg-slate-50 dark:bg-slate-800/40 rounded-xl text-center">
        <p className="text-slate-500 dark:text-slate-400 text-sm">
          No leaks detected yet. Click <strong>Scrape Now</strong> above to fetch from tech sources.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {trending.map((rumor: any, i: number) => (
        <TrendingCard key={rumor.rumor_id} rumor={rumor} rank={i + 1} />
      ))}
    </div>
  );
}
