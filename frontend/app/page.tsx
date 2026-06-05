import { FactoryWizard } from "@/components/factory-wizard";

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-10 sm:px-12 sm:py-14">
      <header className="mb-10 max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Content Factory
        </h1>
        <p className="mt-2 text-sm leading-relaxed text-slate-400 sm:text-base">
          Nhap mot brief, khoa brand kit va sinh 2-3 bien the video ngan de
          bien tap, cham QA va dong goi.
        </p>
      </header>

      <FactoryWizard />

      <footer className="mt-14 max-w-6xl mx-auto text-center text-xs text-slate-500 pb-10">
        MarkX - Content Factory - TRAE orchestration
      </footer>
    </main>
  );
}
