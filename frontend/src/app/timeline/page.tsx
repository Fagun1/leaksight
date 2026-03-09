"use client";

import { useTrending } from "@/hooks/useTrending";
import Link from "next/link";

export default function TimelinePage() {
  const { data } = useTrending(30);
  const trending = data?.trending ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Leak Timeline
        </h1>
        <p className="text-slate-500 mt-1">Chronological view of trending leaks</p>
      </div>

      {trending.length === 0 ? (
        <div className="p-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          No timeline data yet.
        </div>
      ) : (
        <div className="space-y-4">
          {trending.map((rumor: any, i: number) => (
            <Link
              key={rumor.rumor_id}
              href={`/rumors/${rumor.rumor_id}`}
              className="block p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:shadow-md transition-shadow"
            >
              <div className="flex gap-4">
                <div className="text-slate-400 font-mono text-sm w-24 shrink-0">
                  {new Date(rumor.first_seen).toLocaleDateString()}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {rumor.title}
                  </h3>
                  {rumor.summary && (
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-1">
                      {rumor.summary}
                    </p>
                  )}
                  <div className="flex gap-2 mt-2">
                    <span className="text-xs text-cyan-600">
                      {rumor.total_mentions} posts
                    </span>
                    <span className="text-xs text-slate-400">
                      {rumor.credibility_score}% credible
                    </span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
