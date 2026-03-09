"use client";

import Link from "next/link";
import StatusBadge from "./StatusBadge";
import CredibilityBadge from "./CredibilityBadge";
import MiniTimeline from "../timeline/MiniTimeline";
import type { Rumor } from "@/types/rumor";

function getTimeAgo(dateStr: string): string {
  if (!dateStr) return "";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays === 0) return "today";
  if (diffDays === 1) return "1d ago";
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
  return `${Math.floor(diffDays / 30)}mo ago`;
}

const CATEGORY_EMOJI: Record<string, string> = {
  hardware_leak: "📱",
  HARDWARE_LEAK: "📱",
  software_leak: "💻",
  SOFTWARE_LEAK: "💻",
  ai_leak: "🤖",
  business_leak: "💼",
  product_announcement: "📢",
};

interface LeakCardProps {
  rumor: Rumor;
  expanded?: boolean;
}

export default function LeakCard({ rumor, expanded = false }: LeakCardProps) {
  const id = rumor.id ?? rumor._id;
  const emoji = CATEGORY_EMOJI[rumor.category] || "📰";
  const score = rumor.confidence ?? rumor.credibility_score != null ? rumor.credibility_score / 100 : 0;
  const timeAgo = getTimeAgo(rumor.first_seen || rumor.last_seen || "");

  return (
    <div className="bg-white dark:bg-slate-900 rounded-lg shadow border border-slate-200 dark:border-slate-800 p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
          <span className="mr-2">{emoji}</span>
          <Link href={`/rumors/${id}`} className="hover:text-cyan-600 dark:hover:text-cyan-400">
            {rumor.title}
          </Link>
        </h3>
        <CredibilityBadge grade={rumor.grade} score={score * 100} />
      </div>
      <div className="flex flex-wrap gap-3 text-sm mb-2">
        <span className="text-slate-500">Score: <strong className="text-cyan-600">{Math.round((score || 0) * 100)}%</strong></span>
        <span className="text-slate-500">Sources: <strong>{rumor.source_count ?? rumor.post_ids?.length ?? 0}</strong></span>
        <StatusBadge status={rumor.status} />
        {timeAgo && <span className="text-slate-400">{timeAgo}</span>}
      </div>
      <div className="flex flex-wrap gap-2 mb-2">
        {rumor.entities?.companies?.map((c) => (
          <span key={c} className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 text-xs rounded-full">{c}</span>
        ))}
        {rumor.entities?.products?.map((p) => (
          <span key={p} className="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-800 dark:text-emerald-200 text-xs rounded-full">{p}</span>
        ))}
        {rumor.entities?.features?.map((f) => (
          <span key={f} className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200 text-xs rounded-full">{f}</span>
        ))}
      </div>
      {expanded && rumor.summary && (
        <p className="text-slate-600 dark:text-slate-300 text-sm mb-3">{rumor.summary}</p>
      )}
      {expanded && rumor.timeline && rumor.timeline.length > 0 && (
        <MiniTimeline events={rumor.timeline} />
      )}
      <div className="flex gap-4 mt-3 text-sm">
        <Link href={`/rumors/${id}`} className="text-cyan-600 hover:text-cyan-700 dark:text-cyan-400">
          View Full Timeline →
        </Link>
      </div>
    </div>
  );
}
