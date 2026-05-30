"use client";

import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Facebook, Music2, CheckCircle2, AlertCircle, Plus, Unplug } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { motion } from "framer-motion";

interface ChannelData {
  id: string;
  platform: "facebook" | "tiktok";
  name: string;
  status: "connected" | "disconnected" | "expired";
  avatar: string;
}

const INITIAL_CHANNELS: ChannelData[] = [
  {
    id: "1",
    platform: "facebook",
    name: "MarkX Official Fanpage",
    status: "connected",
    avatar: "M",
  },
  {
    id: "2",
    platform: "tiktok",
    name: "@markx.ai",
    status: "expired",
    avatar: "MX",
  }
];

export default function ChannelsPage() {
  const [channels, setChannels] = useState<ChannelData[]>(INITIAL_CHANNELS);

  const toggleStatus = (id: string) => {
    setChannels(prev => prev.map(c => {
      if (c.id === id) {
        return {
          ...c,
          status: c.status === "connected" ? "disconnected" : "connected"
        };
      }
      return c;
    }));
  };

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-5xl mx-auto space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-3xl font-bold tracking-tight text-white">Quản lý kênh</h1>
          <p className="text-slate-400">Kết nối và quản lý các tài khoản mạng xã hội của bạn.</p>
        </div>
        <Button className="group active:scale-[0.98] transition-all shrink-0">
          <Plus className="mr-2 h-4 w-4" /> Kết nối kênh mới
        </Button>
      </div>

      {/* Grid Archetype: The Asymmetrical Bento / Cards */}
      <div className="grid gap-6 sm:grid-cols-2">
        {channels.map((channel, i) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
            key={channel.id}
          >
            {/* Double-Bezel outer shell */}
            <div className="rounded-[2rem] bg-white/[0.02] border border-white/5 p-2 transition-all hover:bg-white/[0.04]">
              {/* Inner core */}
              <div className="relative overflow-hidden rounded-[calc(2rem-0.5rem)] bg-[#0a0a0a] shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] p-6 flex flex-col h-full min-h-[200px] justify-between group/card">
                {/* Glow effect based on status */}
                <div className={cn(
                  "absolute inset-0 opacity-[0.03] transition-all group-hover/card:opacity-10",
                  channel.status === "connected" ? "bg-emerald-500" : 
                  channel.status === "expired" ? "bg-rose-500" : "bg-slate-500"
                )} />

                <div className="relative z-10 flex items-start justify-between">
                  <div className="flex items-center gap-4">
                    <div className={cn(
                      "flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-bold shadow-lg",
                      channel.platform === "facebook" ? "bg-blue-600/20 text-blue-500" : "bg-slate-800 text-slate-200"
                    )}>
                      {channel.platform === "facebook" ? <Facebook className="h-6 w-6" /> : <Music2 className="h-6 w-6" />}
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-100 text-lg">{channel.name}</h3>
                      <div className="flex items-center gap-1.5 mt-1">
                        {channel.status === "connected" && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
                        {channel.status === "expired" && <AlertCircle className="h-3.5 w-3.5 text-rose-400" />}
                        {channel.status === "disconnected" && <Unplug className="h-3.5 w-3.5 text-slate-400" />}
                        <span className={cn(
                          "text-xs font-medium uppercase tracking-wider",
                          channel.status === "connected" ? "text-emerald-400" :
                          channel.status === "expired" ? "text-rose-400" : "text-slate-400"
                        )}>
                          {channel.status === "connected" ? "Đã kết nối" : 
                           channel.status === "expired" ? "Hết hạn Token" : "Đã ngắt kết nối"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="relative z-10 mt-8 flex items-center gap-3">
                  {channel.status === "connected" ? (
                    <Button variant="outline" size="sm" onClick={() => toggleStatus(channel.id)} className="group/btn active:scale-[0.98]">
                      Ngắt kết nối
                    </Button>
                  ) : (
                    <Button size="sm" onClick={() => toggleStatus(channel.id)} className={cn(
                      "group/btn active:scale-[0.98]",
                      channel.status === "expired" && "bg-rose-500 hover:bg-rose-600 text-white"
                    )}>
                      {channel.status === "expired" ? "Gia hạn Token" : "Kết nối lại"}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        ))}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
        >
          {/* Add New Channel Placeholder */}
          <div className="rounded-[2rem] border border-dashed border-white/10 p-2 h-full min-h-[200px] transition-all hover:border-white/20 hover:bg-white/[0.02] cursor-pointer flex items-center justify-center group/add">
            <div className="text-center space-y-3">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white/5 group-hover/add:bg-white/10 transition-colors">
                <Plus className="h-6 w-6 text-slate-400 group-hover/add:text-white transition-colors" />
              </div>
              <p className="text-sm font-medium text-slate-400 group-hover/add:text-slate-300">
                Thêm kênh TikTok / Facebook
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
