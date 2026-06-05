"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2, RefreshCw, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FactoryResult, FactoryVariantPack } from "@/lib/types";

export default function VerifyPage() {
  const [pack, setPack] = useState<FactoryResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [approvedId, setApprovedId] = useState<string | null>(null);

  useEffect(() => {
    loadPack();
  }, []);

  async function loadPack() {
    setLoading(true);
    try {
      const data = await api.getLastFactoryPack();
      setPack(data.pack || null);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  const variants = pack?.variants || [];

  return (
    <main className="min-h-screen p-6 sm:p-10 max-w-7xl mx-auto space-y-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Variant Review
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            So sanh cac bien the trong factory pack gan nhat, kiem tra QA va chon ban san sang ban giao.
          </p>
        </div>
        <Button variant="outline" onClick={loadPack} disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          Refresh Pack
        </Button>
      </header>

      {loading ? (
        <div className="flex items-center justify-center p-20">
          <Loader2 className="w-8 h-8 animate-spin text-slate-500" />
        </div>
      ) : !pack ? (
        <Card className="p-10 text-center text-slate-400">
          Chua co factory pack. Hay chay Generate Factory Pack o trang create truoc.
        </Card>
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <Summary label="Variants" value={String(variants.length)} />
            <Summary label="Publishable" value={String((pack.publishable_variants || variants.filter((v) => v.qa_passed)).length)} />
            <Summary label="Wall Time" value={`${pack.wall_s || pack.elapsed_s || 0}s`} />
          </div>

          <div className="grid gap-5 lg:grid-cols-2">
            {variants.map((variant) => (
              <VariantCard
                key={variant.variant_id}
                variant={variant}
                approved={approvedId === variant.variant_id}
                onApprove={() => setApprovedId(variant.variant_id)}
              />
            ))}
          </div>
        </div>
      )}
    </main>
  );
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </Card>
  );
}

function VariantCard({
  variant,
  approved,
  onApprove,
}: {
  variant: FactoryVariantPack;
  approved: boolean;
  onApprove: () => void;
}) {
  const score = variant.qa?.score?.total ?? 0;
  const passed = !!variant.qa_passed;
  const script = variant.script as any;
  const pack = variant.pack as any;

  return (
    <Card className={cn("p-6 space-y-5", passed ? "border-emerald-400/25" : "border-amber-400/25")}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-500">
            Variant {variant.variant_id}
          </p>
          <h2 className="mt-1 text-xl font-semibold text-white">
            {variant.variant_angle || "Creative variant"}
          </h2>
        </div>
        <span className={cn(
          "rounded-full px-3 py-1 text-xs font-medium",
          passed ? "bg-emerald-500/15 text-emerald-300" : "bg-amber-500/15 text-amber-300"
        )}>
          QA {score}/100
        </span>
      </div>

      <div className="space-y-3 text-sm text-slate-300">
        <Block label="Hook" value={script?.hook || "-"} />
        <Block label="CTA" value={script?.cta || "-"} />
        <Block label="Caption" value={pack?.caption || "-"} />
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs text-slate-400">
        <Block label="Clips" value={String((variant as any).clip_urls?.length || 0)} />
        <Block label="Exports" value={Object.keys((variant as any).final_video_urls || {}).join(", ") || "-"} />
      </div>

      <Button onClick={onApprove} disabled={!passed || approved} className="w-full">
        {approved ? (
          <>
            <CheckCircle2 className="h-4 w-4" />
            Approved
          </>
        ) : (
          <>
            <ShieldCheck className="h-4 w-4" />
            Approve Variant
          </>
        )}
      </Button>
    </Card>
  );
}

function Block({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
      <p className="text-[10px] uppercase tracking-wider text-slate-500">{label}</p>
      <p className="mt-1 text-sm leading-relaxed text-slate-300">{value}</p>
    </div>
  );
}
