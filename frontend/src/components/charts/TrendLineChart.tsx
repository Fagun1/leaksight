"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const data = [
  { time: "00:00", mentions: 12, leaks_detected: 3 },
  { time: "04:00", mentions: 8, leaks_detected: 2 },
  { time: "08:00", mentions: 45, leaks_detected: 12 },
  { time: "12:00", mentions: 78, leaks_detected: 23 },
  { time: "16:00", mentions: 92, leaks_detected: 31 },
  { time: "20:00", mentions: 65, leaks_detected: 18 },
  { time: "24:00", mentions: 34, leaks_detected: 9 },
];

export default function TrendLineChart() {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
        Mention Volume (24h)
      </h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="time" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                borderRadius: "8px",
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="mentions"
              stroke="#06b6d4"
              strokeWidth={2}
              dot={false}
              name="Total Mentions"
            />
            <Line
              type="monotone"
              dataKey="leaks_detected"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Leaks Detected"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
