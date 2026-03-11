"use client";

type Status = "emerging" | "developing" | "widespread" | "confirmed" | "denied" | "active" | "expired" | string;

const STATUS_STYLES: Record<string, string> = {
  emerging: "bg-amber-500/10 text-amber-500 border border-amber-500/20",
  developing: "bg-accent-lime/10 text-accent-lime border border-accent-lime/20",
  widespread: "bg-orange-500/10 text-orange-500 border border-orange-500/20",
  confirmed: "bg-accent-lime/10 text-accent-lime border border-accent-lime/20",
  denied: "bg-red-500/10 text-red-500 border border-red-500/20",
  active: "bg-accent-lime/10 text-accent-lime border border-accent-lime/20",
  expired: "bg-slate-500/10 text-slate-400 border border-slate-500/20",
};

export default function StatusBadge({ status }: { status: Status }) {
  const s = (status || "active").toLowerCase();
  const style = STATUS_STYLES[s] || STATUS_STYLES.active;
  return (
    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${style}`}>
      {s}
    </span>
  );
}
