"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/rumors", label: "Rumors", icon: "📰" },
  { href: "/sources", label: "Sources", icon: "👤" },
  { href: "/entities", label: "Entities", icon: "🏷️" },
  { href: "/timeline", label: "Timeline", icon: "📅" },
  { href: "/search", label: "Search", icon: "🔍" },
  { href: "/alerts", label: "Alerts", icon: "🔔" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col border-r border-slate-800">
      <div className="p-6 border-b border-slate-800">
        <Link href="/" className="text-xl font-bold text-cyan-400">
          LeakSight
        </Link>
        <p className="text-xs text-slate-500 mt-1">Tech Leak Intelligence</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              pathname === item.href || pathname.startsWith(item.href + "/")
                ? "bg-cyan-500/20 text-cyan-400"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
