"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Stepper } from "@/components/stepper";
import {
  Field,
  OptionCard,
  TextArea,
  TextInput,
  Toggle,
} from "@/components/ui/field";
import { ImageUploader } from "@/components/image-uploader";
import { DURATIONS, stylesFor } from "@/lib/data";
import type {
  CaptionSuggestion,
  Channel,
  CreateVideoForm,
  ResearchBrief,
  VideoType,
} from "@/lib/types";
import {
  ArrowLeft,
  ArrowRight,
  Clapperboard,
  Megaphone,
  Facebook,
  Music2,
  Sparkles,
  Wand2,
  Loader2,
  CheckCircle2,
  RotateCcw,
  Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const STEPS = ["Cấu hình", "Nội dung", "Phong cách", "Caption", "Xem lại"];

const FB_LIMIT = 63206;
const TIKTOK_LIMIT = 2200;

const emptyForm: CreateVideoForm = {
  videoType: null,
  channel: null,
  scheduledDate: "",
  scheduledTime: "",
  duration: null,
  content: "",
  useGoogleData: false,
  searchKeyword: "",
  images: [],
  styleId: null,
  caption: "",
  generatedPrompt: "",
  researchBrief: null,
};

export function CreateWizard() {
  const [step, setStep] = useState(0);
  const [maxReached, setMaxReached] = useState(0);
  const [form, setForm] = useState<CreateVideoForm>(emptyForm);

  const [genningPrompt, setGenningPrompt] = useState(false);
  const [genningCaption, setGenningCaption] = useState(false);
  const [captionIdeas, setCaptionIdeas] = useState<CaptionSuggestion[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const set = <K extends keyof CreateVideoForm>(
    key: K,
    value: CreateVideoForm[K]
  ) => setForm((f) => ({ ...f, [key]: value }));

  const availableStyles = useMemo(
    () => stylesFor(form.videoType),
    [form.videoType]
  );
  const captionLimit = form.channel === "facebook" ? FB_LIMIT : TIKTOK_LIMIT;

  const goTo = (i: number) => {
    setStep(i);
    setMaxReached((m) => Math.max(m, i));
  };

  const missing = useMemo(() => {
    const m: string[] = [];
    switch (step) {
      case 0:
        if (!form.videoType) m.push("loại video");
        if (!form.channel) m.push("kênh đăng");
        if (!form.scheduledDate) m.push("ngày đăng");
        if (!form.scheduledTime) m.push("giờ đăng");
        if (!form.duration) m.push("thời lượng");
        break;
      case 1:
        if (form.content.trim().length < 10) m.push("nội dung (≥ 10 ký tự)");
        if (form.images.length === 0) m.push("ảnh đính kèm");
        break;
      case 2:
        if (!form.styleId) m.push("phong cách");
        break;
      case 3:
        if (form.caption.trim().length === 0) m.push("caption");
        break;
    }
    return m;
  }, [step, form]);

  const canNext = missing.length === 0;

  const next = () => {
    if (step === 2 && !form.generatedPrompt) generatePrompt();
    goTo(Math.min(step + 1, STEPS.length - 1));
  };
  const back = () => goTo(Math.max(step - 1, 0));

  async function generatePrompt() {
    setGenningPrompt(true);
    try {
      const styleName =
        availableStyles.find((s) => s.id === form.styleId)?.name || "";
      const res = await fetch("/api/prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: form.content,
          videoType: form.videoType,
          duration: form.duration,
          styleId: form.styleId,
          styleName,
          useGoogleData: form.useGoogleData,
          searchKeyword: form.searchKeyword,
          hasImages: form.images.length > 0,
        }),
      });
      const data = await res.json();
      set("generatedPrompt", data.prompt ?? "");
    } catch {
      set("generatedPrompt", "");
    } finally {
      setGenningPrompt(false);
    }
  }

  const suggestCaption = async () => {
    setGenningCaption(true);
    try {
      const styleName = availableStyles.find(s => s.id === form.styleId)?.name || "";
      const res = await api.post("/caption/generate", {
        content: form.content,
        style_name: styleName,
        channel: form.channel
      });
      if (res && res.captions) {
        setCaptionIdeas(res.captions.map((c: string) => ({ text: c, tone: "Gợi ý AI" })));
      }
    } catch (e) {
      console.error(e);
      alert("Lỗi khi tạo caption.");
    } finally {
      setGenningCaption(false);
    }
  };

  async function submit() {
    setSubmitting(true);
    try {
      if (!form.generatedPrompt) await generatePrompt();
      
      const formData = new FormData();
      formData.append("video_type", form.videoType || "");
      formData.append("channel", form.channel || "");
      formData.append("scheduled_date", form.scheduledDate);
      formData.append("raw_content", form.content);
      formData.append("style_id", form.styleId || "");
      
      const styleName = availableStyles.find(s => s.id === form.styleId)?.name || "";
      formData.append("style_name", styleName);

      // Parse duration from string (e.g. "20-30") to integer (e.g. 20)
      let parsedDuration = 30;
      if (typeof form.duration === "number") {
        parsedDuration = form.duration;
      } else if (typeof form.duration === "string") {
        const first = parseInt(form.duration.split("-")[0], 10);
        if (!Number.isNaN(first)) parsedDuration = first;
      }
      formData.append("duration", parsedDuration.toString());

      formData.append("country_code", "VN");
      formData.append("use_google_data", form.useGoogleData ? "true" : "false");
      formData.append("search_keyword", form.searchKeyword);

      if (form.researchBrief) {
        const filtered = {
          ...form.researchBrief,
          stages: form.researchBrief.stages.filter(s => s.enabled),
          key_facts: form.researchBrief.key_facts.filter(f => f.enabled).map(f => f.text),
        };
        formData.append("research_brief", JSON.stringify(filtered));
      }
      
      if (form.images.length > 0 && form.images[0].file) {
        formData.append("mascot_image", form.images[0].file);
      }

      await api.post("/video/create", formData);
      setSubmitted(true);
    } catch (e) {
      console.error("Failed to create video:", e);
      alert("Lỗi: " + (e instanceof Error ? e.message : String(e)));
    } finally {
      setSubmitting(false);
    }
  }

  const reset = () => {
    setForm(emptyForm);
    setCaptionIdeas([]);
    setSubmitted(false);
    setStep(0);
    setMaxReached(0);
  };

  if (submitted) {
    return <SuccessScreen form={form} onReset={reset} />;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <Card className="px-5 py-5 sm:px-8">
        <Stepper
          steps={STEPS}
          current={step}
          maxReached={maxReached}
          onStepClick={goTo}
        />
      </Card>

      <div className="relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 15, filter: "blur(4px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: -15, filter: "blur(4px)" }}
            transition={{ duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
          >
            <Card className="p-6 sm:p-8">
              {step === 0 && <StepConfig form={form} set={set} />}
              {step === 1 && <StepContent form={form} set={set} />}
              {step === 2 && (
                <StepStyle
                  form={form}
                  set={set}
                  styles={availableStyles}
                />
              )}
              {step === 3 && (
                <StepCaption
                  form={form}
                  set={set}
                  limit={captionLimit}
                  ideas={captionIdeas}
                  loading={genningCaption}
                  onSuggest={suggestCaption}
                />
              )}
              {step === 4 && (
                <StepReview
                  form={form}
                  loadingPrompt={genningPrompt}
                  onRegenerate={generatePrompt}
                />
              )}
            </Card>
          </motion.div>
        </AnimatePresence>
      </div>

      <div className="flex items-center justify-between pt-4">
        <Button
          variant="ghost"
          onClick={back}
          disabled={step === 0}
          className={cn(step === 0 && "invisible", "group active:scale-[0.98] transition-all")}
        >
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/10 group-hover:bg-white/20 transition-all duration-300 group-hover:-translate-x-1">
            <ArrowLeft className="h-3.5 w-3.5" />
          </div>
          Quay lại
        </Button>

        {step < STEPS.length - 1 ? (
          <div className="flex items-center gap-4">
            {missing.length > 0 && (
              <span className="hidden text-xs text-slate-500 sm:block">
                Còn thiếu: {missing.join(", ")}
              </span>
            )}
            <Button onClick={next} disabled={!canNext} className="pl-6 pr-2 py-2 group active:scale-[0.98] transition-all duration-300">
              Tiếp tục
              <div className="ml-2 flex h-8 w-8 items-center justify-center rounded-full bg-black/10 group-hover:bg-black/20 transition-all duration-300 group-hover:translate-x-1 group-hover:-translate-y-[1px] group-hover:scale-105">
                <ArrowRight className="h-4 w-4" />
              </div>
            </Button>
          </div>
        ) : (
          <Button onClick={submit} disabled={submitting} size="lg" className="pl-6 pr-2 py-2 group active:scale-[0.98] transition-all duration-300">
            {submitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Đang xử lý...
              </>
            ) : (
              <>
                Tạo & Lên lịch
                <div className="ml-3 flex h-10 w-10 items-center justify-center rounded-full bg-black/10 group-hover:bg-black/20 transition-all duration-300 group-hover:translate-x-1 group-hover:-translate-y-[1px] group-hover:scale-105">
                  <Sparkles className="h-4 w-4" />
                </div>
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}

/* ---------- Step 1: Config ---------- */
function StepConfig({
  form,
  set,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
}) {
  return (
    <div className="space-y-7">
      <div className="space-y-1 mb-8">
        <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">Bước 1</span>
        <Header
          title="Cấu hình cơ bản"
          subtitle="Chọn loại video, kênh đăng và thời điểm bạn muốn xuất bản."
        />
      </div>

      <Field label="Loại video" required>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            selected={form.videoType === "entertainment"}
            onClick={() => {
              set("videoType", "entertainment");
              set("duration", null);
              set("styleId", null);
            }}
            title="Giải trí"
            description="Video giải trí, review, vlog..."
            icon={<span className="text-2xl drop-shadow-md">🎬</span>}
          />
          <OptionCard
            selected={form.videoType === "ads"}
            onClick={() => {
              set("videoType", "ads");
              set("duration", null);
              set("styleId", null);
            }}
            title="Quảng cáo"
            description="Quảng bá sản phẩm, dịch vụ"
            icon={<span className="text-2xl drop-shadow-md">📢</span>}
          />
        </div>
      </Field>

      <Field label="Kênh đăng" required>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            selected={form.channel === "facebook"}
            onClick={() => set("channel", "facebook")}
            title="Facebook"
            description="Đăng lên Fanpage"
            icon={<Facebook className="h-5 w-5 text-[#1877F2]" />}
          />
          <OptionCard
            selected={form.channel === "tiktok"}
            onClick={() => set("channel", "tiktok")}
            title="TikTok"
            description="Đăng lên kênh TikTok"
            icon={<Music2 className="h-5 w-5 text-slate-200" />}
          />
        </div>
      </Field>

      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Ngày đăng" required>
          <TextInput
            type="date"
            value={form.scheduledDate}
            onChange={(e) => set("scheduledDate", e.target.value)}
          />
        </Field>
        <Field label="Giờ đăng" required>
          <TextInput
            type="time"
            value={form.scheduledTime}
            onChange={(e) => set("scheduledTime", e.target.value)}
          />
        </Field>
      </div>

      <Field label="Thời lượng dự kiến" required hint="giây">
        <div className="flex flex-wrap gap-2.5">
          {DURATIONS.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => set("duration", d)}
              className={cn(
                "h-10 px-4 rounded-full border text-sm font-medium transition-all duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]",
                form.duration === d
                  ? "border-white bg-white text-black shadow-[0_0_15px_rgba(255,255,255,0.2)]"
                  : "border-white/10 bg-white/[0.02] text-slate-300 hover:border-white/20 hover:bg-white/[0.05]"
              )}
            >
              {d}s
            </button>
          ))}
        </div>
      </Field>
    </div>
  );
}

/* ---------- Step 2: Content ---------- */
function StepContent({
  form,
  set,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
}) {
  const [researching, setResearching] = useState(false);

  const doResearch = async () => {
    if (!form.searchKeyword.trim()) return;
    setResearching(true);
    try {
      const res = await api.post("/research/preview", {
        topic: form.searchKeyword,
        focus_points: form.content,
        duration: Number(form.duration) || 60,
      });
      const brief: ResearchBrief = {
        topic: res.topic || form.searchKeyword,
        summary: res.summary || "",
        stages: (res.stages || []).map((s: any) => ({ ...s, enabled: true })),
        key_facts: (res.key_facts || []).map((f: string) => ({ text: f, enabled: true })),
      };
      set("researchBrief", brief);
    } catch (e) {
      console.error(e);
      alert("Lỗi khi tìm hiểu chủ đề. Vui lòng thử lại.");
    } finally {
      setResearching(false);
    }
  };

  const updateStage = (id: number, field: string, value: any) => {
    if (!form.researchBrief) return;
    const stages = form.researchBrief.stages.map((s) =>
      s.id === id ? { ...s, [field]: value } : s
    );
    set("researchBrief", { ...form.researchBrief, stages });
  };

  const updateFact = (idx: number, field: string, value: any) => {
    if (!form.researchBrief) return;
    const key_facts = form.researchBrief.key_facts.map((f, i) =>
      i === idx ? { ...f, [field]: value } : f
    );
    set("researchBrief", { ...form.researchBrief, key_facts });
  };

  return (
    <div className="space-y-7">
      <Header
        title="Nội dung video"
        subtitle="Mô tả ý tưởng của bạn. Tùy chọn thêm ảnh để giữ nhân vật nhất quán."
      />

      <Field label="Ý tưởng / nội dung" required hint="tối thiểu 10 ký tự">
        <TextArea
          rows={5}
          placeholder="VD: Review 5 quán cà phê view đẹp ở Đà Nẵng, tập trung vào không gian và đồ uống signature..."
          value={form.content}
          onChange={(e) => set("content", e.target.value)}
        />
      </Field>

      {form.videoType === "entertainment" && (
        <div className="space-y-3">
          <Toggle
            checked={form.useGoogleData}
            onChange={(v) => set("useGoogleData", v)}
            label="Tự động bổ sung data từ Google"
            description="Tìm kiếm kiến thức nền về chủ đề để làm giàu kịch bản video"
          />
          {form.useGoogleData && (
            <div className="space-y-3">
              <Field label="Từ khóa tìm kiếm">
                <TextInput
                  placeholder="VD: quá trình hình thành trái dừa"
                  value={form.searchKeyword}
                  onChange={(e) => set("searchKeyword", e.target.value)}
                />
              </Field>
              <Button
                variant="outline"
                onClick={doResearch}
                disabled={researching || !form.searchKeyword.trim()}
              >
                {researching ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" /> Đang tìm hiểu...
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4 text-sky-400" /> Tìm hiểu chủ đề
                  </>
                )}
              </Button>
            </div>
          )}

          {form.researchBrief && (
            <div className="mt-4 space-y-4 rounded-xl border border-sky-400/20 bg-gradient-to-br from-sky-500/[0.04] to-indigo-500/[0.04] p-4">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-200">
                  Kết quả nghiên cứu: {form.researchBrief.topic}
                </h4>
                <Button variant="ghost" size="sm" onClick={doResearch} disabled={researching}>
                  <RotateCcw className={cn("h-3.5 w-3.5", researching && "animate-spin")} />
                  Tạo lại
                </Button>
              </div>

              {form.researchBrief.summary && (
                <textarea
                  value={form.researchBrief.summary}
                  onChange={(e) => set("researchBrief", { ...form.researchBrief!, summary: e.target.value })}
                  rows={2}
                  className="w-full resize-y rounded-md border border-transparent bg-transparent p-2 text-xs text-slate-400 transition-colors placeholder:text-slate-600 hover:border-white/10 hover:bg-white/[0.02] focus:border-sky-500/50 focus:bg-white/[0.03] focus:text-slate-200 focus:outline-none"
                />
              )}

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                    Các giai đoạn ({form.researchBrief.stages.filter(s => s.enabled).length}/{form.researchBrief.stages.length} đang chọn)
                  </p>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="h-6 text-[10px] text-sky-400"
                    onClick={() => {
                      if (!form.researchBrief) return;
                      const newId = Math.max(0, ...form.researchBrief.stages.map(s => s.id)) + 1;
                      set("researchBrief", {
                        ...form.researchBrief,
                        stages: [...form.researchBrief.stages, { id: newId, title: "Giai đoạn mới", detail: "", duration_hint: "Tùy chỉnh", enabled: true }]
                      });
                    }}
                  >
                    + Thêm giai đoạn
                  </Button>
                </div>
                {form.researchBrief.stages.map((stage) => (
                  <div
                    key={stage.id}
                    className={cn(
                      "flex gap-3 rounded-lg border p-3 transition-all",
                      stage.enabled
                        ? "border-white/10 bg-white/[0.03]"
                        : "border-white/5 bg-white/[0.01] opacity-50"
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={stage.enabled}
                      onChange={(e) => updateStage(stage.id, "enabled", e.target.checked)}
                      className="mt-1 h-4 w-4 rounded border-white/20 bg-white/5 accent-sky-500"
                    />
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          value={stage.title}
                          onChange={(e) => updateStage(stage.id, "title", e.target.value)}
                          className="flex-1 rounded border border-transparent bg-transparent px-1 text-sm font-medium text-slate-100 transition-colors placeholder:text-slate-600 hover:border-white/10 hover:bg-white/[0.02] focus:border-sky-500/50 focus:bg-white/[0.03] focus:outline-none"
                        />
                        {stage.duration_hint && (
                          <span className="shrink-0 text-[10px] text-slate-500">
                            {stage.duration_hint}
                          </span>
                        )}
                      </div>
                      <textarea
                        value={stage.detail}
                        onChange={(e) => updateStage(stage.id, "detail", e.target.value)}
                        rows={3}
                        className="w-full resize-y rounded border border-transparent bg-transparent p-1 text-xs text-slate-400 transition-colors placeholder:text-slate-600 hover:border-white/10 hover:bg-white/[0.02] focus:border-sky-500/50 focus:bg-white/[0.03] focus:text-slate-200 focus:outline-none"
                      />
                    </div>
                  </div>
                ))}
              </div>

              {form.researchBrief.key_facts && (
                <div className="space-y-2 mt-4">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                      Dữ kiện then chốt
                    </p>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="h-6 text-[10px] text-sky-400"
                      onClick={() => {
                        if (!form.researchBrief) return;
                        set("researchBrief", {
                          ...form.researchBrief,
                          key_facts: [...form.researchBrief.key_facts, { text: "Dữ kiện mới", enabled: true }]
                        });
                      }}
                    >
                      + Thêm dữ kiện
                    </Button>
                  </div>
                  {form.researchBrief.key_facts.map((fact, idx) => (
                    <div key={idx} className="flex items-start gap-2 mb-1">
                      <input
                        type="checkbox"
                        checked={fact.enabled}
                        onChange={(e) => updateFact(idx, "enabled", e.target.checked)}
                        className="mt-1 h-3.5 w-3.5 rounded border-white/20 bg-white/5 accent-sky-500"
                      />
                      <textarea
                        value={fact.text}
                        onChange={(e) => updateFact(idx, "text", e.target.value)}
                        rows={1}
                        className="flex-1 resize-y rounded border border-transparent bg-transparent px-1 py-0 text-xs text-slate-300 transition-colors placeholder:text-slate-600 hover:border-white/10 hover:bg-white/[0.02] focus:border-sky-500/50 focus:bg-white/[0.03] focus:text-slate-200 focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <Field label="Hình ảnh đính kèm" required hint="bắt buộc để render">
        <ImageUploader
          images={form.images}
          onChange={(imgs) => set("images", imgs)}
        />
      </Field>
    </div>
  );
}

/* ---------- Step 3: Style ---------- */
function StepStyle({
  form,
  set,
  styles,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
  styles: ReturnType<typeof stylesFor>;
}) {
  return (
    <div className="space-y-7">
      <Header
        title="Chọn phong cách"
        subtitle="Phong cách quyết định nhịp điệu, màu sắc và cảm xúc của video."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {styles.map((s) => {
          const selected = form.styleId === s.id;
          return (
              <button
              key={s.id}
              type="button"
              onClick={() => set("styleId", s.id)}
              className={cn(
                "group relative overflow-hidden rounded-[1.5rem] border text-left transition-all duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:-translate-y-1",
                selected
                  ? "border-white/20 bg-white/[0.08] shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),_0_8px_20px_rgba(255,255,255,0.05)]"
                  : "border-white/5 bg-white/[0.02] hover:border-white/15 hover:bg-white/[0.04]"
              )}
            >
              <div
                className={cn(
                  "flex h-32 items-center justify-center bg-gradient-to-br text-5xl transition-transform duration-500 group-hover:scale-105",
                  s.gradient
                )}
              >
                {s.emoji}
              </div>
              <div className="space-y-1.5 p-5">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-100 transition-colors group-hover:text-white">
                    {s.name}
                  </h4>
                  {selected && (
                    <CheckCircle2 className="h-5 w-5 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.5)]" />
                  )}
                </div>
                <p className="text-xs leading-relaxed text-slate-400">
                  {s.description}
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

/* ---------- Step 4: Caption ---------- */
function StepCaption({
  form,
  set,
  limit,
  ideas,
  loading,
  onSuggest,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
  limit: number;
  ideas: CaptionSuggestion[];
  loading: boolean;
  onSuggest: () => void;
}) {
  const len = form.caption.length;
  const over = len > limit;
  return (
    <div className="space-y-7">
      <Header
        title="Caption bài đăng"
        subtitle="Tự viết hoặc để AI gợi ý caption tối ưu theo nền tảng đã chọn."
      />

      <div className="flex flex-wrap items-center gap-3">
        <Button variant="outline" onClick={onSuggest} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Đang nghĩ...
            </>
          ) : (
            <>
              <Wand2 className="h-4 w-4 text-fuchsia-400" /> AI gợi ý caption
            </>
          )}
        </Button>
        <span className="text-xs text-slate-500">
          Tối ưu cho {form.channel === "facebook" ? "Facebook" : "TikTok"}
        </span>
      </div>

      {ideas.length > 0 && (
        <div className="space-y-2.5">
          {ideas.map((idea, i) => (
            <button
              key={i}
              type="button"
              onClick={() => set("caption", idea.text)}
              className="flex w-full items-start gap-3 rounded-xl border border-white/10 bg-white/[0.03] p-3.5 text-left transition-colors hover:border-indigo-400/40 hover:bg-indigo-500/[0.08]"
            >
              <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-fuchsia-400" />
              <span className="space-y-1">
                <span className="block text-xs font-medium uppercase tracking-wide text-sky-400">
                  {idea.tone}
                </span>
                <span className="block text-sm text-slate-200">
                  {idea.text}
                </span>
              </span>
            </button>
          ))}
        </div>
      )}

      <Field label="Caption" required>
        <TextArea
          rows={5}
          placeholder="Nhập caption hoặc chọn một gợi ý phía trên..."
          value={form.caption}
          onChange={(e) => set("caption", e.target.value)}
        />
        <div className="flex justify-end">
          <span
            className={cn(
              "text-xs",
              over ? "text-red-400" : "text-slate-500"
            )}
          >
            {len.toLocaleString()} / {limit.toLocaleString()}
          </span>
        </div>
      </Field>
    </div>
  );
}

/* ---------- Step 5: Review ---------- */
function StepReview({
  form,
  loadingPrompt,
  onRegenerate,
}: {
  form: CreateVideoForm;
  loadingPrompt: boolean;
  onRegenerate: () => void;
}) {
  const style = stylesFor(form.videoType).find((s) => s.id === form.styleId);
  return (
    <div className="space-y-7">
      <Header
        title="Xem lại & xác nhận"
        subtitle="Kiểm tra thông tin trước khi tạo video và lên lịch đăng."
      />

      <div className="grid gap-3 sm:grid-cols-2">
        <Summary label="Loại video" value={form.videoType === "ads" ? "Quảng cáo" : "Giải trí"} />
        <Summary label="Kênh đăng" value={form.channel === "facebook" ? "Facebook" : "TikTok"} />
        <Summary label="Lịch đăng" value={`${form.scheduledDate} · ${form.scheduledTime}`} />
        <Summary label="Thời lượng" value={form.duration ? `${form.duration}s` : "-"} />
        <Summary label="Phong cách" value={style?.name ?? "-"} />
        <Summary label="Số ảnh đính kèm" value={`${form.images.length} ảnh`} />
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-200">Nội dung</p>
        <p className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 text-sm text-slate-300">
          {form.content}
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-200">Caption</p>
        <p className="whitespace-pre-wrap rounded-xl border border-white/10 bg-white/[0.03] p-3.5 text-sm text-slate-300">
          {form.caption}
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <p className="flex items-center gap-1.5 text-sm font-medium text-slate-200">
            <Sparkles className="h-4 w-4 text-fuchsia-400" /> Prompt do AI sinh ra
          </p>
          <Button
            variant="ghost"
            size="sm"
            onClick={onRegenerate}
            disabled={loadingPrompt}
          >
            <RotateCcw className={cn("h-3.5 w-3.5", loadingPrompt && "animate-spin")} />
            Tạo lại
          </Button>
        </div>
        <div className="rounded-xl border border-indigo-400/20 bg-gradient-to-br from-sky-500/[0.06] to-fuchsia-500/[0.06] p-4">
          {loadingPrompt ? (
            <div className="flex items-center gap-2 text-sm text-indigo-300">
              <Loader2 className="h-4 w-4 animate-spin" /> Đang sinh prompt...
            </div>
          ) : (
            <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
              {form.generatedPrompt || "Prompt sẽ được sinh khi bạn tới bước này."}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Shared bits ---------- */
function Header({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="space-y-1">
      <h2 className="text-xl font-semibold text-white">{title}</h2>
      <p className="text-sm text-slate-400">{subtitle}</p>
    </div>
  );
}

function Summary({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-0.5 text-sm font-medium text-slate-100">{value}</p>
    </div>
  );
}

function SuccessScreen({
  form,
  onReset,
}: {
  form: CreateVideoForm;
  onReset: () => void;
}) {
  const router = useRouter();

  return (
    <Card className="animate-fade-in p-10 text-center">
      <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/15 ring-1 ring-emerald-400/30">
        <CheckCircle2 className="h-8 w-8 text-emerald-400" />
      </div>
      <h2 className="text-2xl font-semibold text-white">
        Đã gửi yêu cầu thành công!
      </h2>
      <p className="mx-auto mt-2 max-w-md text-sm text-slate-400">
        Video đang được tạo bằng MarkX. Hệ thống sẽ tự động đăng lên{" "}
        {form.channel === "facebook" ? "Facebook" : "TikTok"} vào{" "}
        <span className="font-medium text-slate-200">
          {form.scheduledDate} lúc {form.scheduledTime}
        </span>
        .
      </p>
      <div className="mt-7 flex flex-col sm:flex-row items-center justify-center gap-3">
        <Button onClick={onReset} className="group active:scale-[0.98] transition-all">
          <Sparkles className="h-4 w-4 mr-2" /> Tạo video mới
        </Button>
        <Button variant="outline" onClick={() => router.push("/history")} className="group active:scale-[0.98] transition-all">
          Xem lịch sử
        </Button>
      </div>
    </Card>
  );
}
