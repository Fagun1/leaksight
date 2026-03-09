"use client";

export default function Header() {
  return (
    <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-slate-600 dark:text-slate-400">
          AI-Powered Tech Leak Intelligence
        </h2>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-xs text-slate-500">Real-time monitoring</span>
      </div>
    </header>
  );
}
