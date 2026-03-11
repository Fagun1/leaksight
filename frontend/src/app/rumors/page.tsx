"use client";

import { useRumors } from "@/hooks/useRumors";
import LeakCard from "@/components/rumors/LeakCard";
import type { Rumor } from "@/types/rumor";

export default function RumorsPage() {
  const { data, isLoading, error } = useRumors({ per_page: 50 });

  if (isLoading) {
    return (
      <div className="max-w-[1600px] mx-auto space-y-6">
        <div className="flex items-center gap-2 text-xs font-black text-accent-lime uppercase tracking-[0.3em] mb-1">
          <span className="material-symbols-outlined text-sm">forum</span>
          Intel Feed
        </div>
        <h2 className="text-4xl font-black text-white tracking-tighter">RUMOR_FEED</h2>
        <div className="glass-card rounded-xl p-6 space-y-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-24 bg-white/5 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-[1600px] mx-auto space-y-6">
        <div className="flex items-center gap-2 text-xs font-black text-accent-lime uppercase tracking-[0.3em] mb-1">
          <span className="material-symbols-outlined text-sm">forum</span>
          Intel Feed
        </div>
        <h2 className="text-4xl font-black text-white tracking-tighter">RUMOR_FEED</h2>
        <div className="glass-card rounded-xl p-8 text-center">
          <p className="text-amber-500">Failed to load rumors. Check API connection.</p>
        </div>
      </div>
    );
  }

  const rumors = (data?.data ?? []) as Rumor[];

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div>
        <div className="flex items-center gap-2 text-xs font-black text-accent-lime uppercase tracking-[0.3em] mb-1">
          <span className="material-symbols-outlined text-sm">forum</span>
          Intel Feed
        </div>
        <h2 className="text-4xl font-black text-white tracking-tighter">RUMOR_FEED</h2>
        <p className="text-slate-500 text-sm mt-1">All detected tech leaks and rumors</p>
      </div>

      {rumors.length === 0 ? (
        <div className="p-8 glass-card rounded-xl text-center text-slate-500">
          No rumors yet. Run a scrape or wait for data collection.
        </div>
      ) : (
        <div className="glass-card rounded-xl overflow-hidden">
          <div className="divide-y divide-white/5">
            {rumors.map((rumor) => (
              <LeakCard key={rumor._id} rumor={rumor} expanded={false} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
