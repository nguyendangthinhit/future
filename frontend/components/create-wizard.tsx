"use client";

import { useMemo, useState } from "react";
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
} from "lucide-react";
import { cn } from "@/lib/utils";

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
      const res = await fetch("/api/prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: form.content,
          videoType: form.videoType,
          duration: form.duration,
          styleId: form.styleId,
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

  async function suggestCaption() {
    setGenningCaption(true);
    try {
      const res = await fetch("/api/caption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: form.content,
          channel: form.channel,
          styleId: form.styleId,
          videoType: form.videoType,
        }),
      });
      const data = await res.json();
      setCaptionIdeas(data.suggestions ?? []);
    } catch {
      setCaptionIdeas([]);
    } finally {
      setGenningCaption(false);
    }
  }

  async function submit() {
    setSubmitting(true);
    if (!form.generatedPrompt) await generatePrompt();
    // Giả lập gọi backend — API thật sẽ cắm sau
    await new Promise((r) => setTimeout(r, 1200));
    setSubmitting(false);
    setSubmitted(true);
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
    <div className="space-y-8">
      <Card className="px-5 py-5 sm:px-8">
        <Stepper
          steps={STEPS}
          current={step}
          maxReached={maxReached}
          onStepClick={goTo}
        />
      </Card>

      <Card className="animate-fade-in p-6 sm:p-8" key={step}>
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

      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={back}
          disabled={step === 0}
          className={cn(step === 0 && "invisible")}
        >
          <ArrowLeft className="h-4 w-4" /> Quay lại
        </Button>

        {step < STEPS.length - 1 ? (
          <div className="flex items-center gap-3">
            {missing.length > 0 && (
              <span className="hidden text-xs text-slate-400 sm:block">
                Còn thiếu: {missing.join(", ")}
              </span>
            )}
            <Button onClick={next} disabled={!canNext}>
              Tiếp tục <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <Button onClick={submit} disabled={submitting} size="lg">
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Đang gửi...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" /> Tạo video & lên lịch
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
  const durations = form.videoType ? DURATIONS[form.videoType] : [];
  return (
    <div className="space-y-7">
      <Header
        title="Cấu hình cơ bản"
        subtitle="Chọn loại video, kênh đăng và thời điểm bạn muốn xuất bản."
      />

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
            description="30 / 60 / 90 giây"
            icon={<Clapperboard className="h-5 w-5 text-sky-400" />}
          />
          <OptionCard
            selected={form.videoType === "ads"}
            onClick={() => {
              set("videoType", "ads");
              set("duration", null);
              set("styleId", null);
            }}
            title="Quảng cáo"
            description="15 / 30 / 60 giây"
            icon={<Megaphone className="h-5 w-5 text-fuchsia-400" />}
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

      <Field label="Thời lượng" required hint="giây">
        <div className="flex flex-wrap gap-3">
          {durations.length === 0 && (
            <p className="text-sm text-slate-500">
              Chọn loại video để xem các mức thời lượng.
            </p>
          )}
          {durations.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => set("duration", d)}
              className={cn(
                "h-11 w-20 rounded-xl border text-sm font-semibold transition-all",
                form.duration === d
                  ? "border-indigo-400/60 bg-gradient-to-br from-sky-500/15 to-fuchsia-500/15 text-white ring-2 ring-indigo-500/30"
                  : "border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/25"
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
            description="Lấy thông tin & trend mới nhất để làm giàu kịch bản"
          />
          {form.useGoogleData && (
            <Field label="Từ khóa tìm kiếm">
              <TextInput
                placeholder="VD: cà phê Đà Nẵng 2026"
                value={form.searchKeyword}
                onChange={(e) => set("searchKeyword", e.target.value)}
              />
            </Field>
          )}
        </div>
      )}

      <Field label="Hình ảnh đính kèm" hint="tùy chọn">
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
                "group overflow-hidden rounded-2xl border text-left transition-all duration-150",
                selected
                  ? "border-indigo-400/60 ring-2 ring-indigo-500/30"
                  : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:-translate-y-0.5"
              )}
            >
              <div
                className={cn(
                  "flex h-28 items-center justify-center bg-gradient-to-br text-4xl",
                  s.gradient
                )}
              >
                {s.emoji}
              </div>
              <div className="space-y-1 p-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-semibold text-slate-100">
                    {s.name}
                  </h4>
                  {selected && (
                    <CheckCircle2 className="h-4 w-4 text-indigo-400" />
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
        <Summary label="Thời lượng" value={`${form.duration}s`} />
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
  return (
    <Card className="animate-fade-in p-10 text-center">
      <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/15 ring-1 ring-emerald-400/30">
        <CheckCircle2 className="h-8 w-8 text-emerald-400" />
      </div>
      <h2 className="text-2xl font-semibold text-white">
        Đã gửi yêu cầu thành công!
      </h2>
      <p className="mx-auto mt-2 max-w-md text-sm text-slate-400">
        Video đang được tạo bằng ViMax. Hệ thống sẽ tự động đăng lên{" "}
        {form.channel === "facebook" ? "Facebook" : "TikTok"} vào{" "}
        <span className="font-medium text-slate-200">
          {form.scheduledDate} lúc {form.scheduledTime}
        </span>
        .
      </p>
      <div className="mt-7">
        <Button onClick={onReset}>
          <Sparkles className="h-4 w-4" /> Tạo video mới
        </Button>
      </div>
    </Card>
  );
}
