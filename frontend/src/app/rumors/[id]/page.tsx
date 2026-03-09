"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import StatusBadge from "@/components/rumors/StatusBadge";
import CredibilityBadge from "@/components/rumors/CredibilityBadge";

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
      <div className="space-y-4">
        <div className="h-8 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
        <div className="h-64 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>
    );
  }

  if (error || !rumor) {
    return (
      <div>
        <Link href="/rumors" className="text-cyan-600 hover:underline mb-4 inline-block">
          ← Back to Rumors
        </Link>
        <p className="text-amber-600">Rumor not found.</p>
      </div>
    );
  }

  const timeline = rumor.timeline ?? [];

  return (
    <div className="space-y-6">
      <Link href="/rumors" className="text-cyan-600 hover:underline inline-block">
        ← Back to Rumors
      </Link>

      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
        <div className="flex justify-between items-start mb-4 flex-wrap gap-2">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            {rumor.title}
          </h1>
          <div className="flex gap-2 items-center">
            <CredibilityBadge grade={rumor.grade} score={rumor.credibility_score} />
            <StatusBadge status={rumor.status ?? "active"} />
          </div>
        </div>

        {rumor.summary && (
          <p className="text-slate-600 dark:text-slate-400 mb-4">{rumor.summary}</p>
        )}

        <div className="flex flex-wrap gap-2 mb-4">
          {rumor.entities?.companies?.map((c: string) => (
            <span
              key={c}
              className="px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded text-sm"
            >
              {c}
            </span>
          ))}
          {rumor.entities?.products?.map((p: string) => (
            <span
              key={p}
              className="px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200 rounded text-sm"
            >
              {p}
            </span>
          ))}
        </div>

        {timeline.length > 0 && (
          <div className="mb-6">
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3">Timeline</h3>
            <ul className="space-y-2">
              {timeline.map((e: { type?: string; date?: string; description?: string; source?: string }, i: number) => (
                <li key={i} className="flex gap-3 text-sm">
                  <span className="text-slate-500 shrink-0">{(e.date ?? "").slice(0, 10)}</span>
                  <span className="font-medium capitalize text-slate-700 dark:text-slate-300">{e.type?.replace(/_/g, " ")}</span>
                  <span className="text-slate-600 dark:text-slate-400">{e.description ?? e.source ?? ""}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {rumor.posts && rumor.posts.length > 0 && (
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white mb-3">
              Related Posts
            </h3>
            <div className="space-y-2">
              {rumor.posts.map((post: { id?: string; _id?: string; cleaned_content?: string; content?: string; source_platform?: string; author_username?: string; source_url?: string }) => (
                <div
                  key={post.id ?? post._id}
                  className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg"
                >
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    {post.cleaned_content || post.content}
                  </p>
                  <div className="flex gap-2 mt-2 text-xs text-slate-500">
                    <span>{post.source_platform}</span>
                    <span>•</span>
                    <span>{post.author_username}</span>
                    {post.source_url && (
                      <a
                        href={post.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-600 hover:underline"
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
