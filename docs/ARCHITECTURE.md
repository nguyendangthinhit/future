# Architecture (BX-T1)

## Mục đích
Tài liệu này giải thích kiến trúc kỹ thuật của Content Factory, ánh xạ từng
agent ↔ file ↔ model provider ↔ endpoint. Mục tiêu: dev mới onboard trong
30 phút có thể chỉnh prompt, thêm agent, hoặc swap backend.

## Stack
- **Backend:** Python 3.10, FastAPI, asyncio, dataclass, FFmpeg (subprocess)
- **Frontend:** Next.js 14, React, TypeScript, Tailwind
- **Model gateway:** `model_gateway/` (legacy = Gemini + Ecomdy, byteplus = Seed 2.0 + Seedance 2.0)
- **Storage:** Google Sheets (tracking) + Google Drive (asset)
- **Orchestration template:** `trae/workflows/content-factory.trae.json`
- **TTS:** Ecomdy TTS (legacy) → ElevenLabs (planned)
- **STT:** faster-whisper (local) với fallback heuristic
- **Render:** FFmpeg concat + overlay + color grade

## Layers
```
┌────────────────────────────────────────────────────────────┐
│ UI (Next.js): /, /verify, /history, /dashboard, /schedule │
└──────────────┬─────────────────────────────────────────────┘
               │  POST /api/v1/factory/generate
               ▼
┌────────────────────────────────────────────────────────────┐
│ routers/factory.py                                         │
│   - validate Brief                                         │
│   - call orchestrator                                      │
│   - return full pack + trace                               │
└──────────────┬─────────────────────────────────────────────┘
               ▼
┌────────────────────────────────────────────────────────────┐
│ services/orchestrator/factory.py                           │
│   - Planner → 2+ variants                                  │
│   - Brand Steward (shared)                                 │
│   - asyncio.gather(crew_a, crew_b)                         │
│   - emit trace events for live DAG                         │
└──────┬─────────────────────────────────────────┬────────────┘
       │                                         │
       ▼                                         ▼
┌─────────────────┐                     ┌─────────────────────┐
│ Crew A (async)  │                     │ Crew B (async)      │
│ ├─ copywriter   │                     │ ├─ copywriter        │
│ ├─ director     │                     │ ├─ director          │
│ ├─ visualist    │                     │ ├─ visualist         │
│ ├─ renderer ────│── get_video() ──────│── renderer           │
│ ├─ voice ───────│── synthesize() ─────│── voice              │
│ ├─ subtitler    │                     │ ├─ subtitler         │
│ ├─ editor       │                     │ ├─ editor            │
│ ├─ qa           │                     │ ├─ qa                │
│ └─ packer       │                     │ └─ packer            │
└────────┬────────┘                     └──────────┬──────────┘
         │                                        │
         └────────────┬───────────────────────────┘
                      ▼
┌────────────────────────────────────────────────────────────┐
│ model_gateway/                                              │
│   - get_llm()    → LLMClient (Seed2Client | LegacyLLM)     │
│   - get_video()  → VideoClient (SeedanceVC | LegacyVC)     │
│   - chọn backend qua MODEL_BACKEND env                     │
└────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│ External                                                    │
│   - Gemini (legacy) / Seed 2.0 (byteplus) for LLM          │
│   - Ecomdy (legacy) / Seedance 2.0 (byteplus) for video    │
│   - ElevenLabs TTS                                         │
│   - faster-whisper local                                   │
│   - FFmpeg (system) for edit/sub/concat                    │
└────────────────────────────────────────────────────────────┘
```

## File map (agent ↔ code)

| Agent         | File                                            | Model                  | Sync? |
|---------------|-------------------------------------------------|------------------------|-------|
| Planner       | `services/agents/planner.py`                    | LLM                    | sync  |
| Brand Steward | `services/agents/brand_steward.py`              | LLM                    | sync  |
| Copywriter    | `services/agents/copywriter.py`                 | LLM                    | sync  |
| Director      | `services/agents/director.py`                   | LLM                    | sync  |
| Visualist     | `services/agents/visualist.py`                  | LLM                    | sync  |
| Renderer      | `model_gateway.VideoClient.submit/poll`         | Video API              | async |
| Voice         | `services/voice/tts.py`                         | TTS API                | async |
| Subtitler     | `services/subtitles/whisper_burn.py`            | Whisper + FFmpeg       | async |
| Editor        | `services/edit/concat.py`                       | FFmpeg                 | async |
| QA            | `services/qa/rubric.py`                         | LLM judge + heuristic | sync  |
| Packer        | `services/agents/packer.py`                     | LLM                    | sync  |

## Data flow (1 variant)
```
brief + brand_lock + variant  →  copywriter  →  script (dict)
                                            ↓
                                          director   →  storyboard (shots[])
                                            ↓
                                         visualist  →  refined storyboard
                                            ↓
                                          renderer   →  clip_urls[]
                                            ↓
                  voice ──────────► editor ◄── subtitler
                              ↓
                              qa (≥80?)
                              ↓
                           packer   →  pack.json
```

## Brief schema
- Source: `models/brief.py` (dataclass, no pydantic dependency)
- TypeScript mirror: tương ứng — nên generate từ JSON schema khi integrate frontend
- Field quan trọng: `theme`, `brand.{name, toneOfVoice, palette, claimsAllowed, claimsForbidden}`, `constraints.{lengthSec, aspect, mustInclude, mustAvoid}`, `variantsTarget`

## Performance budget
- Planner: 5s
- Brand Steward: 5s
- Copywriter: 15s
- Director: 10s
- Visualist: 10s
- Renderer (6 shot × 2 variant, 3 concurrent): 240s
- Voice (2 variant): 30s
- Subtitles: 30s
- Edit (concat + color + logo + 2 aspect): 60s
- QA + Packer (2 variant): 10s
- **Total: ~7 min/variant, 2 variant chạy song song → ~10 min total**

## How to add a new agent
1. Tạo file `services/agents/<name>.py` với 1 hàm `run_<name>(brief, brand_lock, ...) -> <Result>`.
2. Trong `services/agents/pipeline.py` (hàm `run_full_factory`) hoặc `services/orchestrator/factory.py` (`_render_one_variant`), chèn agent vào đúng chỗ trong DAG.
3. Cập nhật `trae/workflows/content-factory.trae.json` để thêm node + edge.
4. Thêm 1 method `to_dict()` cho output schema nếu cần serialization.

## How to swap backend
1. Điền `MODEL_BACKEND=byteplus` + `BYTEPLUS_*_API_KEY` vào `.env`.
2. Restart. Không cần đổi code.

## Failure modes & fallbacks
- LLM fail → mỗi agent có `_fallback()` trả về output hợp lệ tối thiểu. Pipeline luôn chạy tiếp.
- Render fail → clip_urls rỗng, editor skip, output pack vẫn có script + storyboard + caption.
- QA < 80 → vẫn xuất pack nhưng flag `qa_passed=False` cho UI highlight.
- TTS fail → dùng script text làm VO placeholder, sub vẫn tạo được.

## Testing
- Smoke test: `python -m services.orchestrator.smoke_test` (chạy 1 brief end-to-end, không cần key).
- Gateway test: `python -m model_gateway.smoke_test` (import + routing).
- Toàn bộ test: `python -m pytest tests/` (TODO: viết thêm).
