"use client";

import { useRouter } from "next/navigation";
import { useTrending } from "@/hooks/useTrending";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const { data: trendingData, isLoading: trendingLoading } = useTrending(20);
  const { data: velocityData } = useQuery({
    queryKey: ["analytics", "velocity", 14],
    queryFn: () => api.getAnalyticsVelocity(14),
  });
  const { data: companyData } = useQuery({
    queryKey: ["companyDist"],
    queryFn: () => api.getCompanyDistribution(),
  });

  const stats = trendingData?.stats ?? {};
  const trending = trendingData?.trending ?? [];
  const velocityPoints = velocityData?.data ?? [];
  const companies = companyData?.data ?? [];

  // Compute max velocity for chart scaling
  const maxVelocity = Math.max(...velocityPoints.map((p: any) => p.total), 1);

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-black text-accent-lime uppercase tracking-[0.3em] mb-1">
            <span className="material-symbols-outlined text-sm">security</span>
            Night Ops Analyst Interface
          </div>
          <h2 className="text-4xl font-black text-white tracking-tighter">SURVEILLANCE_TERMINAL</h2>
        </div>
      </div>

      {/* Stat Cards - connected to API */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-4 rounded-xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-24 h-24 bg-accent-lime/5 blur-3xl rounded-full -translate-y-1/2 translate-x-1/2"></div>
          <div className="flex justify-between items-center mb-4">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Leaks Detected</p>
            <span className="material-symbols-outlined text-accent-lime/40 text-[18px]">release_alert</span>
          </div>
          <div className="flex items-end justify-between">
            <h3 className="text-3xl font-black text-white glow-text">
              {trendingLoading ? "—" : (stats.leaks_total ?? 0).toLocaleString()}
            </h3>
            <span className="text-accent-lime text-[10px] font-black flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">trending_up</span> LIVE
            </span>
          </div>
          <div className="h-[2px] w-full bg-white/5 mt-4 overflow-hidden">
            <div className="h-full bg-accent-lime shadow-[0_0_8px_#ccff00] w-[65%]"></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl relative overflow-hidden">
          <div className="flex justify-between items-center mb-4">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Active Rumors</p>
            <span className="material-symbols-outlined text-slate-600 text-[18px]">forum</span>
          </div>
          <div className="flex items-end justify-between">
            <h3 className="text-3xl font-black text-white glow-text">
              {trendingLoading ? "—" : (stats.total_rumors ?? 0).toLocaleString()}
            </h3>
            <span className="text-slate-500 text-[10px] font-black uppercase">Monitoring</span>
          </div>
          <div className="h-[2px] w-full bg-white/5 mt-4 overflow-hidden">
            <div className="h-full bg-white/20 w-[40%]"></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl relative overflow-hidden border-l-2 border-l-red-500/50">
          <div className="flex justify-between items-center mb-4">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Total Posts</p>
            <span className="material-symbols-outlined text-red-500 text-[18px]">description</span>
          </div>
          <div className="flex items-end justify-between">
            <h3 className="text-3xl font-black text-white glow-text">
              {trendingLoading ? "—" : (stats.total_posts ?? 0).toLocaleString()}
            </h3>
            <span className="text-red-500 text-[10px] font-black bg-red-500/10 px-1.5 py-0.5 rounded">INDEXED</span>
          </div>
          <div className="h-[2px] w-full bg-white/5 mt-4 overflow-hidden">
            <div className="h-full bg-red-500/50 w-[80%] shadow-[0_0_8px_rgba(239,68,68,0.5)]"></div>
          </div>
        </div>

        <div className="glass-card p-4 rounded-xl relative overflow-hidden border-l-2 border-l-accent-lime">
          <div className="flex justify-between items-center mb-4">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest text-accent-lime">Avg Confidence</p>
            <span className="material-symbols-outlined text-accent-lime text-[18px]">show_chart</span>
          </div>
          <div className="flex items-end justify-between">
            <h3 className="text-3xl font-black text-accent-lime glow-text">
              {trendingLoading ? "—" : `${stats.avg_confidence ?? 0}%`}
            </h3>
            <span className="text-accent-lime text-[10px] font-black uppercase">Score</span>
          </div>
          <div className="h-[2px] w-full bg-accent-lime/10 mt-4 overflow-hidden">
            <div className="h-full bg-accent-lime w-full animate-pulse shadow-[0_0_8px_#ccff00]"></div>
          </div>
        </div>
      </div>

      {/* Main Grid: Trending + Entity Watchlist */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
        {/* Trending Intel Table */}
        <div className="xl:col-span-3 glass-card rounded-xl overflow-hidden flex flex-col">
          <div className="px-5 py-3 border-b border-white/10 flex justify-between items-center bg-black/20">
            <h3 className="font-black text-white text-[10px] uppercase tracking-[0.2em] flex items-center gap-2">
              <span className="material-symbols-outlined text-accent-lime text-lg">local_fire_department</span>
              TRENDING_INTEL
            </h3>
            <div className="flex items-center gap-4">
              <button className="text-[10px] font-black text-accent-lime hover:glow-text">EXPORT_DATA</button>
            </div>
          </div>
          <div className="overflow-x-auto custom-scrollbar flex-1">
            {trendingLoading ? (
              <div className="p-6 space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-12 bg-white/5 rounded animate-pulse" />
                ))}
              </div>
            ) : trending.length === 0 ? (
              <div className="p-10 text-center text-slate-500 text-sm">
                No leaks detected yet. Click <strong className="text-accent-lime">SCRAPE_CORE</strong> above to start fetching.
              </div>
            ) : (
              <table className="w-full text-left">
                <thead className="bg-black/40 text-slate-500 text-[9px] font-black uppercase tracking-[0.2em]">
                  <tr>
                    <th className="px-6 py-3">#</th>
                    <th className="px-6 py-3">INTEL_RECAP</th>
                    <th className="px-6 py-3">CATEGORY</th>
                    <th className="px-6 py-3">CONFIDENCE</th>
                    <th className="px-6 py-3">SOURCES</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {trending.map((rumor: any, i: number) => {
                    const confidence = rumor.avg_confidence ?? rumor.confidence ?? 0;
                    const level = confidence >= 80 ? "HIGH_CRIT" : confidence >= 50 ? "MEDIUM_INTEL" : "LOW_RISK";
                    const levelColors = confidence >= 80
                      ? "bg-red-500/10 text-red-500 border-red-500/20"
                      : confidence >= 50
                        ? "bg-orange-500/10 text-orange-500 border-orange-500/20"
                        : "bg-accent-lime/10 text-accent-lime border-accent-lime/20";
                    const rumorId = rumor.rumor_id ?? rumor._id ?? rumor.id;
                    return (
                      <tr
                        key={rumor.rumor_id || i}
                        onClick={() => rumorId && router.push(`/rumors/${rumorId}`)}
                        className="glass-row group cursor-pointer hover:bg-white/[0.06] transition-colors"
                      >
                        <td className="px-6 py-4">
                          <span className="text-accent-lime/60 text-xs font-mono">{String(i + 1).padStart(2, "0")}</span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="max-w-md">
                            <p className="text-xs font-bold text-slate-200 truncate uppercase">{rumor.title || rumor.summary || "Untitled Intel"}</p>
                            <p className="text-slate-500 text-[10px] truncate tracking-tight">{rumor.companies?.join(" / ") || rumor.category || "UNCLASSIFIED"}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-accent-lime/80 text-[10px] font-mono tracking-widest uppercase">{rumor.category || "N/A"}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-0.5 text-[9px] font-black uppercase rounded border ${levelColors}`}>{level}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-slate-400 text-xs font-mono">{rumor.source_count ?? rumor.post_count ?? 0}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Entity Watchlist - from company distribution API */}
        <div className="glass-card p-5 rounded-xl flex flex-col h-full border border-white/10">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-black text-white text-[10px] uppercase tracking-[0.2em]">ENTITY_WATCHLIST</h3>
          </div>
          <div className="space-y-6 flex-1">
            {companies.length === 0 ? (
              <p className="text-slate-500 text-xs text-center">No entity data yet.</p>
            ) : (
              companies.slice(0, 6).map((company: any, i: number) => {
                const maxCount = Math.max(...companies.map((c: any) => c.count), 1);
                const pct = Math.round((company.count / maxCount) * 100);
                return (
                  <div key={company.company || i} className="space-y-2">
                    <div className="flex justify-between text-[10px] font-black uppercase tracking-widest">
                      <span className={i === 0 ? "text-white" : "text-slate-400"}>{company.company}</span>
                      <span className={i === 0 ? "text-accent-lime glow-text" : "text-slate-300"}>{company.count}</span>
                    </div>
                    <div className="w-full bg-white/5 h-[3px] rounded-full overflow-hidden">
                      <div
                        className={i === 0 ? "bg-accent-lime h-full shadow-[0_0_8px_#ccff00]" : `bg-white/${Math.max(10, 40 - i * 10)} h-full`}
                        style={{ width: `${pct}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Velocity Chart - from velocity API */}
        <div className="xl:col-span-4 glass-card p-5 rounded-xl flex flex-col min-h-[280px]">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="font-black text-white text-[10px] uppercase tracking-[0.2em]">INTEL_VELOCITY_MAP (14D)</h3>
              <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mt-1">REAL-TIME DATA STREAM FROM CORE_v2.4</p>
            </div>
            <div className="flex gap-4 items-center">
              <div className="flex items-center gap-2">
                <div className="size-2 rounded-full bg-accent-lime shadow-[0_0_8px_#ccff00]"></div>
                <span className="text-[9px] text-white font-black uppercase tracking-widest">PEAK_ALERT</span>
              </div>
              <button className="material-symbols-outlined text-slate-500 hover:text-accent-lime text-[20px] transition-colors">fullscreen</button>
            </div>
          </div>
          <div className="flex-1 flex items-end gap-2 px-2 pb-2">
            {velocityPoints.length === 0 ? (
              <p className="text-slate-500 text-xs text-center w-full py-8">No velocity data yet. Scrape some data first.</p>
            ) : (
              velocityPoints.map((point: any, i: number) => {
                const heightPct = Math.max(5, (point.total / maxVelocity) * 100);
                const isHigh = heightPct > 60;
                return (
                  <div
                    key={point.date || i}
                    className={`flex-1 rounded-sm transition-all cursor-crosshair ${isHigh ? "velocity-bar neon-border" : "bg-white/5 hover:bg-accent-lime/10"}`}
                    style={{ height: `${heightPct}%` }}
                    title={`${point.date}: ${point.total} leaks`}
                  ></div>
                );
              })
            )}
          </div>
          {velocityPoints.length > 0 && (
            <div className="flex justify-between text-[8px] text-slate-600 font-black uppercase tracking-[0.3em] mt-6 border-t border-white/5 pt-4">
              <span>{velocityPoints[0]?.date}</span>
              <span>{velocityPoints[Math.floor(velocityPoints.length / 2)]?.date}</span>
              <span>{velocityPoints[velocityPoints.length - 1]?.date}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
