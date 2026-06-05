"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { FactoryBrief, FactoryResult, FactoryVariantPack } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { ArrowRight, FileJson, Loader2, RefreshCw } from "lucide-react";

interface SampleBrief {
  file: string;
  theme: string;
  brand: string;
  audience: string;
  payload: FactoryBrief;
}

interface DemoResult {
  changed_field: string;
  before: FactoryResult;
  after: FactoryResult;
}

function getQaTotal(variant: FactoryVariantPack) {
  return Number(variant.qa?.score?.total ?? 0);
}

function getHook(variant: FactoryVariantPack) {
  const hook = variant.script?.hook;
  return typeof hook === "string" ? hook : JSON.stringify(hook ?? "");
}

function VariantCard({ variant }: { variant: FactoryVariantPack }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-white">{variant.variant_angle}</p>
          <p className="text-xs text-slate-500">{variant.variant_id}</p>
        </div>
        <span
          className={cn(
            "rounded-full border px-2.5 py-1 text-xs font-semibold",
            variant.qa_passed
              ? "border-emerald-400/30 bg-emerald-400/10 text-emerald-300"
              : "border-amber-400/30 bg-amber-400/10 text-amber-300"
          )}
        >
          QA {getQaTotal(variant)}
        </span>
      </div>
      <p className="line-clamp-3 text-sm leading-6 text-slate-300">{getHook(variant)}</p>
    </div>
  );
}

export default function HistoryPage() {
  const [samples, setSamples] = useState<SampleBrief[]>([]);
  const [selectedFile, setSelectedFile] = useState("");
  const [lastPack, setLastPack] = useState<FactoryResult | null>(null);
  const [demo, setDemo] = useState<DemoResult | null>(null);
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [sampleRes, packRes] = await Promise.all([
          api.getFactorySamples(),
          api.getLastFactoryPack(),
        ]);
        const loadedSamples = sampleRes.samples ?? [];
        setSamples(loadedSamples);
        setSelectedFile(loadedSamples[0]?.file ?? "");
        setLastPack(packRes.pack ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Cannot load factory history");
      }
    }
    load();
  }, []);

  const selectedSample = useMemo(
    () => samples.find((sample) => sample.file === selectedFile),
    [samples, selectedFile]
  );

  async function runDemo() {
    setLoadingDemo(true);
    setError("");
    try {
      const result = await api.runOneInputChangeDemo(selectedSample?.payload);
      setDemo(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Demo failed");
    } finally {
      setLoadingDemo(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-7xl space-y-8 p-6 sm:p-10">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
            Factory History
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Demo mot input thay doi
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Chon mot brief mau, doi audience, chay lai planner/director/QA va so sanh
            output truoc-sau.
          </p>
        </div>
        <Button onClick={runDemo} disabled={loadingDemo}>
          {loadingDemo ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Run one-input-change demo
        </Button>
      </header>

      {error && (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      <section className="grid gap-4 md:grid-cols-3">
        {samples.map((sample) => (
          <button
            key={sample.file}
            onClick={() => setSelectedFile(sample.file)}
            className={cn(
              "rounded-3xl border p-5 text-left transition-colors",
              selectedFile === sample.file
                ? "border-white/25 bg-white/[0.08]"
                : "border-white/10 bg-white/[0.03] hover:bg-white/[0.05]"
            )}
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10">
              <FileJson className="h-5 w-5 text-sky-300" />
            </div>
            <p className="text-sm font-semibold text-white">{sample.theme || sample.file}</p>
            <p className="mt-1 text-xs text-slate-500">{sample.file}</p>
            <p className="mt-3 text-xs text-slate-400">
              {sample.brand || "Unknown brand"} / {sample.audience || "Unknown audience"}
            </p>
          </button>
        ))}
      </section>

      {demo ? (
        <section className="grid gap-6 lg:grid-cols-[1fr_auto_1fr]">
          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
              Before
            </p>
            <h2 className="mt-2 text-xl font-semibold text-white">
              {String(demo.before.brief?.audience ? (demo.before.brief.audience as any).segment : "Original audience")}
            </h2>
            <div className="mt-5 space-y-3">
              {demo.before.variants.map((variant) => (
                <VariantCard key={variant.variant_id} variant={variant} />
              ))}
            </div>
          </Card>

          <div className="hidden items-center justify-center lg:flex">
            <div className="rounded-full border border-white/10 bg-white/[0.03] p-4">
              <ArrowRight className="h-6 w-6 text-slate-400" />
            </div>
          </div>

          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
              After
            </p>
            <h2 className="mt-2 text-xl font-semibold text-white">
              {String(demo.after.brief?.audience ? (demo.after.brief.audience as any).segment : "Changed audience")}
            </h2>
            <div className="mt-5 space-y-3">
              {demo.after.variants.map((variant) => (
                <VariantCard key={variant.variant_id} variant={variant} />
              ))}
            </div>
          </Card>
        </section>
      ) : (
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-white">Last generated pack</h2>
          {lastPack ? (
            <div className="mt-5 grid gap-3 md:grid-cols-2">
              {lastPack.variants.map((variant) => (
                <VariantCard key={variant.variant_id} variant={variant} />
              ))}
            </div>
          ) : (
            <p className="mt-3 text-sm text-slate-500">
              Chua co pack nao. Hay tao pack dau tien tai trang Content Factory.
            </p>
          )}
        </Card>
      )}
    </main>
  );
}
