"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useScrape } from "@/hooks/useScrape";

export default function Header() {
  const pathname = usePathname();
  const { runScrape, loading } = useScrape();

  return (
    <nav className="bg-black/40 backdrop-blur-2xl border-b border-white/10 px-4 h-12 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="size-7 rounded-sm bg-accent-lime flex items-center justify-center text-obsidian shadow-[0_0_15px_rgba(204,255,0,0.3)]">
            <span className="material-symbols-outlined font-black text-lg">radar</span>
          </div>
          <h1 className="text-white text-sm font-black tracking-[0.2em] uppercase glow-text">LeakSight</h1>
        </div>
        <div className="h-4 w-[1px] bg-white/10 hidden md:block"></div>
        <div className="flex items-center gap-1 group/nav">
          <Link
            className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold transition-all ${pathname === "/dashboard" || pathname === "/" ? "text-accent-lime bg-accent-lime/10 border border-accent-lime/20" : "text-slate-500 hover:text-white font-medium"}`}
            href="/dashboard"
          >
            <span className="material-symbols-outlined text-[18px]">dashboard</span>
            <span>DASHBOARD</span>
          </Link>
          <Link
            className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold transition-all ${pathname === "/rumors" ? "text-accent-lime bg-accent-lime/10 border border-accent-lime/20" : "text-slate-500 hover:text-white font-medium"}`}
            href="/rumors"
          >
            <span className="material-symbols-outlined text-[18px]">forum</span>
            <span className="hidden lg:inline">RUMORS</span>
          </Link>
          <Link
            className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold transition-all ${pathname === "/sources" ? "text-accent-lime bg-accent-lime/10 border border-accent-lime/20" : "text-slate-500 hover:text-white font-medium"}`}
            href="/sources"
          >
            <span className="material-symbols-outlined text-[18px]">database</span>
            <span className="hidden lg:inline">SOURCES</span>
          </Link>
          <Link
            className={`flex items-center gap-2 px-3 py-1 rounded text-xs font-bold transition-all ${pathname === "/entities" ? "text-accent-lime bg-accent-lime/10 border border-accent-lime/20" : "text-slate-500 hover:text-white font-medium"}`}
            href="/entities"
          >
            <span className="material-symbols-outlined text-[18px]">fingerprint</span>
            <span className="hidden lg:inline">ENTITIES</span>
          </Link>
          <button className="flex items-center gap-2 px-3 py-1 rounded text-slate-500 hover:text-white text-xs font-medium transition-all">
            <span className="material-symbols-outlined text-[18px]">search</span>
          </button>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-[10px] font-bold text-accent-lime/70 tracking-tighter">
          <span className="size-1.5 rounded-full bg-accent-lime animate-pulse"></span>
          LIVE_OPS
        </div>
        <button
          onClick={() => runScrape()}
          disabled={loading}
          className="bg-accent-lime/10 border border-accent-lime/30 text-accent-lime px-3 py-1 rounded text-[10px] font-black uppercase tracking-widest hover:bg-accent-lime hover:text-obsidian transition-all disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:bg-accent-lime/10 disabled:hover:text-accent-lime"
        >
          {loading ? "SCRAPING..." : "SCRAPE_CORE"}
        </button>
      </div>
    </nav>
  );
}
