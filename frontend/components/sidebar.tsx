"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  PlusCircle,
  Clock,
  Link as LinkIcon,
  Settings,
  Sparkles,
  LogOut,
  CheckSquare,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/", label: "Tạo video", icon: PlusCircle }, // Current page is create
  { href: "/verify", label: "Kiểm duyệt", icon: CheckSquare },
  { href: "/history", label: "Lịch sử", icon: Clock },
  { href: "/channels", label: "Kênh", icon: LinkIcon },
  { href: "/settings", label: "Cài đặt", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 hidden h-screen w-64 flex-col border-r border-white/5 bg-[#050505]/80 backdrop-blur-2xl sm:flex">
      {/* Header */}
      <div className="flex h-20 items-center px-6">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 ring-1 ring-white/20">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">
            MarkX
          </span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-2 px-4 py-6">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-all duration-300",
                isActive
                  ? "bg-white/10 text-white shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]"
                  : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
              )}
            >
              <item.icon
                className={cn(
                  "h-5 w-5 transition-transform duration-300 group-hover:scale-110",
                  isActive ? "text-white" : "text-slate-500 group-hover:text-slate-300"
                )}
              />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-white/5 p-4">
        <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/[0.02] p-3 transition-colors hover:bg-white/[0.04]">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-full bg-gradient-to-br from-indigo-500 to-fuchsia-500" />
            <div className="space-y-0.5">
              <p className="text-sm font-medium text-white">Admin</p>
              <p className="text-xs text-slate-500">Free Plan</p>
            </div>
          </div>
          <button className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-white/10 hover:text-white">
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
