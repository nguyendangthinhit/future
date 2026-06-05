# BX-T1 – Content Creation Video Factory: Build Recommendation

> **Hackathon track:** BX-T1 · **Sponsor:** BytePlus × TRAE
> **One-liner:** Brief in → 2 publish-ready TikTok variants out in <60 min, ≥80% editor-rated publishable.
> **Audience of this doc:** the team that will build, demo, and judge the rebuild.

---

## 1. Executive Summary

You already have a working skeleton (`backend/` FastAPI + `frontend/` Next.js + n8n + Sheets/Drive). To win BX-T1, the rebuild should **stop being a "video render API wrapper" and become a TRAE-orchestrated, agentic content factory** that is observably:

1. **Multi-agent** – planner, copywriter, director, storyboarder, voice, edit, QA.
2. **Brand-locked** – every variant respects the brand kit (logo, palette, fonts, voice, claims).
3. **Platform-correct** – TikTok / Reels / Shorts (9:16, 1:1, 15-30s, hard subs, native captions).
4. **A/B-ready** – ≥2 distinct creative directions per brief with measurable variant IDs.
5. **Re-runnable** – judges can clone the TRAE workflow, paste a brief, and reproduce.

The recommendation below is a **phased rebuild plan** (P0 → P1 → P2) with concrete file changes, prompt patterns, and acceptance gates. It re-uses your existing infra (Sheets/Drive as content store, FastAPI as orchestrator, Next.js as control plane) and **adds** the missing pieces: Seedance 2.0 (T2V/I2V/R2V), Seed 2.0 (ModelArk) for script/copy, ElevenLabs/TTS for VO, Whisper + burn-in for subtitles, and a TRAE workflow template as a first-class deliverable.

---

## 2. Current State Audit (what to keep, what to drop)

**Keep (still valuable):**
- `backend/main.py` FastAPI bootstrap, router registration, APScheduler lifespan.
- `backend/services/sheets.py`, `drive_service.py` – content store + asset CDN (perfect for a "brand asset library").
- `backend/routers/verify.py` – idea approval workflow maps to "variant A/B approval" gate.
- `frontend/components/create-wizard.tsx` – good shell for the brief intake form.
- `frontend/app/{dashboard,history,verify,schedule}` pages – reuse for the editor console.
- `n8n/n8n_workflow_template.json` – evolve into the "TRAE orchestration template".

**Rewrite / replace:**
- `backend/routers/video.py` – currently single-pipeline render. Replace with a **multi-agent pipeline orchestrator** that emits 2 variants in parallel.
- `backend/services/agents/{scriptwriter,director,pipeline}.py` – currently a 2-step chain. Extend to 6+ specialized agents (see §4).
- `backend/services/llm_manager.py`, `ecomdy.py` – split into a generic `model_gateway/` that routes between **Seed 2.0 (ModelArk) for text** and **Seedance 2.0 for video** (mandatory).
- `frontend/app/page.tsx` + `create-wizard.tsx` – needs a **Brief Schema** with brand kit, audience, platform, hard constraints, and a **Variant Selector** at the end.

**Add (net-new, mandatory for the brief):**
- `backend/services/seedance/` – Seedance 2.0 client (T2V / I2V / R2V modes).
- `backend/services/seed2/` – Seed 2.0 (ModelArk) client for hook/script/caption/title A/B.
- `backend/services/voice/` – ElevenLabs or compatible TTS with brand-voice selection.
- `backend/services/subtitles/` – Whisper transcription + burn-in renderer (FFmpeg `subtitles` filter + style preset).
- `backend/services/brand_kit/` – logo overlay, palette extraction, font loading, claim-compliance checker.
- `backend/services/qa/` – editor-rubric scorer (publishability 0-100) to drive the ≥80% gate.
- `trae/workflows/content-factory.trae.json` – **first-class deliverable**, mirrors the agent DAG so judges can clone & re-run.
- `docs/WORKFLOW.md` – the 1-page workflow doc (deliverable).

---

## 3. Target Architecture (TRAE-orchestrated)

```
                ┌──────────────────────┐
                │   Brief In (UI/API)  │
                │  theme, brand kit,   │
                │  audience, platform, │
                │  hard constraints    │
                └──────────┬───────────┘
                           │
                ┌──────────▼───────────┐
                │   Planner Agent      │  ← Seed 2.0 (ModelArk)
                │ 2 creative directions│
                │ A/B variant plan     │
                └──────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ Variant A Crew   │       │ Variant B Crew   │
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
              │ A/B results          │
              └──────────────────────┘
```

**Why this shape wins the brief:**
- "TRAE orchestration must be visible" → the DAG above is exactly what `trae/workflows/content-factory.trae.json` describes; the UI can render the same DAG with live status.
- "≥2 creative directions with A/B setup" → Planner forks into two isolated crew runs, each with its own copy/visual/voice decisions and a variant ID stamped onto every frame.
- "Brief → 2 variants in <60 min" → variants run **in parallel** (asyncio.gather across the two crews), Seedance T2V is the long pole, so we keep it under 4 min per shot and cap at 6 shots/variant.
- "≥80% editor-rated publishable" → the QA rubric gates export; only variants scoring ≥80 are auto-published to the pack, the rest loop back to the Director for a fast revision.

---

## 4. Agent Roster (each one is a small, focused prompt)

| # | Agent | Model | Responsibility | Output |
|---|---|---|---|---|
| 1 | **Planner** | Seed 2.0 | Decompose brief into 2 distinct creative angles, define A/B hypothesis | `plan.json` |
| 2 | **Brand Steward** | Seed 2.0 | Lock palette, font, logo placement, claim whitelist/blacklist, tone-of-voice | `brand_lock.json` |
| 3 | **Copywriter** | Seed 2.0 | Hook variants (A/B/C), 15-30s script, CTA, on-screen text | `script.json` |
| 4 | **Director** | Seed 2.0 | Shot list: scene-by-scene A-roll/B-roll, transitions, Pacing | `storyboard.json` |
| 5 | **Visualist** | Seed 2.0 | Per-shot visual prompt tuned for Seedance 2.0 (T2V/I2V/R2V) | `shots.json` |
| 6 | **Renderer** | Seedance 2.0 | Generate raw clips (async, parallel across shots) | `clip_*.mp4` |
| 7 | **Voice** | ElevenLabs / TTS | VO per variant in brand voice | `vo.mp3` |
| 8 | **Subtitler** | Whisper | Transcribe VO, burn in hard subs with brand style | `subs.srt` + `video_with_subs.mp4` |
| 9 | **Editor** | FFmpeg | Concat, transitions, logo overlay, color grade, export 9:16 + 1:1 | `final_*.mp4` |
| 10 | **QA / Editor-in-Chief** | Seed 2.0 | Score 0-100 on rubric (hook, pace, brand, compliance, audio). Reject <80. | `qa.json` |
| 11 | **Packer** | Internal | Cover art (Seed 2.0 image), caption, title, hashtags, schedule hint | `pack.json` |

**TRAE visibility rule:** every agent must (a) write a status row to Sheets, (b) emit a `trace.jsonl` event the UI can stream, and (c) be a node in `content-factory.trae.json`.

---

## 5. Brief Schema (frontend ↔ backend contract)

This is the single source of truth. Define it once in `frontend/lib/types.ts` and mirror as a Pydantic model in `backend/models/brief.py`.

```ts
type Brief = {
  theme: string;            // "F&B: Vietnamese iced coffee, gen-z launch"
  brand: {
    name: string;
    toneOfVoice: string;    // "playful, confident, witty"
    palette: { primary: string; accent: string; bg: string };
    fonts: { display: string; body: string };
    logoUrl: string;
    voiceId: string;        // ElevenLabs voice id
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
  variantsTarget: 1 | 2;     // default 2
};
```

**Hard rule:** if `claimsForbidden` matches anything in the script, QA auto-rejects. This is how you hit "hard constraints" cleanly.

---

## 6. Seedance 2.0 Integration (mandatory)

`backend/services/seedance/client.py` — thin async client.

```python
class SeedanceMode(str, Enum):
    T2V = "text_to_video"
    I2V = "image_to_video"   # storyboard frame → motion
    R2V = "reference_to_video"  # product photo + brand reference set

async def generate(prompt: str, *, mode: SeedanceMode, duration_s: int,
                   seed: int, reference_urls: list[str] | None = None,
                   aspect: str = "9:16") -> bytes: ...
```

**Usage rules:**
- **First shot of every variant:** `T2V` from the Director's scene description (sets the visual world).
- **Product demo shots:** `I2V` with a product still from `brand_kit/` as the anchor frame → brand-locked motion.
- **B-roll / lifestyle shots:** `R2V` with the brand reference set so Seedance can borrow the brand's color/light DNA.
- Always pass `seed` so the **same brief produces the same clip** (reproducibility for judges).
- Cap to **6 shots per variant**; total video length 15-30s.

---

## 7. Seed 2.0 (ModelArk) Integration (optional but recommended for A/B)

`backend/services/seed2/client.py` — used by Planner, Brand Steward, Copywriter, Director, Visualist, QA.

Prompt pattern (copywriter example):

```
SYSTEM: You are the Copywriter in a BytePlus content factory. Voice: {brand.toneOfVoice}.
HARD RULES: length ≤ {lengthSec}s, {platform} conventions, no claims outside {claimsAllowed}.
OUTPUT JSON: { "hook": str, "script": [ { "t": number, "line": str, "shot": str } ], "cta": str }
USER BRIEF: {brief}
VARIANT_ANGLE: {variant.angle}   // e.g. "emotional storytelling" vs "product-led demo"
```

Use **structured outputs / JSON mode** so agents hand off without parsing fragility.

---

## 8. Voice, Subtitles, Edit (the "publishable" layer)

- **Voice** (`voice/tts.py`): ElevenLabs for SEA voices (Vietnamese, Thai, Indonesian, English). Brand voice locked in `brand.voiceId`. Fallback to a local TTS if quota is hit.
- **Subtitles** (`subtitles/whisper_burn.py`):
  1. Whisper transcribes `vo.mp3` → word-level JSON.
  2. Group into 2-line chunks, max 7 words/line.
  3. FFmpeg `subtitles=...:force_style='FontName={brand.fonts.display},FontSize=18,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2,MarginV=80'`.
- **Editor** (`edit/concat.py`): FFmpeg `xfade` transitions, `overlay` logo (top-right, 12% width), `eq`/`colorbalance` for palette consistency, `scale` to 9:16 (1080x1920) and 1:1 (1080x1080).

---

## 9. QA / "Editor-Rated Publishable" Gate

`backend/services/qa/rubric.py` — a deterministic + LLM hybrid scorer.

| Dimension | Weight | How |
|---|---|---|
| Hook strength (first 3s) | 25 | Seed 2.0 judge with rubric prompt |
| Brand consistency | 20 | Palette + logo presence detection (image diff vs `brand_lock.json`) |
| Compliance | 20 | Regex + LLM check vs `claimsForbidden` |
| Audio quality | 10 | LUFS target, peak, silence ratio |
| Pacing | 10 | Shot length variance, dead air |
| Caption quality | 10 | Subtitle coverage, line length |
| CTA clarity | 5 | LLM judge |

Score = Σ. **Pass = ≥80.** If pass, the variant enters the export pack. If fail, the Director gets the QA feedback and runs one cheap revision (no extra Seedance generations, just a re-edit + re-VO if needed).

---

## 10. Frontend Rebuild (control plane, not a render UI)

Keep the wizard, **upgrade the surface**:

| Page | What it becomes |
|---|---|
| `/` (create) | Brief wizard → 1/2 variants selector → "Generate pack" |
| `/verify` | Side-by-side variant viewer with QA scores, one-click approve |
| `/dashboard` | Throughput: briefs/day, avg time-to-pack, % pass rate |
| `/history` | Re-run with one input changed (the Gen-Z → Millennial-mom demo) |
| `/schedule` | n8n hand-off: pick platforms + times, push to TikTok/Reels |
| `/settings` | Brand kit editor, claim lists, voice picker |

**Critical demo affordances:**
- A **"change one input"** button on `/history` that re-runs the same brief with one field swapped (the required scenario).
- A **live DAG** on the create page that lights up agents as they run (TRAE visibility).

---

## 11. TRAE Workflow Template (deliverable)

`trae/workflows/content-factory.trae.json` must:
- Mirror the agent DAG from §4.
- Have typed inputs matching the `Brief` schema.
- Expose every agent's prompt as an editable node (so judges can tweak).
- Be re-runnable: `trae run content-factory --brief briefs/coffee.json`.

A 1-page `docs/WORKFLOW.md` should include: the DAG diagram, a 60-second narrated screenshot, and a "how to clone & run" 3-step.

---

## 12. Performance Plan (hit "<60 minutes")

Sequential budget for **one variant** (two run in parallel):

| Step | Time | Parallel? |
|---|---|---|
| Planner + Brand Steward | 15s | shared |
| Copywriter + Director + Visualist (per variant) | 30s | per-variant |
| Seedance 2.0 (6 shots, 3 concurrent) | 3-4 min | per-shot |
| Voice + Whisper | 30s | per-variant |
| Edit (concat, overlay, subs, color) | 45s | per-variant |
| QA + Packer | 30s | per-variant |
| **Variant wall-clock** | **~7 min** | — |
| **Two variants end-to-end** | **~10 min** | parallel crew |

This leaves **~50 min of headroom** for retries, n8n handoff, and demo breathing room. The 60-min target is safe.

---

## 13. Phased Rebuild Plan

### P0 – Foundations (Day 1, ~4h)
- [ ] Add Seedance 2.0 client (`backend/services/seedance/`).
- [ ] Add Seed 2.0 (ModelArk) client (`backend/services/seed2/`).
- [ ] Define `Brief` Pydantic model + TS type.
- [ ] Replace `routers/video.py` with `routers/factory.py` (one endpoint, fans out to 2 crews).
- [ ] Wire Sheets + Drive as `brand_kit/` + `output/` storage.

**Gate:** `POST /api/v1/factory/generate` returns 2 raw clips in <10 min on a coffee brief.

### P1 – Agents + TRAE template (Day 2, ~5h)
- [ ] Implement Planner, Brand Steward, Copywriter, Director, Visualist (Seed 2.0).
- [ ] Build the two-crew parallel orchestrator (`asyncio.gather`).
- [ ] Author `trae/workflows/content-factory.trae.json`.
- [ ] Live DAG in the frontend create page.

**Gate:** TRAE template runs end-to-end; judges can clone + re-run with the sample coffee brief.

### P2 – Polish to "publishable" (Day 3, ~4h)
- [ ] ElevenLabs VO + Whisper + subtitle burn-in.
- [ ] FFmpeg edit: concat, logo, palette grade, 9:16 + 1:1 export.
- [ ] QA rubric + auto-reject loop.
- [ ] Cover art, caption, title A/B, hashtags via Seed 2.0.
- [ ] n8n push for scheduled posting (optional).

**Gate:** Coffee brief produces 2 variants scoring ≥80, exported in 9:16 + 1:1.

### P3 – Demo + submission (Day 4, ~3h)
- [ ] `docs/WORKFLOW.md` (1 page).
- [ ] Demo video: 90s walkthrough of a brief → 2 variants → schedule.
- [ ] GitHub repo clean-up: README, ARCHITECTURE.md, sample briefs, sample outputs.
- [ ] Two more sample briefs (skincare, services) to prove generalization.

---

## 14. Sample Briefs to Ship in the Repo

Place under `briefs/`:

- `coffee-genz.json` – F&B, Vietnamese iced coffee, gen-z, 20s, TikTok.
- `coffee-millennial-mom.json` – same product, audience swap → output must change meaningfully.
- `skincare-ab.json` – skincare, A/B/C hook variants, winner gets full video.
- `clinic-services.json` – services vertical, claim-heavy, exercises the compliance gate.

This satisfies the "Change one input → output changes meaningfully" judging criterion.

---

## 15. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Seedance 2.0 latency blows 60-min budget | Cap to 6 shots; 3 concurrent; per-shot timeout; render-preview fallback to I2V with a still |
| Brand drift between variants | Brand Steward output is injected into **every** downstream prompt; QA palette check |
| Claims/compliance violation | Forbidden-claim regex + LLM judge, hard reject, no human in the loop |
| ElevenLabs quota | Local TTS fallback; cache VO per `voiceId + script hash` |
| Subtitle timing drift | Whisper word-level + force-align to VO duration; cap line length |
| Judges can't reproduce | TRAE workflow is the canonical entrypoint; `trae run` reproduces; `seed` is pinned |
| "≥80% publishable" feels subjective | Rubric is open, weights are public, scores are shown in the UI |

---

## 16. Acceptance Criteria (judge-mirrored)

- [ ] Brief → 2 variants in **<60 min** (logged wall-clock in Sheets).
- [ ] Both variants have **distinct creative directions** (planner plan diff is visible).
- [ ] **TRAE orchestration is visible** in UI (live DAG) and as a file (`content-factory.trae.json`).
- [ ] **Seedance 2.0 is used** for at least one shot per variant, with the mode (T2V/I2V/R2V) logged.
- [ ] Exports include **9:16 + 1:1**, hard-burned subtitles, cover art, caption, title.
- [ ] **One-input-change** demo re-runs and produces a meaningfully different pack.
- [ ] **QA score ≥80** on both shipped variants.
- [ ] **Workflow is clone-and-run** in 3 commands.

---

## 17. File-by-File Action List (for whoever codes it)

**New backend files**
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

**Modified**
- `backend/main.py` – register `factory` router, drop `video` (or alias for back-compat)
- `backend/services/scheduler.py` – point at `factory` jobs
- `frontend/lib/types.ts` – add `Brief`
- `frontend/components/create-wizard.tsx` – brief schema form + variant target
- `frontend/app/page.tsx` – live DAG + run button
- `frontend/lib/api.ts` – `generatePack(brief)`

**New docs/assets**
- `trae/workflows/content-factory.trae.json`
- `docs/WORKFLOW.md` (1 page)
- `docs/ARCHITECTURE.md`
- `briefs/*.json` (4 samples)
- `outputs/` (sample packs for judge inspection)

---

## 18. TL;DR for the Team

1. **Re-orchestrate, don't re-render.** The win is in the agent DAG + TRAE visibility, not in a faster render call.
2. **Two crews in parallel** is what gets you to <60 min with 2 distinct variants.
3. **Brand-locked + QA-gated** is what gets you to ≥80% publishable.
4. **Ship a TRAE template** that judges can clone. That single artifact is the "reusability" score.
5. **Demo the one-input-change** scenario — it's the easiest judging criterion to visibly pass.

