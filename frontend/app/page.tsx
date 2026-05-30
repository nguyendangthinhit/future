import { CreateWizard } from "@/components/create-wizard";

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 sm:py-14">
      <header className="mb-10 max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Tạo video mới
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-400 sm:text-base">
          Điền thông tin bên dưới để hệ thống tự tạo và lên lịch đăng video lên Facebook & TikTok.
        </p>
      </header>

      <CreateWizard />

      <footer className="mt-14 max-w-4xl mx-auto text-center text-xs text-slate-500 pb-10">
        MarkX · Gemini · n8n scheduled publishing
      </footer>
    </main>
  );
}
