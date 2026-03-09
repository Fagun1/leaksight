"use client";

import { useRumors } from "@/hooks/useRumors";
import LeakCard from "@/components/rumors/LeakCard";
import type { Rumor } from "@/types/rumor";

export default function RumorsPage() {
  const { data, isLoading, error } = useRumors({ per_page: 50 });

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Rumors</h1>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1 className="text-2xl font-bold">Rumors</h1>
        <p className="mt-4 text-amber-600">Failed to load rumors. Check API connection.</p>
      </div>
    );
  }

  const rumors = (data?.data ?? []) as Rumor[];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Rumors</h1>
        <p className="text-slate-500 mt-1">All detected tech leaks and rumors</p>
      </div>

      {rumors.length === 0 ? (
        <div className="p-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          No rumors yet. Run a scrape or wait for data collection.
        </div>
      ) : (
        <div className="space-y-4">
          {rumors.map((rumor) => (
            <LeakCard key={rumor._id} rumor={rumor} expanded={false} />
          ))}
        </div>
      )}
    </div>
  );
}
