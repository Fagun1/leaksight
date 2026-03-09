"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["rumors", "search", submitted],
    queryFn: () => api.getRumors({ per_page: 50 }),
    enabled: submitted.length > 0,
  });
  const rumors = (data?.data ?? []).filter((r: { title?: string; summary?: string; entities?: { companies?: string[]; products?: string[] } }) => {
    if (!submitted) return true;
    const q = submitted.toLowerCase();
    return (
      (r.title || "").toLowerCase().includes(q) ||
      (r.summary || "").toLowerCase().includes(q) ||
      (r.entities?.companies ?? []).some((c: string) => c.toLowerCase().includes(q)) ||
      (r.entities?.products ?? []).some((p: string) => p.toLowerCase().includes(q))
    );
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Search</h1>
      <div className="flex gap-2">
        <input
          type="search"
          placeholder="Search rumors, products, companies..."
          className="flex-1 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && setSubmitted(query)}
        />
        <button
          type="button"
          onClick={() => setSubmitted(query)}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700"
        >
          Search
        </button>
      </div>
      {submitted && (
        <p className="text-slate-500 dark:text-slate-400">
          Results for &quot;{submitted}&quot;: {rumors.length} rumor(s)
        </p>
      )}
      {isLoading && submitted ? (
        <div className="animate-pulse space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-slate-200 dark:bg-slate-800 rounded" />
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {rumors.map((rumor: { _id: string; id?: string; title: string; summary?: string; credibility_score?: number; entities?: { companies?: string[] } }) => (
            <Link
              key={rumor.id ?? rumor._id}
              href={`/rumors/${rumor.id ?? rumor._id}`}
              className="block p-4 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 hover:shadow-md"
            >
              <h3 className="font-semibold text-slate-900 dark:text-white">{rumor.title}</h3>
              {rumor.summary && <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">{rumor.summary}</p>}
              <div className="flex gap-2 mt-2 text-xs">
                <span className="text-cyan-600">{rumor.credibility_score ?? 0}%</span>
                {(rumor.entities?.companies ?? []).slice(0, 3).map((c: string) => (
                  <span key={c} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded">{c}</span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
