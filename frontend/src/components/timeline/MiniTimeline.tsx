"use client";

import type { TimelineEvent } from "@/types/rumor";

export default function MiniTimeline({ events }: { events: TimelineEvent[] }) {
  const list = (events || []).slice(0, 5);
  if (list.length === 0) return null;
  return (
    <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700">
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2">Timeline</p>
      <ul className="space-y-1.5 text-sm">
        {list.map((e, i) => (
          <li key={i} className="flex gap-2">
            <span className="text-slate-400 dark:text-slate-500 shrink-0">
              {(e.date || e.timestamp || "").slice(0, 10)}
            </span>
            <span className="text-slate-600 dark:text-slate-300 truncate">
              {e.description || e.type || e.source || "—"}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
