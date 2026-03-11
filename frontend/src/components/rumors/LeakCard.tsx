"use client";

import Link from "next/link";
import StatusBadge from "./StatusBadge";
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
  const score = rumor.confidence ?? (rumor.credibility_score != null ? rumor.credibility_score / 100 : 0);
  const scorePct = Math.round((score || 0) * 100);
  const level = scorePct >= 80 ? "HIGH_CRIT" : scorePct >= 50 ? "MEDIUM_INTEL" : "LOW_RISK";
  const levelColors =
    scorePct >= 80
      ? "bg-red-500/10 text-red-500 border-red-500/20"
      : scorePct >= 50
        ? "bg-orange-500/10 text-orange-500 border-orange-500/20"
        : "bg-accent-lime/10 text-accent-lime border-accent-lime/20";
  const timeAgo = getTimeAgo(rumor.first_seen || rumor.last_seen || "");

  return (
    <div className="p-5 hover:bg-white/[0.03] transition-colors">
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="text-base font-bold text-white">
          <span className="mr-2">{emoji}</span>
          <Link href={`/rumors/${id}`} className="hover:text-accent-lime hover:glow-text transition-colors">
            {rumor.title}
          </Link>
        </h3>
        <span className={`px-2 py-0.5 text-[9px] font-black uppercase rounded border shrink-0 ${levelColors}`}>
          {scorePct}%
        </span>
      </div>
      <div className="flex flex-wrap gap-3 text-[10px] font-black uppercase tracking-widest mb-2">
        <span className="text-slate-500">
          SCORE: <span className="text-accent-lime">{scorePct}%</span>
        </span>
        <span className="text-slate-500">
          SOURCES: <span className="text-white">{rumor.source_count ?? rumor.post_ids?.length ?? 0}</span>
        </span>
        <StatusBadge status={rumor.status} />
        {timeAgo && <span className="text-slate-400">{timeAgo}</span>}
      </div>
      <div className="flex flex-wrap gap-2 mb-2">
        {rumor.entities?.companies?.map((c) => (
          <span key={c} className="px-2 py-0.5 bg-accent-lime/10 text-accent-lime border border-accent-lime/20 text-[10px] font-black uppercase rounded">
            {c}
          </span>
        ))}
        {rumor.entities?.products?.map((p) => (
          <span key={p} className="px-2 py-0.5 bg-red-500/10 text-red-500 border border-red-500/20 text-[10px] font-black uppercase rounded">
            {p}
          </span>
        ))}
        {rumor.entities?.features?.map((f) => (
          <span key={f} className="px-2 py-0.5 bg-orange-500/10 text-orange-500 border border-orange-500/20 text-[10px] font-black uppercase rounded">
            {f}
          </span>
        ))}
      </div>
      {expanded && rumor.summary && (
        <p className="text-slate-400 text-sm mb-3">{rumor.summary}</p>
      )}
      {expanded && rumor.timeline && rumor.timeline.length > 0 && (
        <MiniTimeline events={rumor.timeline} />
      )}
      <div className="flex gap-4 mt-3">
        <Link
          href={`/rumors/${id}`}
          className="text-[10px] font-black text-accent-lime uppercase tracking-widest hover:glow-text transition-all"
        >
          View Full Timeline →
        </Link>
      </div>
    </div>
  );
}
