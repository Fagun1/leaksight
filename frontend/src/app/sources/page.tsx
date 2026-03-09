"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function SourcesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["sources"],
    queryFn: () => api.getSources(50),
  });

  if (isLoading) {
    return (
      <div>
        <h1 className="text-2xl font-bold">Sources</h1>
        <div className="mt-4 animate-pulse space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-20 bg-slate-200 dark:bg-slate-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  const sources = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Source Credibility Rankings
        </h1>
        <p className="text-slate-500 mt-1">Tech leakers and their track records</p>
      </div>

      {sources.length === 0 ? (
        <div className="p-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          No sources yet. Data will appear as posts are processed.
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 dark:bg-slate-800/50">
              <tr>
                <th className="text-left p-4 font-semibold">Source</th>
                <th className="text-left p-4 font-semibold">Platform</th>
                <th className="text-left p-4 font-semibold">Credibility</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((source: any) => (
                <tr
                  key={`${source.platform}-${source.username}`}
                  className="border-t border-slate-200 dark:border-slate-800"
                >
                  <td className="p-4 font-medium">{source.display_name || source.username}</td>
                  <td className="p-4 text-slate-500">{source.platform}</td>
                  <td className="p-4">
                    <span className="text-cyan-600 font-medium">
                      {source.credibility_score ?? 0}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
