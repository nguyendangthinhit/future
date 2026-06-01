"use client";

import { useState, useMemo, useEffect } from "react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  X,
  RefreshCw,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";

type Status = "success" | "processing" | "failed";

interface VideoEvent {
  id: string;
  type: string;
  channel: string;
  title: string;
  time: string;
  status: Status;
  dateIndex: number; // 0 to 6 (T2 to CN)
}

// We will load this dynamically
// const FAKE_EVENTS = ...

const FILTERS = ["All", "Facebook", "TikTok", "Thành công", "Thất bại", "Đang xử lý"];

export default function HistoryPage() {
  const [selectedEvent, setSelectedEvent] = useState<VideoEvent | null>(null);
  const [activeFilter, setActiveFilter] = useState("All");
  const [events, setEvents] = useState<VideoEvent[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await api.get("/video/list");
        const mapped = data.map((item: any) => {
          let status: Status = "processing";
          if (item.status === "done") status = "success";
          if (item.status === "failed") status = "failed";
          
          let dateIndex = 0;
          if (item.scheduled_date) {
            const d = new Date(item.scheduled_date);
            dateIndex = d.getDay() === 0 ? 6 : d.getDay() - 1; // 0=Mon..6=Sun
          }
          
          return {
            id: item.id,
            type: item.video_type === "ads" ? "Quảng cáo" : "Giải trí",
            channel: item.channel === "tiktok" ? "TikTok" : "Facebook",
            title: item.raw_content ? item.raw_content.substring(0, 50) + "..." : "Video không tên",
            time: item.scheduled_time || "00:00",
            status,
            dateIndex,
            rawPrompt: item.final_prompt,
            videoUrl: item.video_url
          };
        });
        setEvents(mapped);
      } catch (e) {
        console.error("Failed to load videos:", e);
      }
    }
    loadData();
  }, []);

  const filteredEvents = useMemo(() => {
    return events.filter((ev) => {
      if (activeFilter === "All") return true;
      if (activeFilter === "Facebook" && ev.channel !== "Facebook") return false;
      if (activeFilter === "TikTok" && ev.channel !== "TikTok") return false;
      if (activeFilter === "Thành công" && ev.status !== "success") return false;
      if (activeFilter === "Thất bại" && ev.status !== "failed") return false;
      if (activeFilter === "Đang xử lý" && ev.status !== "processing") return false;
      return true;
    });
  }, [activeFilter, events]);

  const getStatusColor = (status: Status) => {
    switch (status) {
      case "success": return "emerald";
      case "processing": return "amber";
      case "failed": return "red";
    }
  };

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-7xl mx-auto flex flex-col h-screen">
      {/* Header */}
      <header className="flex items-center justify-between mb-8 shrink-0">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Lịch sử video
        </h1>
        <Link
          href="/"
          className="inline-flex items-center gap-2 h-10 px-5 rounded-full bg-white text-black font-semibold text-sm transition-transform hover:scale-105 active:scale-95"
        >
          <Plus className="h-4 w-4" />
          Tạo video
        </Link>
      </header>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-white font-medium text-lg">
            <button className="p-1.5 rounded-lg hover:bg-white/10 transition-colors">
              <ChevronLeft className="h-5 w-5" />
            </button>
            <span className="min-w-[120px] text-center">Tháng 5, 2026</span>
            <button className="p-1.5 rounded-lg hover:bg-white/10 transition-colors">
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
          <button className="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-slate-300 hover:bg-white/10 transition-colors">
            Hôm nay
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={cn(
                "px-4 py-1.5 rounded-full text-xs font-medium border transition-all duration-300",
                activeFilter === f
                  ? "bg-white text-black border-white shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                  : "bg-white/[0.03] text-slate-400 border-white/10 hover:border-white/30"
              )}
            >
              {f === "Facebook" && <span className="text-blue-400 mr-1.5">f</span>}
              {f === "TikTok" && <span className="text-red-400 mr-1.5">♪</span>}
              {f === "Thành công" && <span className="text-emerald-400 mr-1.5">●</span>}
              {f === "Thất bại" && <span className="text-red-400 mr-1.5">●</span>}
              {f === "Đang xử lý" && <span className="text-amber-400 mr-1.5">●</span>}
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="flex-1 flex flex-col rounded-2xl border border-white/10 bg-[#050505]/50 overflow-hidden backdrop-blur-xl">
        {/* Days Header */}
        <div className="grid grid-cols-7 border-b border-white/10 bg-white/[0.02]">
          {["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map((day, i) => (
            <div key={day} className="py-4 text-center border-r border-white/10 last:border-0">
              <span className="text-sm font-medium text-slate-400">{day}</span>
            </div>
          ))}
        </div>
        {/* Dates Header */}
        <div className="grid grid-cols-7 border-b border-white/10 bg-white/[0.01]">
          {[25, 26, 27, 28, 29, 30, 31].map((date, i) => (
            <div key={date} className="py-4 flex justify-center border-r border-white/10 last:border-0">
              <span
                className={cn(
                  "flex h-8 w-8 items-center justify-center rounded-full text-sm font-semibold",
                  i === 0
                    ? "bg-white text-black shadow-[0_0_15px_rgba(255,255,255,0.3)]"
                    : "text-slate-300"
                )}
              >
                {date}
              </span>
            </div>
          ))}
        </div>

        {/* Grid Area */}
        <div className="grid grid-cols-7 flex-1 min-h-[500px]">
          {[0, 1, 2, 3, 4, 5, 6].map((colIndex) => (
            <div key={colIndex} className="border-r border-white/5 last:border-0 p-2 space-y-2 relative group/col hover:bg-white/[0.01] transition-colors">
              <AnimatePresence mode="popLayout">
                {filteredEvents.filter((e) => e.dateIndex === colIndex).map((ev) => (
                  <motion.button
                    layout
                    initial={{ opacity: 0, scale: 0.9, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: -10 }}
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    key={ev.id}
                    onClick={() => setSelectedEvent(ev)}
                    className="w-full text-left relative overflow-hidden rounded-xl bg-[#0a0a0a] border border-white/5 p-3 hover:border-white/20 transition-all duration-300 group/card hover:shadow-[0_0_20px_rgba(255,255,255,0.05)] active:scale-[0.98]"
                  >
                    {/* Left Glow Border */}
                    <div className={cn(
                      "absolute top-0 bottom-0 left-0 w-[3px]",
                      ev.status === "success" && "bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]",
                      ev.status === "processing" && "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]",
                      ev.status === "failed" && "bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]"
                    )} />
                    <div className={cn(
                      "absolute inset-0 opacity-10 bg-gradient-to-r to-transparent",
                      ev.status === "success" && "from-emerald-500",
                      ev.status === "processing" && "from-amber-500",
                      ev.status === "failed" && "from-red-500"
                    )} />

                    <div className="relative z-10 space-y-1 pl-1">
                      <p className="text-[10px] text-slate-400 font-medium">
                        {ev.type} • {ev.channel}
                      </p>
                      <p className="text-xs font-semibold text-slate-200 line-clamp-2 leading-tight">
                        {ev.title}
                      </p>
                      <p className={cn(
                        "text-[10px] font-medium pt-1",
                        ev.status === "success" && "text-emerald-400",
                        ev.status === "processing" && "text-amber-400",
                        ev.status === "failed" && "text-red-400"
                      )}>
                        {ev.time}
                      </p>
                    </div>
                  </motion.button>
                ))}
              </AnimatePresence>
            </div>
          ))}
        </div>
      </div>

      {/* Side Panel Overlay & Drawer */}
      <AnimatePresence>
        {selectedEvent && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedEvent(null)}
              className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm"
            />
            {/* Drawer */}
            <motion.div
              initial={{ x: "100%", opacity: 0.5 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: "100%", opacity: 0.5 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="fixed inset-y-0 right-0 z-50 w-full sm:w-[400px] border-l border-white/10 bg-[#080808]/95 p-6 shadow-2xl backdrop-blur-3xl overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-8">
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="p-2 -ml-2 rounded-full text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="p-2 -mr-2 rounded-full text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="space-y-8">
                {/* Video Info */}
                <div>
                  <h3 className="text-lg font-bold text-white mb-4">Video Kết Quả</h3>
                  {/* @ts-ignore */}
                  {selectedEvent.videoUrl ? (
                    <video 
                      src={(selectedEvent as any).videoUrl} 
                      controls 
                      autoPlay
                      loop
                      className="w-full rounded-2xl border border-white/10 bg-black/50"
                      style={{ maxHeight: "60vh" }}
                    />
                  ) : (
                    <p className="text-sm text-slate-400 leading-relaxed italic">
                      Video đang được render hoặc chưa có video...
                    </p>
                  )}
                </div>

                {/* Status */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3">Current status</h3>
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium">
                    <CheckCircle2 className="h-4 w-4" />
                    Thành công
                  </div>
                </div>

                {/* Prompt */}
                <div>
                  <h3 className="text-sm font-semibold text-slate-300 mb-3">Prompt</h3>
                  <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4">
                    <p className="text-sm text-slate-400 leading-relaxed font-mono">
                      {/* @ts-ignore */}
                      {selectedEvent.rawPrompt || "Chưa có prompt."}
                    </p>
                  </div>
                  <button className="w-full mt-4 flex items-center justify-center gap-2 h-11 rounded-full bg-white text-black font-semibold text-sm hover:scale-[1.02] active:scale-[0.98] transition-transform">
                    <RefreshCw className="h-4 w-4" />
                    Regenerate
                  </button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </main>
  );
}
