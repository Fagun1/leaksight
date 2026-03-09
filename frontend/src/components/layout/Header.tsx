"use client";

import { useState } from "react";
import Sidebar from "./Sidebar";

export default function Header() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header className="h-14 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 sm:px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Mobile menu button */}
          <button
            type="button"
            className="inline-flex items-center justify-center rounded-md p-2 text-slate-500 hover:text-slate-200 hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-500 md:hidden"
            aria-label="Open navigation"
            onClick={() => setMobileOpen(true)}
          >
            <span className="sr-only">Open navigation</span>
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <h2 className="text-sm font-medium text-slate-600 dark:text-slate-400">
            AI-Powered Tech Leak Intelligence
          </h2>
        </div>
        <div className="hidden sm:flex items-center gap-4">
          <span className="text-xs text-slate-500">Real-time monitoring</span>
        </div>
      </header>

      {/* Mobile sidebar overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 flex md:hidden">
          <div
            className="fixed inset-0 bg-black/40"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative z-50 w-64 max-w-full h-full bg-slate-900">
            <Sidebar />
          </div>
        </div>
      )}
    </>
  );
}
