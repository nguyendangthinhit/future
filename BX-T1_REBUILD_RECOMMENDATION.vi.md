# BX-T1 – Content Creation Video Factory: Khuyến Nghị Xây Dựng Lại

> **Hackathon track:** BX-T1 · **Nhà tài trợ:** BytePlus × TRAE
> **Một câu tóm tắt:** Đưa brief vào → xuất ra 2 phiên bản TikTok sẵn sàng đăng trong <60 phút, ≥80% biên tập viên đánh giá là có thể đăng.
> **Đối tượng đọc tài liệu này:** team sẽ xây dựng, demo và chấm điểm bản rebuild.

---

## 1. Tóm tắt điều hành

Bạn đã có một skeleton hoạt động (`backend/` FastAPI + `frontend/` Next.js + n8n + Sheets/Drive). Để thắng BX-T1, bản rebuild cần **ngừng là "wrapper API render video" và trở thành một content factory có agent được điều phối bởi TRAE**, có thể quan sát được ở các điểm sau:

1. **Đa agent** – planner, copywriter, director, storyboarder, voice, edit, QA.
2. **Khóa thương hiệu** – mọi biến thể đều tôn trọng bộ nhận diện (logo, bảng màu, font, voice, claims).
3. **Đúng chuẩn nền tảng** – TikTok / Reels / Shorts (9:16, 1:1, 15-30s, sub cứng, caption native).
4. **Sẵn sàng A/B** – ≥2 hướng sáng tạo khác biệt cho mỗi brief với mã biến thể đo lường được.
5. **Chạy lại được** – giám khảo có thể clone workflow TRAE, paste một brief và tái tạo kết quả.

Khuyến nghị dưới đây là **kế hoạch rebuild theo pha** (P0 → P1 → P2) với các thay đổi file cụ thể, mẫu prompt và cổng chấp nhận. Nó tận dụng hạ tầng hiện có (Sheets/Drive làm content store, FastAPI làm orchestrator, Next.js làm control plane) và **bổ sung** các mảnh ghép còn thiếu: Seedance 2.0 (T2V/I2V/R2V), Seed 2.0 (ModelArk) cho script/copy, ElevenLabs/TTS cho VO, Whisper + burn-in cho sub, và một template workflow TRAE như một deliverable hạng nhất.

---

## 2. Kiểm tra trạng thái hiện tại (giữ gì, loại bỏ gì)

**Giữ lại (vẫn có giá trị):**
- `backend/main.py` – bootstrap FastAPI, đăng ký router, lifespan APScheduler.
- `backend/services/sheets.py`, `drive_service.py` – content store + asset CDN (hoàn hảo cho "thư viện tài sản thương hiệu").
- `backend/routers/verify.py` – workflow duyệt ý tưởng ánh xạ thành cổng "duyệt biến thể A/B".
- `frontend/components/create-wizard.tsx` – vỏ tốt cho form nhập brief.
- `frontend/app/{dashboard,history,verify,schedule}` – tái sử dụng cho editor console.
- `n8n/n8n_workflow_template.json` – phát triển thành "template điều phối TRAE".

**Viết lại / thay thế:**
- `backend/routers/video.py` – hiện tại chỉ là pipeline render đơn. Thay bằng một **orchestrator đa agent** chạy song song 2 biến thể.
- `backend/services/agents/{scriptwriter,director,pipeline}.py` – hiện là chuỗi 2 bước. Mở rộng thành 6+ agent chuyên biệt (xem §4).
- `backend/services/llm_manager.py`, `ecomdy.py` – tách thành `model_gateway/` chung để route giữa **Seed 2.0 (ModelArk) cho text** và **Seedance 2.0 cho video** (bắt buộc).
- `frontend/app/page.tsx` + `create-wizard.tsx` – cần **Brief Schema** với brand kit, audience, platform, hard constraints và **Variant Selector** ở cuối.

**Bổ sung (mới, bắt buộc cho brief):**
- `backend/services/seedance/` – client Seedance 2.0 (chế độ T2V / I2V / R2V).
- `backend/services/seed2/` – client Seed 2.0 (ModelArk) cho hook/script/caption/title A/B.
- `backend/services/voice/` – ElevenLabs hoặc TTS tương thích với chọn brand voice.
- `backend/services/subtitles/` – Whisper transcribe + burn-in renderer (FFmpeg `subtitles` filter + style preset).
- `backend/services/brand_kit/` – overlay logo, trích màu, load font, kiểm tra tuân thủ claims.
- `backend/services/qa/` – editor-rubric scorer (publishability 0-100) để chạy cổng ≥80%.
- `trae/workflows/content-factory.trae.json` – **deliverable hạng nhất**, mirror DAG agent để giám khảo clone & chạy lại.
- `docs/WORKFLOW.md` – tài liệu workflow 1 trang (deliverable).

---

## 3. Kiến trúc mục tiêu (điều phối bởi TRAE)

```
                ┌──────────────────────┐
                │  Brief vào (UI/API)  │
                │  theme, brand kit,   │
                │  audience, platform, │
                │  hard constraints    │
                └──────────┬───────────┘
                           │
                ┌──────────▼───────────┐
                │   Planner Agent      │  ← Seed 2.0 (ModelArk)
                │ 2 hướng sáng tạo     │
                │ kế hoạch A/B         │
                └──────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ Crew biến thể A  │       │ Crew biến thể B  │
   │ copy → storyboard│       │ copy → storyboard│
   │ → shot list      │       │ → shot list      │
   └────────┬─────────┘       └────────┬─────────┘
            ▼                          ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ Seedance 2.0     │       │ Seedance 2.0     │
   │ T2V / I2V / R2V  │       │ T2V / I2V / R2V  │
   └────────┬─────────┘       └────────┬─────────┘
            ▼                          ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ ElevenLabs VO    │       │ ElevenLabs VO    │
   │ + Whisper subs   │       │ + Whisper subs   │
   │ + brand overlay  │       │ + brand overlay  │
   └────────┬─────────┘       └────────┬─────────┘
            ▼                          ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ QA / Rubric      │       │ QA / Rubric      │
   │ publishable ≥80% │       │ publishable ≥80% │
   └────────┬─────────┘       └────────┬─────────┘
            ▼                          ▼
            └────────────┬─────────────┘
                         ▼
              ┌──────────────────────┐
              │ Export Pack          │
              │ 9:16 + 1:1, SRT,     │
              │ cover, caption,      │
              │ kết quả A/B          │
              └──────────────────────┘
```

**Tại sao hình dạng này thắng brief:**
- "TRAE orchestration phải nhìn thấy được" → DAG ở trên chính là thứ mà `trae/workflows/content-factory.trae.json` mô tả; UI có thể render cùng DAG với trạng thái trực tiếp.
- "≥2 hướng sáng tạo với thiết lập A/B" → Planner rẽ thành 2 crew chạy cô lập, mỗi crew có quyết định copy/visual/voice riêng và một variant ID được đóng dấu lên mọi frame.
- "Brief → 2 biến thể trong <60 phút" → các biến thể chạy **song song** (asyncio.gather giữa 2 crew), Seedance T2V là điểm nghẽn, nên ta giữ dưới 4 phút mỗi shot và giới hạn 6 shot/biến thể.
- "≥80% editor-rated publishable" → rubric QA chặn export; chỉ biến thể đạt ≥80 mới tự động được đưa vào pack, các biến thể khác quay lại Director để sửa nhanh.

---

## 4. Danh sách agent (mỗi agent là một prompt nhỏ, tập trung)

| # | Agent | Model | Trách nhiệm | Output |
|---|---|---|---|---|
| 1 | **Planner** | Seed 2.0 | Phân rã brief thành 2 góc sáng tạo khác biệt, định nghĩa giả thuyết A/B | `plan.json` |
| 2 | **Brand Steward** | Seed 2.0 | Khóa palette, font, vị trí logo, whitelist/blacklist claims, tone-of-voice | `brand_lock.json` |
| 3 | **Copywriter** | Seed 2.0 | Hook variants (A/B/C), script 15-30s, CTA, on-screen text | `script.json` |
| 4 | **Director** | Seed 2.0 | Shot list: A-roll/B-roll theo cảnh, transition, pacing | `storyboard.json` |
| 5 | **Visualist** | Seed 2.0 | Visual prompt theo shot tinh chỉnh cho Seedance 2.0 (T2V/I2V/R2V) | `shots.json` |
| 6 | **Renderer** | Seedance 2.0 | Sinh clip thô (async, song song giữa các shot) | `clip_*.mp4` |
| 7 | **Voice** | ElevenLabs / TTS | VO cho mỗi biến thể theo brand voice | `vo.mp3` |
| 8 | **Subtitler** | Whisper | Transcribe VO, burn-in sub cứng theo style thương hiệu | `subs.srt` + `video_with_subs.mp4` |
| 9 | **Editor** | FFmpeg | Nối clip, transition, overlay logo, color grade, export 9:16 + 1:1 | `final_*.mp4` |
| 10 | **QA / Editor-in-Chief** | Seed 2.0 | Chấm 0-100 theo rubric (hook, pace, brand, compliance, audio). Loại <80. | `qa.json` |
| 11 | **Packer** | Internal | Cover art (Seed 2.0 image), caption, title, hashtag, gợi ý lịch đăng | `pack.json` |

**Quy tắc hiển thị TRAE:** mọi agent phải (a) ghi một hàng trạng thái vào Sheets, (b) phát ra sự kiện `trace.jsonl` để UI stream, và (c) là một node trong `content-factory.trae.json`.

---

## 5. Brief Schema (hợp đồng frontend ↔ backend)

Đây là nguồn sự thật duy nhất. Định nghĩa một lần trong `frontend/lib/types.ts` và mirror thành Pydantic model trong `backend/models/brief.py`.

```ts
type Brief = {
  theme: string;            // "F&B: cà phê sữa đá Việt Nam, ra mắt gen-z"
  brand: {
    name: string;
    toneOfVoice: string;    // "vui tươi, tự tin, hài hước"
    palette: { primary: string; accent: string; bg: string };
    fonts: { display: string; body: string };
    logoUrl: string;
    voiceId: string;        // id giọng ElevenLabs
    claimsAllowed: string[];
    claimsForbidden: string[];
  };
  audience: { segment: string; age: string; locale: string };
  platform: "tiktok" | "reels" | "shorts" | "all";
  constraints: {
    lengthSec: 15 | 20 | 30;
    aspect: ("9:16" | "1:1")[];
    mustInclude: string[];
    mustAvoid: string[];
  };
  moodboardUrls?: string[];
  variantsTarget: 1 | 2;     // mặc định 2
};
```

**Quy tắc cứng:** nếu `claimsForbidden` khớp bất cứ thứ gì trong script, QA tự động loại. Đây là cách bạn xử lý sạch "hard constraints".

---

## 6. Tích hợp Seedance 2.0 (bắt buộc)

`backend/services/seedance/client.py` — async client mỏng.

```python
class SeedanceMode(str, Enum):
    T2V = "text_to_video"
    I2V = "image_to_video"   # storyboard frame → chuyển động
    R2V = "reference_to_video"  # ảnh sản phẩm + bộ reference thương hiệu

async def generate(prompt: str, *, mode: SeedanceMode, duration_s: int,
                   seed: int, reference_urls: list[str] | None = None,
                   aspect: str = "9:16") -> bytes: ...
```

**Quy tắc sử dụng:**
- **Shot đầu của mỗi biến thể:** `T2V` từ mô tả cảnh của Director (thiết lập thế giới hình ảnh).
- **Shot demo sản phẩm:** `I2V` với ảnh tĩnh sản phẩm từ `brand_kit/` làm frame neo → chuyển động khóa thương hiệu.
- **Shot B-roll / lifestyle:** `R2V` với bộ reference thương hiệu để Seedance mượn DNA màu/ánh sáng thương hiệu.
- Luôn truyền `seed` để **cùng brief sinh ra cùng clip** (tái lập cho giám khảo).
- Giới hạn **6 shot/biến thể**; tổng thời lượng video 15-30s.

---

## 7. Tích hợp Seed 2.0 (ModelArk) (tùy chọn nhưng khuyến nghị cho A/B)

`backend/services/seed2/client.py` — dùng cho Planner, Brand Steward, Copywriter, Director, Visualist, QA.

Mẫu prompt (ví dụ copywriter):

```
SYSTEM: Bạn là Copywriter trong một content factory của BytePlus. Voice: {brand.toneOfVoice}.
HARD RULES: độ dài ≤ {lengthSec}s, tuân thủ chuẩn {platform}, không dùng claim ngoài {claimsAllowed}.
OUTPUT JSON: { "hook": str, "script": [ { "t": number, "line": str, "shot": str } ], "cta": str }
USER BRIEF: {brief}
VARIANT_ANGLE: {variant.angle}   // vd: "emotional storytelling" vs "product-led demo"
```

Dùng **structured outputs / JSON mode** để các agent bàn giao không bị lỗi parse.

---

## 8. Voice, Subtitle, Edit (lớp "publishable")

- **Voice** (`voice/tts.py`): ElevenLabs cho giọng Đông Nam Á (Việt, Thái, Indo, Anh). Brand voice khóa trong `brand.voiceId`. Fallback local TTS nếu hết quota.
- **Subtitles** (`subtitles/whisper_burn.py`):
  1. Whisper transcribe `vo.mp3` → JSON cấp từ.
  2. Gom thành chunk 2 dòng, tối đa 7 từ/dòng.
  3. FFmpeg `subtitles=...:force_style='FontName={brand.fonts.display},FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=80'`.
- **Editor** (`edit/concat.py`): FFmpeg `xfade` transition, `overlay` logo (trên-phải, 12% width), `eq`/`colorbalance` để nhất quán palette, `scale` sang 9:16 (1080x1920) và 1:1 (1080x1080).

---

## 9. QA / Cổng "Editor-Rated Publishable"

`backend/services/qa/rubric.py` — bộ chấm hybrid (deterministic + LLM).

| Tiêu chí | Trọng số | Cách chấm |
|---|---|---|
| Sức mạnh hook (3s đầu) | 25 | Judge Seed 2.0 theo prompt rubric |
| Nhất quán thương hiệu | 20 | Phát hiện palette + logo (image diff so với `brand_lock.json`) |
| Tuân thủ | 20 | Regex + LLM kiểm tra `claimsForbidden` |
| Chất lượng âm thanh | 10 | LUFS target, peak, tỉ lệ im lặng |
| Pacing | 10 | Phương sai độ dài shot, dead air |
| Chất lượng caption | 10 | Độ phủ sub, độ dài dòng |
| Rõ ràng CTA | 5 | Judge LLM |

Điểm = Σ. **Đậu = ≥80.** Nếu đậu, biến thể vào export pack. Nếu trượt, Director nhận feedback QA và chạy một vòng sửa rẻ (không sinh thêm Seedance, chỉ re-edit + re-VO nếu cần).

---

## 10. Rebuild Frontend (control plane, không phải UI render)

Giữ wizard, **nâng cấp bề mặt**:

| Trang | Trở thành gì |
|---|---|
| `/` (create) | Brief wizard → chọn 1/2 biến thể → "Generate pack" |
| `/verify` | So sánh cạnh nhau các biến thể với điểm QA, duyệt một click |
| `/dashboard` | Throughput: briefs/ngày, thời gian trung bình ra pack, tỉ lệ đậu |
| `/history` | Chạy lại với một input đổi (demo Gen-Z → Millennial-mom) |
| `/schedule` | Bàn giao n8n: chọn nền tảng + giờ, đẩy lên TikTok/Reels |
| `/settings` | Editor brand kit, danh sách claims, chọn voice |

**Tiện ích demo quan trọng:**
- Nút **"change one input"** trên `/history` chạy lại cùng brief với một trường đã đổi (kịch bản bắt buộc).
- **DAG trực tiếp** trên trang create sáng đèn khi agent chạy (hiển thị TRAE).

---

## 11. Template Workflow TRAE (deliverable)

`trae/workflows/content-factory.trae.json` phải:
- Mirror DAG agent ở §4.
- Có input có kiểu khớp schema `Brief`.
- Lộ prompt của mọi agent dưới dạng node có thể sửa (để giám khảo tinh chỉnh).
- Chạy lại được: `trae run content-factory --brief briefs/coffee.json`.

Một `docs/WORKFLOW.md` 1 trang nên gồm: sơ đồ DAG, ảnh chụp màn hình 60 giây có narration, và 3 bước "clone & run".

---

## 12. Kế hoạch hiệu năng (đạt "<60 phút")

Ngân sách tuần tự cho **một biến thể** (hai chạy song song):

| Bước | Thời gian | Song song? |
|---|---|---|
| Planner + Brand Steward | 15s | chia sẻ |
| Copywriter + Director + Visualist (mỗi biến thể) | 30s | theo biến thể |
| Seedance 2.0 (6 shot, 3 đồng thời) | 3-4 phút | theo shot |
| Voice + Whisper | 30s | theo biến thể |
| Edit (concat, overlay, subs, color) | 45s | theo biến thể |
| QA + Packer | 30s | theo biến thể |
| **Wall-clock biến thể** | **~7 phút** | — |
| **Hai biến thể end-to-end** | **~10 phút** | crew song song |

Còn lại **~50 phút dư** cho retry, bàn giao n8n và thở khi demo. Mục tiêu 60 phút rất an toàn.

---

## 13. Kế hoạch rebuild theo pha

### P0 – Nền tảng (Ngày 1, ~4h)
- [ ] Thêm client Seedance 2.0 (`backend/services/seedance/`).
- [ ] Thêm client Seed 2.0 (ModelArk) (`backend/services/seed2/`).
- [ ] Định nghĩa Pydantic model `Brief` + kiểu TS.
- [ ] Thay `routers/video.py` bằng `routers/factory.py` (một endpoint, fan-out 2 crew).
- [ ] Nối Sheets + Drive làm storage `brand_kit/` + `output/`.

**Cổng:** `POST /api/v1/factory/generate` trả về 2 clip thô trong <10 phút với brief cà phê.

### P1 – Agent + template TRAE (Ngày 2, ~5h)
- [ ] Implement Planner, Brand Steward, Copywriter, Director, Visualist (Seed 2.0).
- [ ] Xây orchestrator 2 crew song song (`asyncio.gather`).
- [ ] Author `trae/workflows/content-factory.trae.json`.
- [ ] DAG trực tiếp trong frontend trang create.

**Cổng:** Template TRAE chạy end-to-end; giám khảo có thể clone + chạy lại với sample brief cà phê.

### P2 – Bóng bẩy đến "publishable" (Ngày 3, ~4h)
- [ ] ElevenLabs VO + Whisper + burn-in sub.
- [ ] FFmpeg edit: concat, logo, color grade, export 9:16 + 1:1.
- [ ] Rubric QA + vòng tự loại.
- [ ] Cover art, caption, title A/B, hashtag qua Seed 2.0.
- [ ] Đẩy n8n cho lịch đăng (tùy chọn).

**Cổng:** Brief cà phê sinh ra 2 biến thể đạt ≥80, export 9:16 + 1:1.

### P3 – Demo + nộp bài (Ngày 4, ~3h)
- [ ] `docs/WORKFLOW.md` (1 trang).
- [ ] Video demo: walkthrough 90s từ brief → 2 biến thể → schedule.
- [ ] Dọn dẹp repo GitHub: README, ARCHITECTURE.md, sample brief, sample output.
- [ ] Thêm 2 sample brief (skincare, services) để chứng minh khả năng tổng quát hóa.

---

## 14. Sample brief cần đưa vào repo

Đặt dưới `briefs/`:

- `coffee-genz.json` – F&B, cà phê sữa đá Việt Nam, gen-z, 20s, TikTok.
- `coffee-millennial-mom.json` – cùng sản phẩm, đổi audience → output phải thay đổi có ý nghĩa.
- `skincare-ab.json` – skincare, A/B/C hook variants, người thắng được full video.
- `clinic-services.json` – ngành dịch vụ, nhiều claim, vận hành cổng tuân thủ.

Điều này thỏa tiêu chí "Change one input → output changes meaningfully".

---

## 15. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Độ trễ Seedance 2.0 phá budget 60 phút | Giới hạn 6 shot; 3 đồng thời; timeout mỗi shot; fallback render preview sang I2V với ảnh tĩnh |
| Lệch brand giữa các biến thể | Output Brand Steward được tiêm vào **mọi** prompt downstream; QA check palette |
| Vi phạm claims/compliance | Regex claim cấm + LLM judge, loại cứng, không cần người duyệt |
| Hết quota ElevenLabs | Fallback local TTS; cache VO theo `voiceId + script hash` |
| Lệch timing sub | Whisper cấp từ + force-align theo VO; giới hạn độ dài dòng |
| Giám khảo không tái lập được | Workflow TRAE là entrypoint chuẩn; `trae run` tái lập; `seed` được pin |
| "≥80% publishable" cảm tính | Rubric công khai, trọng số công khai, điểm hiển thị trong UI |

---

## 16. Tiêu chí chấp nhận (mirroring giám khảo)

- [ ] Brief → 2 biến thể trong **<60 phút** (wall-clock ghi log trong Sheets).
- [ ] Hai biến thể có **hướng sáng tạo khác biệt** (diff plan của Planner hiển thị).
- [ ] **TRAE orchestration hiển thị được** trong UI (DAG trực tiếp) và dưới dạng file (`content-factory.trae.json`).
- [ ] **Seedance 2.0 được dùng** cho ít nhất một shot mỗi biến thể, có log chế độ (T2V/I2V/R2V).
- [ ] Export gồm **9:16 + 1:1**, sub burn-in cứng, cover art, caption, title.
- [ ] Demo **one-input-change** chạy lại và cho pack khác biệt có ý nghĩa.
- [ ] **Điểm QA ≥80** trên cả hai biến thể nộp.
- [ ] **Workflow clone-and-run** trong 3 câu lệnh.

---

## 17. Action list file-by-file (cho team code)

**File backend mới**
- `backend/services/seedance/__init__.py`, `client.py`, `modes.py`
- `backend/services/seed2/__init__.py`, `client.py`, `prompts/`
- `backend/services/voice/__init__.py`, `tts.py`, `voices_catalog.py`
- `backend/services/subtitles/__init__.py`, `whisper_burn.py`
- `backend/services/brand_kit/__init__.py`, `overlay.py`, `palette.py`
- `backend/services/qa/__init__.py`, `rubric.py`
- `backend/services/agents/{planner,brand_steward,copywriter,director,visualist,editor,packer}.py`
- `backend/services/orchestrator/factory.py`
- `backend/routers/factory.py`
- `backend/models/brief.py`

**Sửa đổi**
- `backend/main.py` – đăng ký router `factory`, bỏ `video` (hoặc alias cho back-compat)
- `backend/services/scheduler.py` – trỏ vào job của `factory`
- `frontend/lib/types.ts` – thêm `Brief`
- `frontend/components/create-wizard.tsx` – form theo brief schema + variant target
- `frontend/app/page.tsx` – DAG trực tiếp + nút chạy
- `frontend/lib/api.ts` – `generatePack(brief)`

**Tài liệu/asset mới**
- `trae/workflows/content-factory.trae.json`
- `docs/WORKFLOW.md` (1 trang)
- `docs/ARCHITECTURE.md`
- `briefs/*.json` (4 sample)
- `outputs/` (sample pack để giám khảo xem)

---

## 18. TL;DR cho team

1. **Re-orchestrate, đừng re-render.** Chiến thắng nằm ở DAG agent + khả năng hiển thị của TRAE, không phải một lời gọi render nhanh hơn.
2. **Hai crew song song** là cách bạn đạt <60 phút với 2 biến thể khác biệt.
3. **Khóa brand + cổng QA** là cách bạn đạt ≥80% publishable.
4. **Ship một template TRAE** giám khảo có thể clone. Một artifact đó là điểm "reusability".
5. **Demo kịch bản one-input-change** — đó là tiêu chí dễ chứng minh nhất.

