"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function VerifyPage() {
  const [ideas, setIdeas] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const data = await api.get("/verify/list");
      setIdeas(data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(id: string) {
    setProcessingId(id);
    try {
      await api.post(`/verify/${id}/approve`, {});
      await loadData();
    } catch (e) {
      console.error(e);
      alert("Lỗi khi duyệt");
    } finally {
      setProcessingId(null);
    }
  }

  async function handleReject(id: string) {
    setProcessingId(id);
    try {
      await api.post(`/verify/${id}/reject`, {});
      await loadData();
    } catch (e) {
      console.error(e);
      alert("Lỗi khi từ chối");
    } finally {
      setProcessingId(null);
    }
  }

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-7xl mx-auto space-y-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Kiểm duyệt ý tưởng
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Các ý tưởng video được AI tự động sinh ra vào ban đêm.
        </p>
      </header>

      {loading ? (
        <div className="flex items-center justify-center p-20">
          <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
        </div>
      ) : ideas.length === 0 ? (
        <Card className="p-10 text-center text-slate-400">
          Không có ý tưởng nào đang chờ duyệt.
        </Card>
      ) : (
        <div className="space-y-4">
          {ideas.map((idea) => (
            <Card key={idea.id} className="p-6 space-y-4 flex flex-col sm:flex-row gap-6">
              <div className="flex-1 space-y-2">
                <div className="flex gap-2">
                  <span className="text-xs px-2 py-1 rounded bg-indigo-500/20 text-indigo-300">
                    {idea.channel}
                  </span>
                  <span className="text-xs px-2 py-1 rounded bg-fuchsia-500/20 text-fuchsia-300">
                    {idea.style_name || "Tự do"}
                  </span>
                </div>
                <p className="text-lg font-medium text-white">{idea.raw_content}</p>
                {idea.extra_data && (
                  <p className="text-sm text-slate-400">
                    <strong className="text-slate-300">Data:</strong> {idea.extra_data}
                  </p>
                )}
                {idea.final_prompt && (
                  <p className="text-xs text-slate-500 font-mono mt-2 p-2 bg-white/5 rounded">
                    {idea.final_prompt.substring(0, 150)}...
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-2 min-w-[120px]">
                <button
                  disabled={processingId === idea.id}
                  onClick={() => handleApprove(idea.id)}
                  className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 font-medium text-sm transition-all disabled:opacity-50"
                >
                  {processingId === idea.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                  Duyệt
                </button>
                <button
                  disabled={processingId === idea.id}
                  onClick={() => handleReject(idea.id)}
                  className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 font-medium text-sm transition-all disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  Từ chối
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}
