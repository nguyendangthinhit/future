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
  PlayCircle,
  PauseCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const STEPS = ["Cấu hình", "Nội dung", "Nhân vật", "Phong cách", "Xem lại"];

const FB_LIMIT = 63206;
const TIKTOK_LIMIT = 2200;

const emptyForm: CreateVideoForm = {
  videoType: null,
  duration: null,
  targetLanguage: "Vietnamese",
  content: "",
  useGoogleData: false,
  searchKeyword: "",
  engineType: "mascot",
  avatarId: "",
  voiceId: "",
  images: [],
  styleId: null,
  generatedPrompt: "",
  researchBrief: null,
};

export function CreateWizard() {
  const [step, setStep] = useState(0);
  const [maxReached, setMaxReached] = useState(0);
  const [form, setForm] = useState<CreateVideoForm>(emptyForm);

  const [genningPrompt, setGenningPrompt] = useState(false);
  
  
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
  

  const goTo = (i: number) => {
    setStep(i);
    setMaxReached((m) => Math.max(m, i));
  };

  const missing = useMemo(() => {
    const m: string[] = [];
    switch (step) {
      case 0:
        if (!form.videoType) m.push("loại video");
        if (!form.duration) m.push("thời lượng");
        if (!form.targetLanguage) m.push("ngôn ngữ");
        break;
      case 1:
        if (form.content.trim().length < 10) m.push("nội dung (≥ 10 ký tự)");
        break;
      case 2:
        if (form.engineType === "mascot" && form.images.length === 0) m.push("ảnh đính kèm");
        if (form.engineType === "avatar" && !form.avatarId) m.push("chọn avatar");
        break;
      case 3:
        if (!form.styleId) m.push("phong cách");
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
      if (!res.ok) {
        alert(data.error || "Lỗi tạo prompt từ AI");
      } else {
        set("generatedPrompt", data.prompt ?? "");
      }
    } catch (e: any) {
      alert("Không thể kết nối đến máy chủ: " + e.message);
    } finally {
      setGenningPrompt(false);
    }
  }

  
  async function submit() {
    setSubmitting(true);
    try {
      if (!form.generatedPrompt) await generatePrompt();
      
      const formData = new FormData();
      formData.append("video_type", form.videoType || "");
      formData.append("engine_type", form.engineType);
      if (form.avatarId) formData.append("avatar_id", form.avatarId);
      if (form.voiceId) formData.append("voice_id", form.voiceId);
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

      formData.append("target_language", form.targetLanguage);
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
              {step === 2 && <StepEngine form={form} set={set} />}
              {step === 3 && (
                <StepStyle
                  form={form}
                  set={set}
                  styles={availableStyles}
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
          subtitle="Chọn loại video và thời lượng mong muốn."
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

      <div className="grid gap-5 sm:grid-cols-2">
        <Field label="Ngôn ngữ Video" required>
          <select
            value={form.targetLanguage}
            onChange={(e) => set("targetLanguage", e.target.value)}
            className="w-full h-11 rounded-xl border border-white/10 bg-white/[0.03] px-3.5 text-sm text-slate-200 transition-colors placeholder:text-slate-500 hover:border-white/20 focus:border-sky-500/50 focus:bg-white/[0.05] focus:outline-none"
          >
            <option value="Vietnamese">🇻🇳 Vietnam (Tiếng Việt)</option>
            <option value="English (US)">🇺🇸 USA (English)</option>
            <option value="Japanese">🇯🇵 Japan (Tiếng Nhật)</option>
            <option value="Chinese">🇨🇳 China (Tiếng Trung)</option>
            <option value="Korean">🇰🇷 Korea (Tiếng Hàn)</option>
            <option value="English (UK)">🇬🇧 UK (English)</option>
            <option value="Thai">🇹🇭 Thailand (Tiếng Thái)</option>
            <option value="English (Singapore)">🇸🇬 Singapore (English)</option>
            <option value="German">🇩🇪 German (Tiếng Đức)</option>
            <option value="French">🇫🇷 France (Tiếng Pháp)</option>
            <option value="Arabic">🇦🇪 UAE (Tiếng Ả Rập)</option>
          </select>
        </Field>
        
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
        subtitle="Mô tả ý tưởng của bạn. Kịch bản sẽ được sinh tự động."
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

      
    </div>
  );
}

/* ---------- Step 2.5: Engine ---------- */
import { useEffect } from "react";
function StepEngine({
  form,
  set,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
}) {
  const [avatars, setAvatars] = useState<any[]>([]);
  const [voices, setVoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [playingVoiceId, setPlayingVoiceId] = useState<string | null>(null);
  const [audioRef, setAudioRef] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Cleanup audio on unmount
    return () => {
      if (audioRef) {
        audioRef.pause();
      }
    };
  }, [audioRef]);

  const toggleAudio = (e: React.MouseEvent, voiceId: string, url: string) => {
    e.stopPropagation(); // Ngăn việc click vào play lại kích hoạt chọn voice
    if (playingVoiceId === voiceId && audioRef) {
      audioRef.pause();
      setPlayingVoiceId(null);
    } else {
      if (audioRef) audioRef.pause();
      const newAudio = new Audio(url);
      newAudio.play();
      newAudio.onended = () => setPlayingVoiceId(null);
      setAudioRef(newAudio);
      setPlayingVoiceId(voiceId);
    }
  };

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const [avRes, voRes] = await Promise.all([
          api.get("/video/avatars"),
          api.get("/video/voices")
        ]);
        if (avRes && Array.isArray(avRes)) setAvatars(avRes);
        if (voRes && Array.isArray(voRes)) {
          setVoices(voRes);
          // Auto select first voice if not selected
          if (!form.voiceId && voRes.length > 0) {
            set("voiceId", voRes[0].voice_id);
          }
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="space-y-7">
      <Header
        title="Chọn nhân vật"
        subtitle="Chọn chế độ tạo hình: Dùng ảnh tuỳ chỉnh (Kling) hoặc Avatar nhép miệng (Ecomdy)."
      />

      <Field label="Công nghệ tạo hình" required>
        <div className="grid gap-3 sm:grid-cols-2">
          <OptionCard
            selected={form.engineType === "mascot"}
            onClick={() => {
              set("engineType", "mascot");
              set("avatarId", "");
            }}
            title="Mascot / Ảnh tuỳ chỉnh"
            description="Tải lên ảnh 1 nhân vật hoặc phong cảnh để làm video câm."
            icon={<span className="text-2xl drop-shadow-md">🖼️</span>}
          />
          <OptionCard
            selected={form.engineType === "avatar"}
            onClick={() => set("engineType", "avatar")}
            title="Avatar nhép miệng"
            description="Sử dụng AIGC Avatar có sẵn để tạo video người thật nhép miệng."
            icon={<span className="text-2xl drop-shadow-md">🗣️</span>}
          />
        </div>
      </Field>

      {form.engineType === "mascot" && (
        <div className="animate-fade-in mt-4">
          <Field label="Tải lên ảnh Mascot / Phong cảnh" required hint="1 ảnh">
            <ImageUploader
              images={form.images}
              onChange={(imgs) => set("images", imgs)}
            />
          </Field>
        </div>
      )}

      {form.engineType === "avatar" && (
        <div className="animate-fade-in mt-4 space-y-3">
          <Field label="Chọn Avatar" required>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" /> Đang tải danh sách...
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-5 max-h-96 overflow-y-auto pr-2 pb-2">
                {avatars.map((av) => (
                  <button
                    key={av.avatar_id}
                    type="button"
                    onClick={() => set("avatarId", av.avatar_id)}
                    className={cn(
                      "group relative overflow-hidden rounded-xl border-2 transition-all duration-300",
                      form.avatarId === av.avatar_id
                        ? "border-sky-400"
                        : "border-transparent hover:border-white/20"
                    )}
                  >
                    <img src={av.avatar_thumbnail} alt={av.avatar_name} className="w-full h-auto aspect-square object-cover" />
                    <div className="absolute inset-x-0 bottom-0 bg-black/60 p-1.5 text-center text-xs text-white">
                      {av.avatar_name}
                    </div>
                    {form.avatarId === av.avatar_id && (
                      <div className="absolute top-1 right-1 bg-sky-500 rounded-full p-0.5">
                        <CheckCircle2 className="h-3 w-3 text-white" />
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </Field>
          
          <Field label="Chọn Giọng Đọc (Voice)" required>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Loader2 className="h-4 w-4 animate-spin" /> Đang tải danh sách...
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {voices.map((voice) => (
                  <button
                    key={voice.voice_id}
                    type="button"
                    onClick={() => set("voiceId", voice.voice_id)}
                    className={cn(
                      "flex items-center justify-between p-3 rounded-xl border-2 text-left transition-all duration-300",
                      form.voiceId === voice.voice_id
                        ? "border-sky-400 bg-sky-500/10"
                        : "border-white/10 hover:border-white/20 bg-white/5"
                    )}
                  >
                    <div>
                      <div className="text-sm font-semibold text-slate-200">
                        {voice.voice_name}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">
                        {voice.language} • {voice.gender === "female" ? "Nữ" : "Nam"}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {voice.preview_url && (
                        <button
                          type="button"
                          onClick={(e) => toggleAudio(e, voice.voice_id, voice.preview_url)}
                          className="p-1 rounded-full hover:bg-white/10 transition-colors"
                        >
                          {playingVoiceId === voice.voice_id ? (
                            <PauseCircle className="h-5 w-5 text-sky-400" />
                          ) : (
                            <PlayCircle className="h-5 w-5 text-slate-400 hover:text-white" />
                          )}
                        </button>
                      )}
                      {form.voiceId === voice.voice_id && (
                        <CheckCircle2 className="h-5 w-5 text-sky-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </Field>
        </div>
      )}
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
        subtitle="Kiểm tra thông tin trước khi tạo video."
      />

      <div className="grid gap-3 sm:grid-cols-2">
        <Summary label="Loại video" value={form.videoType === "ads" ? "Quảng cáo" : "Giải trí"} />
        <Summary label="Thời lượng" value={form.duration ? `${form.duration}s` : "-"} />
        <Summary label="Phong cách" value={style?.name ?? "-"} />
        <Summary label="Kiểu nhân vật" value={form.engineType === "mascot" ? "Mascot tuỳ chỉnh (Kling)" : "Avatar (Lip-sync)"} />
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium text-slate-200">Nội dung</p>
        <p className="rounded-xl border border-white/10 bg-white/[0.03] p-3.5 text-sm text-slate-300">
          {form.content}
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
        Video đang được tạo bằng MarkX. Quá trình này có thể mất vài phút. Bạn có thể xem trạng thái ở mục Lịch sử và tải file subtitle (.srt).
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
