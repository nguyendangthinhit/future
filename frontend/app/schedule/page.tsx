"use client";

import { useEffect, useMemo, useState } from "react";
import { api } from "@/lib/api";
import type { FactoryResult, FactoryVariantPack } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Field, TextArea, TextInput } from "@/components/ui/field";
import { cn } from "@/lib/utils";
import { Calendar, CheckCircle2, Loader2, Send } from "lucide-react";

type Platform = "tiktok" | "reels" | "shorts";

function getCaption(variant: FactoryVariantPack) {
  const caption = variant.pack?.caption;
  return typeof caption === "string" ? caption : "";
}

function getTitle(variant: FactoryVariantPack) {
  const title = variant.pack?.title;
  return typeof title === "string" ? title : variant.variant_angle;
}

export default function SchedulePage() {
  const [pack, setPack] = useState<FactoryResult | null>(null);
  const [variantId, setVariantId] = useState("");
  const [platform, setPlatform] = useState<Platform>("tiktok");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [caption, setCaption] = useState("");
  const [loading, setLoading] = useState(false);
  const [handoff, setHandoff] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const result = await api.getLastFactoryPack();
        const loadedPack = result.pack ?? null;
        const variants = loadedPack?.publishable_variants ?? loadedPack?.variants ?? [];
        setPack(loadedPack);
        setVariantId(variants[0]?.variant_id ?? "");
        setCaption(variants[0] ? getCaption(variants[0]) : "");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Cannot load factory pack");
      }
    }
    load();
  }, []);

  const variants = useMemo(
    () => pack?.publishable_variants ?? pack?.variants ?? [],
    [pack]
  );
  const selectedVariant = variants.find((variant) => variant.variant_id === variantId);

  function selectVariant(variant: FactoryVariantPack) {
    setVariantId(variant.variant_id);
    setCaption(getCaption(variant));
    setHandoff(null);
  }

  async function submit() {
    if (!variantId || !date || !time) {
      setError("Chon variant, ngay va gio dang truoc khi handoff.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const result = await api.scheduleFactoryHandoff({
        variant_id: variantId,
        platform,
        scheduled_at: `${date} ${time}`,
        caption,
      });
      setHandoff(result.handoff);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Schedule handoff failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto min-h-screen max-w-6xl space-y-8 p-6 sm:p-10">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
          Schedule Handoff
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
          Ban giao pack sang lich dang
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
          Chon variant da qua QA, nen tang va gio dang. Payload se duoc ghi vao
          outputs/schedule_handoff.json va gui n8n neu co N8N_WEBHOOK_URL.
        </p>
      </header>

      {error && (
        <div className="rounded-2xl border border-red-400/20 bg-red-400/10 p-4 text-sm text-red-200">
          {error}
        </div>
      )}

      <section className="grid gap-6 lg:grid-cols-[1fr_0.8fr]">
        <Card className="p-6">
          <h2 className="mb-5 text-lg font-semibold text-white">Publishable variants</h2>
          {variants.length ? (
            <div className="space-y-3">
              {variants.map((variant) => (
                <button
                  key={variant.variant_id}
                  onClick={() => selectVariant(variant)}
                  className={cn(
                    "w-full rounded-2xl border p-4 text-left transition-colors",
                    variantId === variant.variant_id
                      ? "border-white/25 bg-white/[0.08]"
                      : "border-white/10 bg-white/[0.03] hover:bg-white/[0.05]"
                  )}
                >
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{getTitle(variant)}</p>
                      <p className="mt-1 text-xs text-slate-500">
                        {variant.variant_id} / {variant.variant_angle}
                      </p>
                    </div>
                    {variant.qa_passed ? (
                      <CheckCircle2 className="h-5 w-5 text-emerald-300" />
                    ) : null}
                  </div>
                  <p className="mt-3 line-clamp-2 text-xs leading-5 text-slate-400">
                    {getCaption(variant) || "No caption generated yet."}
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              Chua co factory pack. Hay chay Generate Factory Pack truoc.
            </p>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="mb-5 text-lg font-semibold text-white">Schedule payload</h2>
          <div className="space-y-5">
            <Field label="Platform">
              <div className="grid grid-cols-3 gap-2">
                {(["tiktok", "reels", "shorts"] as Platform[]).map((item) => (
                  <button
                    key={item}
                    onClick={() => setPlatform(item)}
                    className={cn(
                      "rounded-full border px-4 py-2 text-sm font-semibold uppercase tracking-wide",
                      platform === item
                        ? "border-white bg-white text-black"
                        : "border-white/10 bg-white/[0.03] text-slate-300"
                    )}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Ngay dang">
                <TextInput type="date" value={date} onChange={(event) => setDate(event.target.value)} />
              </Field>
              <Field label="Gio dang">
                <TextInput type="time" value={time} onChange={(event) => setTime(event.target.value)} />
              </Field>
            </div>

            <Field label="Caption">
              <TextArea rows={6} value={caption} onChange={(event) => setCaption(event.target.value)} />
            </Field>

            <Button className="w-full" onClick={submit} disabled={loading || !selectedVariant}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              Handoff to schedule
            </Button>
          </div>

          {handoff && (
            <div className="mt-6 rounded-2xl border border-emerald-400/20 bg-emerald-400/10 p-4">
              <div className="flex items-center gap-2 text-sm font-semibold text-emerald-200">
                <Calendar className="h-4 w-4" />
                Handoff ready
              </div>
              <p className="mt-2 text-xs leading-5 text-emerald-100/80">
                n8n status: {String(handoff.n8n_status ?? "unknown")}
              </p>
            </div>
          )}
        </Card>
      </section>
    </main>
  );
}
