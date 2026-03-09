import StatsOverview from "@/components/dashboard/StatsOverview";
import TrendingGrid from "@/components/dashboard/TrendingGrid";
import LeakVelocityChart from "@/components/charts/LeakVelocityChart";
import CompanyBarChart from "@/components/charts/CompanyBarChart";
import ScrapeButton from "@/components/dashboard/ScrapeButton";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Dashboard
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm">
            Live tech leak detection across forums and news sites
          </p>
        </div>
        <ScrapeButton />
      </div>

      <StatsOverview />

      <section>
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
          Trending Leaks
        </h2>
        <TrendingGrid />
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CompanyBarChart />
        <LeakVelocityChart days={14} />
      </div>
    </div>
  );
}
