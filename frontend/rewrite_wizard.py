import re

with open("d:/future/frontend/components/create-wizard.tsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update STEPS
content = content.replace('const STEPS = ["Cấu hình", "Nội dung", "Phong cách", "Caption", "Xem lại"];', 'const STEPS = ["Cấu hình", "Nội dung", "Nhân vật", "Phong cách", "Xem lại"];')

# 2. Update emptyForm
empty_form_str = """const emptyForm: CreateVideoForm = {
  videoType: null,
  duration: null,
  content: "",
  useGoogleData: false,
  searchKeyword: "",
  engineType: "mascot",
  avatarId: "",
  images: [],
  styleId: null,
  generatedPrompt: "",
  researchBrief: null,
};"""
content = re.sub(r'const emptyForm: CreateVideoForm = \{[^}]+\};', empty_form_str, content)

# 3. Update missing validation
missing_old = """    switch (step) {
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
    }"""
missing_new = """    switch (step) {
      case 0:
        if (!form.videoType) m.push("loại video");
        if (!form.duration) m.push("thời lượng");
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
    }"""
content = content.replace(missing_old, missing_new)

# 4. Remove Generate Caption, Update Submit
content = re.sub(r'const suggestCaption = async \(\) => \{.*?\};\n', '', content, flags=re.DOTALL)
content = content.replace('const [genningCaption, setGenningCaption] = useState(false);', '')
content = content.replace('const [captionIdeas, setCaptionIdeas] = useState<CaptionSuggestion[]>([]);', '')
content = content.replace('setCaptionIdeas([]);', '')
content = content.replace('const captionLimit = form.channel === "facebook" ? FB_LIMIT : TIKTOK_LIMIT;', '')

# Submit form data
submit_old = """      const formData = new FormData();
      formData.append("video_type", form.videoType || "");
      formData.append("channel", form.channel || "");
      formData.append("scheduled_date", form.scheduledDate);
      formData.append("raw_content", form.content);
      formData.append("style_id", form.styleId || "");"""
submit_new = """      const formData = new FormData();
      formData.append("video_type", form.videoType || "");
      formData.append("engine_type", form.engineType);
      if (form.avatarId) formData.append("avatar_id", form.avatarId);
      formData.append("raw_content", form.content);
      formData.append("style_id", form.styleId || "");"""
content = content.replace(submit_old, submit_new)

# 5. Update UI rendering steps
ui_steps_old = """              {step === 0 && <StepConfig form={form} set={set} />}
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
              )}"""
ui_steps_new = """              {step === 0 && <StepConfig form={form} set={set} />}
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
              )}"""
content = content.replace(ui_steps_old, ui_steps_new)

# 6. Rewrite StepConfig
step1_regex = r'/\* ---------- Step 1: Config ---------- \*/.*?/\* ---------- Step 2: Content ---------- \*/'
step1_new = """/* ---------- Step 1: Config ---------- */
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

/* ---------- Step 2: Content ---------- */"""
content = re.sub(step1_regex, step1_new, content, flags=re.DOTALL)

# Remove ImageUploader from Step 2
content = re.sub(r'<Field label="Hình ảnh đính kèm" required hint="bắt buộc để render">.*?</Field>', '', content, flags=re.DOTALL)
content = content.replace('Mô tả ý tưởng của bạn. Tùy chọn thêm ảnh để giữ nhân vật nhất quán.', 'Mô tả ý tưởng của bạn. Kịch bản sẽ được sinh tự động.')

# Rewrite Review
step_review_regex = r'/\* ---------- Step 5: Review ---------- \*/.*?/\* ---------- Shared bits ---------- \*/'
step_review_new = """/* ---------- Step 5: Review ---------- */
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

/* ---------- Shared bits ---------- */"""
content = re.sub(step_review_regex, step_review_new, content, flags=re.DOTALL)

# Rewrite SuccessScreen
success_regex = r'function SuccessScreen\(\{.*?\}\) \{.*?\}'
success_new = """function SuccessScreen({
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
}"""
content = re.sub(success_regex, success_new, content, flags=re.DOTALL)

# Add StepEngine Component
step_engine = """/* ---------- Step 2.5: Engine ---------- */
import { useEffect } from "react";
function StepEngine({
  form,
  set,
}: {
  form: CreateVideoForm;
  set: <K extends keyof CreateVideoForm>(k: K, v: CreateVideoForm[K]) => void;
}) {
  const [avatars, setAvatars] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchAvatars() {
      setLoading(true);
      try {
        const res = await api.get("/video/avatars");
        if (res && Array.isArray(res)) {
          setAvatars(res);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchAvatars();
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
                    key={av.id}
                    type="button"
                    onClick={() => set("avatarId", av.id)}
                    className={cn(
                      "group relative overflow-hidden rounded-xl border-2 transition-all duration-300",
                      form.avatarId === av.id
                        ? "border-sky-400"
                        : "border-transparent hover:border-white/20"
                    )}
                  >
                    <img src={av.avatar_image} alt={av.name} className="w-full h-auto aspect-square object-cover" />
                    <div className="absolute inset-x-0 bottom-0 bg-black/60 p-1.5 text-center text-xs text-white">
                      {av.name}
                    </div>
                    {form.avatarId === av.id && (
                      <div className="absolute top-1 right-1 bg-sky-500 rounded-full p-0.5">
                        <CheckCircle2 className="h-3 w-3 text-white" />
                      </div>
                    )}
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
"""

content = re.sub(r'/\* ---------- Step 3: Style ---------- \*/', step_engine + '\n/* ---------- Step 3: Style ---------- */', content)

# Remove StepCaption completely
content = re.sub(r'/\* ---------- Step 4: Caption ---------- \*/.*?/\* ---------- Step 5: Review ---------- \*/', '/* ---------- Step 5: Review ---------- */', content, flags=re.DOTALL)

with open("d:/future/frontend/components/create-wizard.tsx", "w", encoding="utf-8") as f:
    f.write(content)
print("Rewrite complete")
