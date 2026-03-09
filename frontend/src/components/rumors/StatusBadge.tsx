"use client";

type Status = "emerging" | "developing" | "widespread" | "confirmed" | "denied" | "active" | "expired" | string;

const STATUS_STYLES: Record<string, string> = {
  emerging: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  developing: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  widespread: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300",
  confirmed: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  denied: "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300",
  active: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300",
  expired: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
};

export default function StatusBadge({ status }: { status: Status }) {
  const s = (status || "active").toLowerCase();
  const style = STATUS_STYLES[s] || STATUS_STYLES.active;
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${style}`}>
      {s}
    </span>
  );
}
