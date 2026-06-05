# Content Factory Workflow (1 page)

> **Track:** BX-T1 · **Sponsor:** BytePlus × TRAE · **One-liner:** Brief in → 2 publish-ready TikTok variants in <60 min, ≥80% editor-rated publishable.

## Stage-based Orchestration

The content factory is divided into 5 visible stages, exposed as API endpoints for TRAE workflow orchestration:

1. **Planner + Brand Steward**
   - Endpoint: `POST /api/v1/factory/stage/plan`
   - Input: Brief
   - Output: Plan (2 variants) + Brand Lock

2. **Variant A Crew**
   - Endpoint: `POST /api/v1/factory/stage/variant`
   - Input: Brief + Brand Lock + Variant A
   - Stages: Copywriter → Director → Visualist → Renderer → Voice → Subtitle → Editor → QA → Packer
   - Output: Variant A result

3. **Variant B Crew**
   - Endpoint: `POST /api/v1/factory/stage/variant`
   - Input: Brief + Brand Lock + Variant B
   - Stages: Copywriter → Director → Visualist → Renderer → Voice → Subtitle → Editor → QA → Packer
   - Output: Variant B result

4. **Finalize Pack**
   - Endpoint: `POST /api/v1/factory/stage/finalize`
   - Input: Brief + Variants (A + B)
   - Output: Publishable variants + final pack

5. **Schedule Handoff**
   - Endpoint: `POST /api/v1/factory/schedule-handoff`
   - Input: Variant ID + platform + schedule time

## DAG (Directed Acyclic Graph)

```
                ┌──────────────────────┐
                │  Brief In (UI/API)   │
                │  theme, brand kit,   │
                │  audience, platform, │
                │  hard constraints    │
                └──────────┬───────────┘
                           │
                ┌──────────▼───────────┐
                │   Planner Agent      │  ← Seed 2.0 (ModelArk)
                │  2 creative variants │
                │  A/B plan            │
                └──────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
   ┌──────────────────┐       ┌──────────────────┐
   │ Crew Variant A   │       │ Crew Variant B   │
   │ Copy → Director  │       │ Copy → Director  │
   │ → Visualist      │       │ → Visualist      │
   │ → Renderer       │       │ → Renderer       │
   │ → Voice          │       │ → Voice          │
   │ → Subtitle       │       │ → Subtitle       │
   │ → Editor         │       │ → Editor         │
   │ → QA             │       │ → QA             │
   │ → Packer         │       │ → Packer         │
   └────────┬─────────┘       └────────┬─────────┘
            ▼                          ▼
            └────────────┬─────────────┘
                         ▼
              ┌──────────────────────┐
              │ Finalize Pack        │
              │ 9:16 + 1:1, SRT,     │
              │ cover, caption,      │
              │ A/B results          │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Schedule Handoff     │
              └──────────────────────┘
```

## 60-second narrated walkthrough
1. **0s** User paste brief vào wizard → `POST /api/v1/factory/stage/plan`
2. **5s** Planner tách brief thành 2 variant (A: emotional storytelling, B: product-led demo)
3. **30s** Brand Steward khóa palette/font/claims cho 2 crew dùng chung
4. **35-180s** 2 crew chạy song song: Copywriter → Director → Visualist (LLM only, ~30s/variant)
5. **180-540s** Seedance 2.0 render 6 shot × 2 variant (3 concurrent, ~4 min/variant)
6. **540-600s** Voice (ElevenLabs) + Whisper sub + brand overlay + concat
7. **600-650s** QA rubric chấm điểm → pack tổng hợp
8. **650-900s** Edit 9:16 + 1:1, cover art, caption, hashtags
9. **~10 phút** Hoàn tất. UI hiện 2 variant side-by-side với QA score.

## 3-step clone & run
```bash
git clone <repo>
cp .env.example .env   # điền GEMINI_API_KEY (legacy) hoặc BYTEPLUS_* (byteplus)
uvicorn main:app --reload --port 8000
trae run content-factory --brief briefs/coffee-genz.json
```

## Key metrics (judging criteria)
- **Time:** 2 variants in <60 min (target: 10 min)
- **A/B setup:** ≥2 distinct variants, each with hypothesis
- **TRAE visibility:** live DAG + `trae/workflows/content-factory.trae.json`
- **Publishability:** ≥80/100 from QA rubric
- **Brand consistency:** Brand Steward inject vào mọi downstream prompt
- **Reproducibility:** same brief + same seed → same output

## One-input-change demo
`briefs/coffee-genz.json` (audience=gen-z) → `briefs/coffee-millennial-mom.json` (audience=millennial mom).
Re-run → output pack changes meaningfully (different tone, different hook, different visual motif).

