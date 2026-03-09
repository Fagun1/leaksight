"use client";

import { useTrending } from "@/hooks/useTrending";

const STAT_CARDS = [
  {
    key: "leaks_total",
    label: "Leaks Detected",
    icon: "🔍",
    color: "text-cyan-600 dark:text-cyan-400",
    bg: "bg-cyan-50 dark:bg-cyan-950/40",
  },
  {
    key: "total_rumors",
    label: "Active Rumors",
    icon: "📰",
    color: "text-violet-600 dark:text-violet-400",
    bg: "bg-violet-50 dark:bg-violet-950/40",
  },
  {
    key: "total_posts",
    label: "Total Posts",
    icon: "📄",
    color: "text-emerald-600 dark:text-emerald-400",
    bg: "bg-emerald-50 dark:bg-emerald-950/40",
  },
  {
    key: "avg_confidence",
    label: "Avg Confidence",
    icon: "🎯",
    color: "text-amber-600 dark:text-amber-400",
    bg: "bg-amber-50 dark:bg-amber-950/40",
    suffix: "%",
  },
];

export default function StatsOverview() {
  const { data, isLoading } = useTrending();
  const stats = data?.stats ?? {};

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {STAT_CARDS.map((card) => (
        <div
          key={card.key}
          className={`${card.bg} rounded-xl p-5 border border-slate-200/60 dark:border-slate-700/40`}
        >
          <div className="flex items-center gap-2 mb-2">
            <span className="text-lg">{card.icon}</span>
            <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
              {card.label}
            </span>
          </div>
          <p className={`text-3xl font-bold ${card.color}`}>
            {stats[card.key] ?? 0}{card.suffix ?? ""}
          </p>
        </div>
      ))}
    </div>
  );
}
