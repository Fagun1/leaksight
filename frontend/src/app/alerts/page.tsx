"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function AlertsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.getAlerts(),
  });

  const alerts = data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Alert Management
        </h1>
        <p className="text-slate-500 mt-1">Configure notifications for new leaks</p>
      </div>

      {isLoading ? (
        <div className="animate-pulse h-32 bg-slate-200 dark:bg-slate-800 rounded" />
      ) : alerts.length === 0 ? (
        <div className="p-8 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500">
          No alerts configured. Use the API to create alerts.
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert: any) => (
            <div
              key={alert._id}
              className="p-5 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800"
            >
              <h3 className="font-semibold text-slate-900 dark:text-white">
                {alert.name}
              </h3>
              <p className="text-sm text-slate-500 mt-1">
                Status: {alert.status} • Triggered: {alert.triggered_count ?? 0} times
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
