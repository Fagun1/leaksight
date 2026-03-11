"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import StatusBadge from "@/components/rumors/StatusBadge";

export default function RumorDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: rumor, isLoading, error } = useQuery({
    queryKey: ["rumor", id],
    queryFn: () => api.getRumor(id),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="max-w-[1600px] mx-auto space-y-6">
        <div className="h-8 w-48 bg-white/5 rounded animate-pulse" />
        <div className="glass-card rounded-xl p-6">
          <div className="h-64 bg-white/5 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  if (error || !rumor) {
    return (
      <div className="max-w-[1600px] mx-auto space-y-6">
        <Link
          href="/rumors"
          className="inline-flex items-center gap-2 text-accent-lime text-[10px] font-black uppercase tracking-widest hover:glow-text transition-all"
        >
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Back to Rumors
        </Link>
        <div className="glass-card rounded-xl p-8 text-center">
          <p className="text-amber-500">Rumor not found.</p>
        </div>
      </div>
    );
  }

  const timeline = rumor.timeline ?? [];
  const scorePct = rumor.credibility_score ?? 0;
  const level = scorePct >= 80 ? "HIGH_CRIT" : scorePct >= 50 ? "MEDIUM_INTEL" : "LOW_RISK";
  const levelColors =
    scorePct >= 80
      ? "bg-red-500/10 text-red-500 border-red-500/20"
      : scorePct >= 50
        ? "bg-orange-500/10 text-orange-500 border-orange-500/20"
        : "bg-accent-lime/10 text-accent-lime border-accent-lime/20";

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <Link
        href="/rumors"
        className="inline-flex items-center gap-2 text-accent-lime text-[10px] font-black uppercase tracking-widest hover:glow-text transition-all"
      >
        <span className="material-symbols-outlined text-[18px]">arrow_back</span>
        Back to Rumors
      </Link>

      <div className="glass-card rounded-xl p-6">
        <div className="flex justify-between items-start mb-4 flex-wrap gap-2">
          <h1 className="text-2xl font-black text-white glow-text tracking-tight">
            {rumor.title}
          </h1>
          <div className="flex gap-2 items-center">
            <span className={`px-2 py-0.5 text-[9px] font-black uppercase rounded border ${levelColors}`}>
              {Math.round(scorePct)}%
            </span>
            <StatusBadge status={rumor.status ?? "active"} />
          </div>
        </div>

        {rumor.summary && (
          <p className="text-slate-400 mb-4">{rumor.summary}</p>
        )}

        <div className="flex flex-wrap gap-2 mb-6">
          {rumor.entities?.companies?.map((c: string) => (
            <span
              key={c}
              className="px-2 py-0.5 bg-accent-lime/10 text-accent-lime border border-accent-lime/20 text-[10px] font-black uppercase rounded"
            >
              {c}
            </span>
          ))}
          {rumor.entities?.products?.map((p: string) => (
            <span
              key={p}
              className="px-2 py-0.5 bg-red-500/10 text-red-500 border border-red-500/20 text-[10px] font-black uppercase rounded"
            >
              {p}
            </span>
          ))}
          {rumor.entities?.features?.map((f: string) => (
            <span
              key={f}
              className="px-2 py-0.5 bg-orange-500/10 text-orange-500 border border-orange-500/20 text-[10px] font-black uppercase rounded"
            >
              {f}
            </span>
          ))}
        </div>

        {timeline.length > 0 && (
          <div className="mb-6">
            <h3 className="font-black text-white text-[10px] uppercase tracking-[0.2em] mb-3">TIMELINE</h3>
            <ul className="space-y-0 divide-y divide-white/5">
              {timeline.map((e: { type?: string; date?: string; description?: string; source?: string }, i: number) => (
                <li key={i} className="flex gap-3 py-3 text-sm glass-row">
                  <span className="text-slate-500 shrink-0 text-[10px] font-mono">{(e.date ?? "").slice(0, 10)}</span>
                  <span className="font-bold capitalize text-slate-300 text-[10px] uppercase tracking-widest shrink-0">
                    {e.type?.replace(/_/g, " ")}
                  </span>
                  <span className="text-slate-400">{e.description ?? e.source ?? ""}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {rumor.posts && rumor.posts.length > 0 && (
          <div>
            <h3 className="font-black text-white text-[10px] uppercase tracking-[0.2em] mb-3">
              RELATED_POSTS
            </h3>
            <div className="space-y-3">
              {rumor.posts.map((post: { id?: string; _id?: string; cleaned_content?: string; content?: string; source_platform?: string; author_username?: string; source_url?: string }) => (
                <div
                  key={post.id ?? post._id}
                  className="p-4 bg-white/5 rounded-lg border border-white/10"
                >
                  <p className="text-sm text-slate-300">
                    {post.cleaned_content || post.content}
                  </p>
                  <div className="flex gap-2 mt-2 text-[10px] text-slate-500 font-black uppercase tracking-widest">
                    <span>{post.source_platform}</span>
                    <span>•</span>
                    <span>{post.author_username}</span>
                    {post.source_url && (
                      <a
                        href={post.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-accent-lime hover:glow-text transition-all"
                      >
                        View source
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
