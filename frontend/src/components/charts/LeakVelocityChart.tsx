"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function LeakVelocityChart({ days = 30 }: { days?: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "velocity", days],
    queryFn: () => api.getAnalyticsVelocity(days),
  });
  const chartData = data?.data ?? [];
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 h-[280px] animate-pulse" />
    );
  }
  return (
    <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Leak Velocity</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
          <XAxis dataKey="date" className="text-xs" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="total" stroke="#06b6d4" strokeWidth={2} name="Leaks" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
