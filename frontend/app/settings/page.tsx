"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Field, TextArea, TextInput } from "@/components/ui/field";
import { Card } from "@/components/ui/card";
import { CheckCircle2, Palette, ShieldCheck, Volume2 } from "lucide-react";

const STORAGE_KEY = "content_factory_brand_settings";

interface BrandSettings {
  brandName: string;
  toneOfVoice: string;
  primary: string;
  accent: string;
  bg: string;
  displayFont: string;
  bodyFont: string;
  voiceId: string;
  claimsAllowed: string;
  claimsForbidden: string;
}

const DEFAULT_SETTINGS: BrandSettings = {
  brandName: "MarkX Demo",
  toneOfVoice: "direct, credible, warm",
  primary: "#0f172a",
  accent: "#38bdf8",
  bg: "#f8fafc",
  displayFont: "Inter",
  bodyFont: "Inter",
  voiceId: "",
  claimsAllowed: "rang xay moi ngay\ngiao nhanh\nnguon goc ro rang",
  claimsForbidden: "chua khoi benh\ncam ket 100% ket qua\ngiam gia gay hieu nham",
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<BrandSettings>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    try {
      setSettings({ ...DEFAULT_SETTINGS, ...JSON.parse(raw) });
    } catch {
      setSettings(DEFAULT_SETTINGS);
    }
  }, []);

  function updateField<K extends keyof BrandSettings>(key: K, value: BrandSettings[K]) {
    setSettings((current) => ({ ...current, [key]: value }));
    setSaved(false);
  }

  function save() {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2000);
  }

  return (
    <main className="mx-auto min-h-screen max-w-5xl space-y-8 p-6 sm:p-10">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">
            Brand Control
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Cai dat brand kit
          </h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Luu cach noi, mau sac, font va nhung dieu AI duoc/khong duoc noi.
          </p>
        </div>
        <Button onClick={save}>
          {saved ? <CheckCircle2 className="h-4 w-4" /> : null}
          {saved ? "Da luu" : "Luu cau hinh"}
        </Button>
      </header>

      <section className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <div className="mb-6 flex items-center gap-3">
            <ShieldCheck className="h-5 w-5 text-emerald-300" />
            <h2 className="text-lg font-semibold text-white">Brand voice</h2>
          </div>
          <div className="space-y-5">
            <Field label="Brand name">
              <TextInput
                value={settings.brandName}
                onChange={(event) => updateField("brandName", event.target.value)}
              />
            </Field>
            <Field label="Tone of voice">
              <TextInput
                value={settings.toneOfVoice}
                onChange={(event) => updateField("toneOfVoice", event.target.value)}
              />
            </Field>
            <Field label="Duoc noi ve san pham" hint="moi dong mot y">
              <TextArea
                rows={5}
                value={settings.claimsAllowed}
                onChange={(event) => updateField("claimsAllowed", event.target.value)}
              />
            </Field>
            <Field label="Khong duoc noi" hint="moi dong mot y">
              <TextArea
                rows={5}
                value={settings.claimsForbidden}
                onChange={(event) => updateField("claimsForbidden", event.target.value)}
              />
            </Field>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <Palette className="h-5 w-5 text-sky-300" />
              <h2 className="text-lg font-semibold text-white">Palette & fonts</h2>
            </div>
            <div className="grid gap-5 sm:grid-cols-3">
              <Field label="Primary">
                <TextInput
                  value={settings.primary}
                  onChange={(event) => updateField("primary", event.target.value)}
                />
              </Field>
              <Field label="Accent">
                <TextInput
                  value={settings.accent}
                  onChange={(event) => updateField("accent", event.target.value)}
                />
              </Field>
              <Field label="Background">
                <TextInput
                  value={settings.bg}
                  onChange={(event) => updateField("bg", event.target.value)}
                />
              </Field>
            </div>
            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <Field label="Display font">
                <TextInput
                  value={settings.displayFont}
                  onChange={(event) => updateField("displayFont", event.target.value)}
                />
              </Field>
              <Field label="Body font">
                <TextInput
                  value={settings.bodyFont}
                  onChange={(event) => updateField("bodyFont", event.target.value)}
                />
              </Field>
            </div>
            <div className="mt-6 flex overflow-hidden rounded-3xl border border-white/10">
              {[settings.primary, settings.accent, settings.bg].map((color) => (
                <div key={color} className="h-24 flex-1" style={{ background: color }} />
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <Volume2 className="h-5 w-5 text-violet-300" />
              <h2 className="text-lg font-semibold text-white">Voice provider</h2>
            </div>
            <Field label="Voice ID" hint="ElevenLabs or provider voice id">
              <TextInput
                value={settings.voiceId}
                placeholder="voice_..."
                onChange={(event) => updateField("voiceId", event.target.value)}
              />
            </Field>
            <p className="mt-4 text-xs leading-5 text-slate-500">
              Seedance/Seed2 BytePlus integration is intentionally excluded per current scope.
            </p>
          </Card>
        </div>
      </section>
    </main>
  );
}
