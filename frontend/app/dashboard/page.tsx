"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { FactoryResult, FactoryVariantPack } from "@/lib/types";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Activity, CheckCircle2, Clock, Layers3, XCircle } from "lucide-react";

function qaTotal(variant: FactoryVariantPack) {
  return Number(variant.qa?.score?.total ?? 0);
}

function StatCard({
  label,
  value,
  detail,
  tone,
}: {
  label: string;
  value: string | number;
  detail: string;
  tone: "emerald" | "sky" | "violet" | "amber";
}) {
  const colors = {
    emerald: "from-emerald-400/20 to-emerald-400/5 text-emerald-300",
    sky: "from-sky-400/20 to-sky-400/5 text-sky-300",
    violet: "from-violet-400/20 to-violet-400/5 text-violet-300",
    amber: "from-amber-400/20 to-amber-400/5 text-amber-300",
  };

  return (
    <Card className="overflow-hidden p-6">
      <div className={cn("mb-6 h-1.5 w-20 rounded-full bg-gradient-to-r", colors[tone])} />
      <p className="text-sm font-medium text-slate-400">{label}</p>
      <p className="mt-2 text-4xl font-bold text-white">{value}</p>
      <p className="mt-2 text-xs text-slate-500">{detail}</p>
    </Card>
  );
}

export default function DashboardPage() {
  const [pack, setPack] = useState<FactoryResult | null>(null);
  const [trace, setTrace] = useState<Array<Record<string, unknown>>>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [packRes, traceRes] = await Promise.all([
          api.getLastFactoryPack(),
          api.getFactoryTrace(),
        ]);
        setPack(packRes.pack ?? null);
        setTrace(traceRes.trace ?? packRes.pack?.trace ?? []);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Dashboard load failed");
      }
    }
    load();
  }, []);

  const stats = useMemo(() => {
    const variants = pack?.variants ?? [];
    const publishable = pack?.publishable_variants ?? variants.filter((variant) => variant.qa_passed);
    const passRate = variants.length ? Math.round((publishable.length / variants.length) * 100) : 0;
    const avgQa = variants.length
      ? Math.round(variants.reduce((sum, variant) => sum + qaTotal(variant), 0) / variants.length)
      : 0;

    return {
      variants: variants.length,
      publishable: publishable.length,
      passRate,
      avgQa,
      wall: pack?.wall_s ?? pack?.elapsed_s ?? 0,
    };
  }, [pack]);

  return (
    <main className="mx-auto min-h-screen max-w-7xl space-y-8 p-6 sm:p-10">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
          Content Factory
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Dashboard van hanh
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Theo doi pack gan nhat: so variant, pass rate, thoi gian chay va trace agent.
        </p>
      </header>

      {error && (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      <section className="grid gap-5 md:grid-cols-4">
        <StatCard label="Variants" value={stats.variants} detail="So concept duoc tao tu brief" tone="sky" />
        <StatCard label="Publishable" value={stats.publishable} detail="QA pass va san sang review" tone="emerald" />
        <StatCard label="Pass rate" value={`${stats.passRate}%`} detail={`Average QA ${stats.avgQa}`} tone="violet" />
        <StatCard label="Wall time" value={`${stats.wall}s`} detail="Tong thoi gian orchestration" tone="amber" />
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="p-6">
          <div className="mb-5 flex items-center gap-3">
            <Layers3 className="h-5 w-5 text-sky-300" />
            <h2 className="text-lg font-semibold text-white">Variant QA</h2>
          </div>
          {pack?.variants?.length ? (
            <div className="space-y-3">
              {pack.variants.map((variant) => (
                <div
                  key={variant.variant_id}
                  className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4"
                >
                  <div>
                    <p className="text-sm font-semibold text-white">{variant.variant_angle}</p>
                    <p className="text-xs text-slate-500">{variant.variant_id}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-slate-200">{qaTotal(variant)}</span>
                    {variant.qa_passed ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-300" />
                    ) : (
                      <XCircle className="h-5 w-5 text-amber-300" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">Chua co factory pack de hien thi.</p>
          )}
        </Card>

        <Card className="p-6">
          <div className="mb-5 flex items-center gap-3">
            <Activity className="h-5 w-5 text-violet-300" />
            <h2 className="text-lg font-semibold text-white">Agent trace</h2>
          </div>
          <div className="space-y-3">
            {(trace.length ? trace : pack?.trace ?? []).map((event, index) => {
              const status = String(event.status ?? "done");
              return (
                <div key={`${String(event.agent ?? "agent")}-${index}`} className="flex gap-3">
                  <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/10 bg-white/[0.04]">
                    <Clock className="h-3.5 w-3.5 text-slate-400" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-white">{String(event.agent ?? "agent")}</p>
                    <p
                      className={cn(
                        "text-xs",
                        status === "failed" ? "text-red-300" : "text-slate-500"
                      )}
                    >
                      {status} {event.t_s ? `- ${String(event.t_s)}s` : ""}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </section>
    </main>
  );
}
