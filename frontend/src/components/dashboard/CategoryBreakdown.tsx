"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

const data = [
  { name: "Hardware", value: 45, color: "#06b6d4" },
  { name: "Software", value: 22, color: "#8b5cf6" },
  { name: "Pricing", value: 8, color: "#f59e0b" },
  { name: "Benchmark", value: 12, color: "#10b981" },
  { name: "Supply Chain", value: 13, color: "#ec4899" },
];

export default function CategoryBreakdown() {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Leak Categories
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
