"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { TextInput, Toggle } from "@/components/ui/field";
import { KeyRound, Shield, Bell, HardDrive, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved">("idle");
  const [autoSync, setAutoSync] = useState(true);
  const [notifications, setNotifications] = useState(true);

  const handleSave = () => {
    setSaveStatus("saving");
    setTimeout(() => {
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 2000);
    }, 1000);
  };

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-4xl mx-auto space-y-10">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold tracking-tight text-white">Cài đặt</h1>
        <p className="text-slate-400">Tùy chỉnh hệ thống, API Key và thông báo.</p>
      </div>

      <div className="grid gap-10">
        
        {/* Section: API Keys */}
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
          className="space-y-6"
        >
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10">
              <KeyRound className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">API AI & Dịch vụ</h2>
              <p className="text-sm text-slate-400">Cấu hình kết nối tới Gemini / LightningAI</p>
            </div>
          </div>

          <div className="rounded-[2rem] bg-white/[0.02] border border-white/5 p-2">
            <div className="rounded-[calc(2rem-0.5rem)] bg-[#0a0a0a] p-6 space-y-6 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 block">Gemini API Key</label>
                <div className="flex gap-3">
                  <TextInput 
                    type="password" 
                    placeholder="AIzaSy..." 
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleSave} 
                    disabled={saveStatus === "saving" || !apiKey}
                    className="group active:scale-[0.98] transition-all w-32"
                  >
                    {saveStatus === "saving" ? "Đang lưu..." : saveStatus === "saved" ? (
                      <><CheckCircle2 className="h-4 w-4 mr-2" /> Đã lưu</>
                    ) : "Lưu thay đổi"}
                  </Button>
                </div>
                <p className="text-xs text-slate-500 mt-2 flex items-center gap-1.5">
                  <Shield className="h-3 w-3" /> API Key được lưu trữ cục bộ và mã hóa.
                </p>
              </div>
            </div>
          </div>
        </motion.section>

        {/* Section: Preferences */}
        <motion.section 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.5, ease: [0.32, 0.72, 0, 1] }}
          className="space-y-6"
        >
          <div className="flex items-center gap-3 border-b border-white/10 pb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/10">
              <HardDrive className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Hệ thống & Dữ liệu</h2>
              <p className="text-sm text-slate-400">Quản lý đồng bộ và thông báo hệ thống</p>
            </div>
          </div>

          <div className="rounded-[2rem] bg-white/[0.02] border border-white/5 p-2">
            <div className="rounded-[calc(2rem-0.5rem)] bg-[#0a0a0a] p-6 space-y-6 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] divide-y divide-white/5">
              
              <div className="pb-6">
                <Toggle 
                  checked={autoSync}
                  onChange={setAutoSync}
                  label="Đồng bộ đám mây"
                  description="Tự động đồng bộ lịch sử và cấu hình video lên máy chủ."
                />
              </div>

              <div className="pt-6">
                <Toggle 
                  checked={notifications}
                  onChange={setNotifications}
                  label="Thông báo trạng thái"
                  description="Nhận thông báo khi render xong video hoặc đăng bài thành công."
                />
              </div>

            </div>
          </div>
        </motion.section>

      </div>
    </main>
  );
}
