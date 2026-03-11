"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function EntitiesPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["entities"],
    queryFn: () => api.getEntities(undefined, 100),
  });

  const entities = data?.data ?? [];

  if (isLoading) {
    return (
      <div>
        <h1 className="text-2xl font-bold">Entities</h1>
        <div className="mt-4 animate-pulse grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <div key={i} className="h-24 bg-slate-200 dark:bg-slate-800 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Entity Explorer
        </h1>
        <p className="text-slate-500 mt-1">Companies, products, and features extracted from leaks</p>
      </div>

      {entities.length === 0 ? (
        <div className="p-8 glass-card rounded-xl text-center text-slate-500">
          No entities yet. They will appear as posts are analyzed.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {entities.map((entity: any) => (
            <div
              key={`${entity.name}-${entity.type}`}
              className="p-5 glass-card rounded-xl"
            >
              <h3 className="font-semibold text-white">
                {entity.name}
              </h3>
              <span
                className={`inline-block mt-2 px-2 py-0.5 rounded text-xs ${entity.type === "COMPANY"
                    ? "bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200"
                    : entity.type === "PRODUCT"
                      ? "bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200"
                      : "bg-amber-100 dark:bg-amber-900/50 text-amber-800 dark:text-amber-200"
                  }`}
              >
                {entity.type}
              </span>
              <p className="mt-2 text-sm text-slate-500">
                {entity.mention_count ?? 0} mentions
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
