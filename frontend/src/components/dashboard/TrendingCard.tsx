"use client";

import Link from "next/link";
import type { TrendingRumor } from "@/types/rumor";

interface TrendingCardProps {
  rumor: TrendingRumor;
  rank: number;
}

const CATEGORY_STYLES: Record<string, { icon: string; label: string; cls: string }> = {
  PRODUCT_LEAK: { icon: "📱", label: "Product", cls: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300" },
  FEATURE_LEAK: { icon: "⚡", label: "Feature", cls: "bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300" },
  HARDWARE_LEAK: { icon: "🔧", label: "Hardware", cls: "bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300" },
  LEAK: { icon: "🔍", label: "Leak", cls: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300" },
};

function cleanTitle(raw: string): string {
  let t = raw;
  const byIdx = t.indexOf("By");
  if (byIdx > 20) t = t.slice(0, byIdx);
  const pubIdx = t.indexOf("published");
  if (pubIdx > 20) t = t.slice(0, pubIdx);
  return t.trim().replace(/\s+/g, " ");
}

function timeAgo(dateStr: string | undefined): string {
  if (!dateStr) return "";
  const diff = Date.now() - new Date(dateStr).getTime();
  const hrs = Math.floor(diff / 3_600_000);
  if (hrs < 1) return "Just now";
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

export default function TrendingCard({ rumor, rank }: TrendingCardProps) {
  const cat = CATEGORY_STYLES[rumor.category] ?? CATEGORY_STYLES.LEAK;
  const score = rumor.credibility_score ?? 0;
  const title = cleanTitle(rumor.title || "Untitled Leak");
  const companies = rumor.entities?.companies ?? [];
  const products = rumor.entities?.products ?? [];

  return (
    <Link href={`/rumors/${rumor.rumor_id}`} className="group block">
      <div className="relative bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 h-full hover:border-cyan-400 dark:hover:border-cyan-600 transition-colors">
        <div className="flex items-center justify-between mb-3">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${cat.cls}`}>
            {cat.icon} {cat.label}
          </span>
          <span className="text-xs text-slate-400 tabular-nums">
            {timeAgo(rumor.first_seen as any)}
          </span>
        </div>

        <h3 className="font-semibold text-slate-900 dark:text-white text-[15px] leading-snug mb-3 line-clamp-2 group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors">
          {title}
        </h3>

        {(companies.length > 0 || products.length > 0) && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {companies.slice(0, 3).map((c: string) => (
              <span key={c} className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded text-[11px] font-medium">
                {c}
              </span>
            ))}
            {products.slice(0, 2).map((p: string) => (
              <span key={p} className="px-2 py-0.5 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-[11px] font-medium">
                {p}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span>{rumor.total_mentions ?? 0} posts</span>
            <span>{rumor.unique_sources ?? 0} sources</span>
          </div>
          <div className="flex items-center gap-1">
            <div
              className="h-1.5 w-12 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden"
              title={`${score}% confidence`}
            >
              <div
                className={`h-full rounded-full ${
                  score >= 70 ? "bg-emerald-500" : score >= 50 ? "bg-amber-500" : "bg-red-400"
                }`}
                style={{ width: `${Math.min(score, 100)}%` }}
              />
            </div>
            <span className="text-[11px] font-medium text-slate-500 tabular-nums">
              {score}%
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}
