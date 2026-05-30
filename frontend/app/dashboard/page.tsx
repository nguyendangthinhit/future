"use client";

import { useRef, useState, useEffect, useMemo } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import {
  TrendingUp,
  CheckCircle2,
  Loader2,
  XCircle,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [videos, setVideos] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.get("/video/list");
        setVideos(data || []);
      } catch (e) {
        console.error("Dashboard load error", e);
      }
    }
    loadData();
  }, []);

  const stats = useMemo(() => {
    const total = videos.length;
    const success = videos.filter(v => v.status === "done").length;
    const failed = videos.filter(v => v.status === "failed").length;
    const processing = videos.filter(v => v.status === "processing" || v.status === "pending").length;
    const fb = videos.filter(v => v.channel === "facebook").length;
    const tt = videos.filter(v => v.channel === "tiktok").length;
    const fbPct = total ? Math.round((fb / total) * 100) : 0;
    const ttPct = total ? Math.round((tt / total) * 100) : 0;

    const upcoming = videos.filter(v => v.status === "pending" || v.status === "processing").slice(0, 10).map((v, i) => {
      return {
        id: v.id,
        p: v.channel === "tiktok" ? "TikTok" : "Facebook",
        t: v.raw_content ? v.raw_content.substring(0, 30) + "..." : "Video không tên",
        time: v.scheduled_date + " " + (v.scheduled_time || ""),
        color: v.channel === "tiktok" ? "from-rose-400 to-red-600" : "from-blue-400 to-violet-500",
        status: v.status
      };
    });

    return { total, success, failed, processing, fbPct, ttPct, upcoming };
  }, [videos]);

  const scroll = (direction: "left" | "right") => {
    if (scrollRef.current) {
      const scrollAmount = direction === "left" ? -300 : 300;
      scrollRef.current.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
  };

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Dashboard
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Tổng quan hoạt động tự động hoá của bạn.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (Stats + Charts) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Top Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Total Videos */}
            <Card className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div className="space-y-1">
                  <p className="text-sm font-medium text-slate-400">Tổng video</p>
                  <p className="text-5xl font-bold text-white">{stats.total}</p>
                </div>
                <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-emerald-400" />
                </div>
              </div>
              {/* Fake Sparkline */}
              <div className="h-12 flex items-end gap-1 opacity-70">
                {[4, 6, 5, 8, 7, 10, 9, 12, 11, 15, 14, 18, 16, 20].map((h, i) => (
                  <div
                    key={i}
                    className="flex-1 bg-gradient-to-t from-emerald-500/50 to-emerald-400 rounded-t-sm"
                    style={{ height: `${h * 5}%` }}
                  />
                ))}
              </div>
            </Card>

            {/* Minor Stats */}
            <div className="grid grid-rows-2 gap-6">
              <Card className="p-5 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-400 mb-1">Thành công</p>
                  <p className="text-3xl font-bold text-white">{stats.success}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div className="h-8 w-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
                    <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  </div>
                </div>
              </Card>

              <div className="grid grid-cols-2 gap-6">
                <Card className="p-5 flex flex-col justify-center relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-3">
                    <Loader2 className="h-4 w-4 text-amber-500/50 animate-spin" />
                  </div>
                  <p className="text-xs font-medium text-slate-400 mb-1">Đang xử lý</p>
                  <p className="text-2xl font-bold text-white">{stats.processing}</p>
                </Card>
                <Card className="p-5 flex flex-col justify-center relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-3">
                    <XCircle className="h-4 w-4 text-red-500/50" />
                  </div>
                  <p className="text-xs font-medium text-slate-400 mb-1">Thất bại</p>
                  <p className="text-2xl font-bold text-white">{stats.failed}</p>
                </Card>
              </div>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Donut Chart */}
            <Card className="p-6 flex flex-col items-center justify-center">
              <h3 className="w-full text-sm font-medium text-slate-400 mb-6 text-left">
                Video theo kênh
              </h3>
              <div className="relative w-40 h-40 rounded-full bg-[conic-gradient(#3b82f6_62%,#ef4444_0)] flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.15)]">
                <div className="absolute inset-4 rounded-full bg-[#0a0a0a] shadow-[inset_0_2px_10px_rgba(0,0,0,0.5)] flex items-center justify-center">
                   <div className="text-center">
                     <p className="text-xs text-blue-400">{stats.fbPct}% FB</p>
                     <p className="text-xs text-red-400">{stats.ttPct}% TT</p>
                   </div>
                </div>
              </div>
              <div className="w-full flex justify-center gap-6 mt-8">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-blue-500" />
                  <span className="text-xs text-slate-300">Facebook</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <span className="text-xs text-slate-300">TikTok</span>
                </div>
              </div>
            </Card>

            {/* Bar Chart */}
            <Card className="p-6 flex flex-col">
              <h3 className="w-full text-sm font-medium text-slate-400 mb-6 text-left">
                Video theo tuần
              </h3>
              <div className="flex-1 flex items-end justify-between gap-2 h-40">
                {[40, 30, 60, 45, 80, 50, 65].map((h, i) => (
                  <div
                    key={i}
                    className="w-full rounded-t-lg bg-gradient-to-t from-violet-600 to-cyan-400 transition-all duration-300 hover:brightness-125 hover:shadow-[0_0_15px_rgba(34,211,238,0.4)]"
                    style={{ height: `${h}%` }}
                  />
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Right Column (Timeline Sidebar-ish thing) */}
        <div className="lg:col-span-1">
          <Card className="h-full p-6 flex flex-col items-center justify-center border-white/5 opacity-50 relative overflow-hidden">
             <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent" />
             {/* Fake Timeline Scale */}
             <div className="h-full w-px bg-white/10 relative flex flex-col justify-between py-10">
                <div className="absolute -left-12 text-xs text-slate-500">50 min</div>
                <div className="w-2 h-px bg-white/30 -ml-1" />
                <div className="absolute -left-12 top-[33%] text-xs text-slate-500">30 min</div>
                <div className="w-2 h-px bg-white/30 -ml-1 mt-[33%]" />
                <div className="absolute -left-12 top-[66%] text-xs text-slate-500">20 min</div>
                <div className="w-2 h-px bg-white/30 -ml-1 mt-[33%]" />
                <div className="absolute -left-12 bottom-10 text-xs text-slate-500">10 min</div>
                <div className="w-2 h-px bg-white/30 -ml-1 mt-[33%]" />
             </div>
             <div className="absolute bottom-1/4 h-1/2 w-1 bg-gradient-to-b from-cyan-400 to-violet-500 blur-[2px]" />
          </Card>
        </div>
      </div>

      {/* Upcoming Schedule Row */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-semibold tracking-wider text-slate-300 uppercase">
            Upcoming Schedule
          </h3>
          <div className="flex items-center gap-2">
            <button onClick={() => scroll("left")} className="p-1 rounded-full text-slate-500 hover:text-white hover:bg-white/10 transition-colors">
              <ChevronLeft className="h-5 w-5" />
            </button>
            <button onClick={() => scroll("right")} className="p-1 rounded-full text-slate-500 hover:text-white hover:bg-white/10 transition-colors">
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>
        <div ref={scrollRef} className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x snap-mandatory">
          {stats.upcoming.length > 0 ? stats.upcoming.map((v) => (
            <div
              key={v.id}
              className="min-w-[180px] sm:min-w-[200px] flex-shrink-0 group cursor-pointer"
            >
              {/* Thumbnail */}
              <div className={cn("w-full h-24 sm:h-28 rounded-2xl mb-3 bg-gradient-to-br transition-transform duration-300 group-hover:scale-[1.02]", v.color)} />
              {/* Details */}
              <div className="space-y-1.5 px-1">
                <span className={cn(
                  "text-[10px] px-2 py-0.5 rounded-full font-medium border",
                  v.p === "Facebook" ? "bg-blue-500/10 text-blue-400 border-blue-500/20" : "bg-red-500/10 text-red-400 border-red-500/20"
                )}>
                  {v.p}
                </span>
                <p className="text-sm font-medium text-slate-200 truncate">{v.t}</p>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-slate-500">{v.time}</p>
                  <span className="text-[10px] text-amber-500 bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">{v.status}</span>
                </div>
              </div>
            </div>
          )) : (
            <div className="text-sm text-slate-500 italic py-4">Không có lịch trình sắp tới.</div>
          )}
        </div>
      </Card>
    </main>
  );
}
