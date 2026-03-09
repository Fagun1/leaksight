"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function CompanyBarChart() {
  const { data, isLoading } = useQuery({
    queryKey: ["analytics", "company-distribution"],
    queryFn: () => api.getCompanyDistribution(),
  });
  const chartData = data?.data ?? [];
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 h-[280px] animate-pulse" />
    );
  }
  return (
    <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">Leaks by Company</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-700" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="company" width={70} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="count" fill="#06b6d4" name="Leaks" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
