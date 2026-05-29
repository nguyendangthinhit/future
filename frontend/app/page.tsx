import { CreateWizard } from "@/components/create-wizard";
import { Sparkles, Video } from "lucide-react";

export default function Home() {
  return (
    <main className="mx-auto min-h-screen max-w-3xl px-4 py-10 sm:px-6 sm:py-14">
      <header className="mb-10 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3.5 py-1.5 text-xs font-medium text-slate-300 backdrop-blur-sm">
          <Sparkles className="h-3.5 w-3.5 text-fuchsia-400" />
          Auto Video Platform
        </div>
        <h1 className="flex items-center justify-center gap-2.5 text-3xl font-bold tracking-tight sm:text-4xl">
          <Video className="h-8 w-8 text-indigo-400" />
          <span className="text-gradient">Tạo video tự động</span>
        </h1>
        <p className="mx-auto mt-3 max-w-xl text-sm leading-relaxed text-slate-400 sm:text-base">
          Nhập ý tưởng, chọn phong cách, thêm caption — hệ thống tự dựng video
          và lên lịch đăng lên Facebook & TikTok.
        </p>
      </header>

      <CreateWizard />

      <footer className="mt-14 text-center text-xs text-slate-500">
        ViMax engine · Gemini · n8n scheduled publishing
      </footer>
    </main>
  );
}
