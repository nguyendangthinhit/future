"use client";

import { useMemo, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Field, TextArea, TextInput } from "@/components/ui/field";
import { ImageUploader } from "@/components/image-uploader";
import type { FactoryBrief, FactoryResult, UploadedImage } from "@/lib/types";
import { api } from "@/lib/api";
import {
  CheckCircle2,
  ImagePlus,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const defaultBrief: FactoryBrief = {
  theme: "",
  brand: {
    name: "",
    toneOfVoice: "tre trung, ro rang, dang tin",
    palette: { primary: "#8B4513", accent: "#FFD700", bg: "#FFFFFF" },
    fonts: { display: "Montserrat", body: "Inter" },
    logoUrl: "",
    voiceId: "",
    claimsAllowed: [],
    claimsForbidden: [],
  },
  audience: { segment: "gen-z Vietnam", age: "18-25", locale: "vi-VN" },
  platform: "tiktok",
  constraints: {
    lengthSec: 20,
    aspect: ["9:16", "1:1"],
    mustInclude: [],
    mustAvoid: [],
  },
  moodboardUrls: [],
  variantsTarget: 2,
};

function splitLines(input: string): string[] {
  return input
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function joinLines(input: string[]): string {
  return input.join("\n");
}

function imageDataUrls(images: UploadedImage[]) {
  return images.map((image) => image.dataUrl);
}

export function FactoryWizard() {
  const [brief, setBrief] = useState<FactoryBrief>(defaultBrief);
  const [referenceImages, setReferenceImages] = useState<UploadedImage[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<FactoryResult | null>(null);
  const [traceRefreshing, setTraceRefreshing] = useState(false);

  const canSubmit = useMemo(() => {
    return (
      brief.theme.trim().length >= 5 &&
      brief.brand.name.trim().length >= 2 &&
      brief.brand.toneOfVoice.trim().length >= 3
    );
  }, [brief]);

  const setBriefField = <Key extends keyof FactoryBrief>(
    key: Key,
    value: FactoryBrief[Key]
  ) => setBrief((current) => ({ ...current, [key]: value }));

  const setBrand = (patch: Partial<FactoryBrief["brand"]>) =>
    setBrief((current) => ({ ...current, brand: { ...current.brand, ...patch } }));

  const setAudience = (patch: Partial<FactoryBrief["audience"]>) =>
    setBrief((current) => ({
      ...current,
      audience: { ...current.audience, ...patch },
    }));

  const setConstraints = (patch: Partial<FactoryBrief["constraints"]>) =>
    setBrief((current) => ({
      ...current,
      constraints: { ...current.constraints, ...patch },
    }));

  function updateImages(images: UploadedImage[]) {
    setReferenceImages(images);
    setBrief((current) => ({
      ...current,
      moodboardUrls: imageDataUrls(images),
    }));
  }

  async function generatePack() {
    setSubmitting(true);
    try {
      const payload: FactoryBrief = {
        ...brief,
        moodboardUrls: imageDataUrls(referenceImages),
      };
      const data = await api.generateFactoryPack(payload);
      setResult(data);
    } catch (error) {
      console.error(error);
      alert(
        "Generate factory pack failed: " +
          (error instanceof Error ? error.message : String(error))
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function refreshTrace() {
    setTraceRefreshing(true);
    try {
      const traceResponse = await api.getFactoryTrace();
      setResult((current) => {
        if (!current) return current;
        return { ...current, trace: traceResponse.trace || [] };
      });
    } catch (error) {
      console.error(error);
    } finally {
      setTraceRefreshing(false);
    }
  }

  function resetBrief() {
    setBrief(defaultBrief);
    setReferenceImages([]);
    setResult(null);
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <Card className="p-6 sm:p-8">
        <div className="mb-6 space-y-1">
          <h2 className="text-2xl font-semibold text-white">Tao Content Factory Pack</h2>
          <p className="text-sm text-slate-400">
            Nhap brief, anh san pham/tham chieu va guideline thuong hieu. He thong se tao
            2 bien the A/B de review.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-5">
            <Field label="Y tuong video" required hint="noi ban muon video noi ve cai gi">
              <TextArea
                rows={4}
                placeholder="VD: Tao video TikTok 20s cho ca phe sua da, danh vao gen-z, mo dau phai bat mat trong 3 giay dau."
                value={brief.theme}
                onChange={(event) => setBriefField("theme", event.target.value)}
              />
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Ten thuong hieu" required>
                <TextInput
                  value={brief.brand.name}
                  onChange={(event) => setBrand({ name: event.target.value })}
                  placeholder="VD: Highlands Coffee"
                />
              </Field>
              <Field label="Giong noi thuong hieu" required hint="cach viet/cach noi">
                <TextInput
                  value={brief.brand.toneOfVoice}
                  onChange={(event) => setBrand({ toneOfVoice: event.target.value })}
                  placeholder="VD: tre trung, vui, dang tin"
                />
              </Field>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Nguoi xem">
                <TextInput
                  value={brief.audience.segment}
                  onChange={(event) => setAudience({ segment: event.target.value })}
                  placeholder="VD: me bim sua"
                />
              </Field>
              <Field label="Do tuoi">
                <TextInput
                  value={brief.audience.age}
                  onChange={(event) => setAudience({ age: event.target.value })}
                />
              </Field>
              <Field label="Ngon ngu">
                <TextInput
                  value={brief.audience.locale}
                  onChange={(event) => setAudience({ locale: event.target.value })}
                />
              </Field>
            </div>

            <Field label="Anh san pham / moodboard / reference" hint="co the upload anh">
              <ImageUploader images={referenceImages} onChange={updateImages} />
            </Field>

            <Field label="Logo URL" hint="khong bat buoc">
              <TextInput
                value={brief.brand.logoUrl ?? ""}
                onChange={(event) => setBrand({ logoUrl: event.target.value })}
                placeholder="https://.../logo.png"
              />
            </Field>

            <Field label="ElevenLabs Voice ID" hint="khong bat buoc">
              <TextInput
                value={brief.brand.voiceId ?? ""}
                onChange={(event) => setBrand({ voiceId: event.target.value })}
                placeholder="VD: 21m00Tcm4TlvDq8ikWAM"
              />
            </Field>
          </div>

          <div className="space-y-5">
            <div className="rounded-3xl border border-sky-400/20 bg-sky-400/10 p-4">
              <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-sky-100">
                <ShieldCheck className="h-4 w-4" />
                Ve phan “duoc noi / khong duoc noi”
              </div>
              <p className="text-xs leading-5 text-sky-100/80">
                Day la bo loc de AI khong noi qua da. Vi du: “duoc noi” la
                “rang xay moi ngay”; “khong duoc noi” la “chua khoi benh”,
                “giam can 100%”. Neu chua can, co the de trong.
              </p>
            </div>

            <Field label="Duoc noi ve san pham" hint="moi dong mot y, co the bo trong">
              <TextArea
                rows={4}
                value={joinLines(brief.brand.claimsAllowed)}
                onChange={(event) =>
                  setBrand({ claimsAllowed: splitLines(event.target.value) })
                }
                placeholder={"rang xay moi ngay\nnguyen lieu Viet Nam\ngiao nhanh trong ngay"}
              />
            </Field>

            <Field label="Khong duoc noi" hint="nhung cau cam / de vi pham">
              <TextArea
                rows={4}
                value={joinLines(brief.brand.claimsForbidden)}
                onChange={(event) =>
                  setBrand({ claimsForbidden: splitLines(event.target.value) })
                }
                placeholder={"chua khoi benh\n100% hieu qua\nre nhat thi truong"}
              />
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Bat buoc co trong video" hint="moi dong mot y">
                <TextArea
                  rows={3}
                  value={joinLines(brief.constraints.mustInclude)}
                  onChange={(event) =>
                    setConstraints({ mustInclude: splitLines(event.target.value) })
                  }
                  placeholder={"ten san pham\nuu dai khai truong\nCTA: dat hang ngay"}
                />
              </Field>

              <Field label="Can tranh trong video" hint="moi dong mot y">
                <TextArea
                  rows={3}
                  value={joinLines(brief.constraints.mustAvoid)}
                  onChange={(event) =>
                    setConstraints({ mustAvoid: splitLines(event.target.value) })
                  }
                  placeholder={"noi qua dai\nhinh anh y te\nso sanh doi thu"}
                />
              </Field>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <Field label="Do dai">
                <select
                  className="h-12 w-full rounded-xl border border-white/10 bg-[#09090b] px-3 text-sm text-slate-200"
                  value={brief.constraints.lengthSec}
                  onChange={(event) =>
                    setConstraints({
                      lengthSec: Number(event.target.value) as 15 | 20 | 30,
                    })
                  }
                >
                  <option value={15}>15s</option>
                  <option value={20}>20s</option>
                  <option value={30}>30s</option>
                </select>
              </Field>

              <Field label="Nen tang">
                <select
                  className="h-12 w-full rounded-xl border border-white/10 bg-[#09090b] px-3 text-sm text-slate-200"
                  value={brief.platform}
                  onChange={(event) =>
                    setBriefField(
                      "platform",
                      event.target.value as "tiktok" | "reels" | "shorts" | "all"
                    )
                  }
                >
                  <option value="tiktok">TikTok</option>
                  <option value="reels">Reels</option>
                  <option value="shorts">Shorts</option>
                  <option value="all">All</option>
                </select>
              </Field>

              <Field label="So bien the">
                <select
                  className="h-12 w-full rounded-xl border border-white/10 bg-[#09090b] px-3 text-sm text-slate-200"
                  value={brief.variantsTarget}
                  onChange={(event) =>
                    setBriefField("variantsTarget", Number(event.target.value) as 1 | 2)
                  }
                >
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                </select>
              </Field>
            </div>
          </div>
        </div>

        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <ImagePlus className="h-4 w-4" />
            {referenceImages.length} anh tham chieu se duoc dua vao brief.
          </div>
          <div className="flex items-center justify-end gap-3">
            <Button variant="outline" onClick={resetBrief} disabled={submitting}>
              Reset
            </Button>
            <Button onClick={generatePack} disabled={!canSubmit || submitting}>
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Dang tao...
                </>
              ) : (
                <>
                  Tao Factory Pack
                  <Sparkles className="h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>

      {result && (
        <Card className="space-y-6 p-6 sm:p-8">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-xl font-semibold text-white">Ket qua factory</h3>
              <p className="text-sm text-slate-400">
                Wall time: {result.wall_s}s / Variants: {result.variants?.length || 0}
              </p>
            </div>
            <Button variant="outline" onClick={refreshTrace} disabled={traceRefreshing}>
              {traceRefreshing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Refreshing...
                </>
              ) : (
                <>
                  <RefreshCw className="h-4 w-4" />
                  Refresh Trace
                </>
              )}
            </Button>
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            {(result.variants || []).map((variant) => {
              const total = variant.qa?.score?.total ?? 0;
              const passed = !!variant.qa_passed;
              return (
                <div
                  key={variant.variant_id}
                  className={cn(
                    "space-y-3 rounded-2xl border p-4",
                    passed
                      ? "border-emerald-400/30 bg-emerald-500/[0.04]"
                      : "border-red-400/30 bg-red-500/[0.04]"
                  )}
                >
                  <div className="flex items-center justify-between gap-3">
                    <h4 className="font-semibold text-white">
                      Variant {variant.variant_id} / {variant.variant_angle}
                    </h4>
                    <span
                      className={cn(
                        "inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs",
                        passed
                          ? "bg-emerald-500/20 text-emerald-300"
                          : "bg-red-500/20 text-red-300"
                      )}
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      {passed ? "Pass" : "Fail"}
                    </span>
                  </div>

                  <div className="text-sm text-slate-300">
                    QA Score: <span className="font-semibold text-white">{total}</span>/100
                  </div>

                  <p className="line-clamp-3 text-xs text-slate-400">
                    Hook: {(variant.script as any)?.hook || "-"}
                  </p>
                  <p className="line-clamp-3 text-xs text-slate-400">
                    Caption: {(variant.pack as any)?.caption || "-"}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-4">
            <h4 className="mb-2 font-medium text-white">Live DAG Trace</h4>
            <div className="flex flex-wrap gap-2">
              {(result.trace || []).map((traceEvent, index) => (
                <span
                  key={`${String(traceEvent.agent)}-${index}`}
                  className="rounded-full border border-white/10 bg-white/5 px-2 py-1 text-xs text-slate-300"
                >
                  {String(traceEvent.agent)} / {String(traceEvent.status || "done")}
                </span>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
