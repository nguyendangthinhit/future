Team Formation
These 5 challenges form the FINAL lineup. Teams will form around their preferred challenge. The hackathon takes place over a weekend in Da Nang. Pick a challenge that matches your team's skills and ship something real.

---
Challenge Index
Nội dung này chỉ được hỗ trợ trong Lark Docs

---
BP1 - BurgerPrintsAgent (POD Catalog Assistant)
Sponsor: BurgerPrints
One-liner: From hundreds of factories to one perfect SKU, let your AI agent do the heavy lifting.
The Problem
BurgerPrints has hundreds of POD products × multiple fulfillment factories × thousands of SKUs (size × color × material × print method × base price × shipping × TAX). New sellers spend hours finding the right fulfillment combination.
Target User
New and experienced POD sellers on BurgerPrints selling cross-border (Etsy, Amazon, TikTok Shop, Shopify), need fast fulfillment decisions.
The Mission
Build an AI conversational chatbot that helps sellers search, compare, and choose fulfillment products in natural language (VN/EN), using BurgerPrints API v2.0 as the data source.
Input
Seller natural-language questions (VN/EN); BurgerPrints API v2.0 credentials (provided); (bonus) order creation endpoint.
Expected Output
Decision-ready answers with reasoning + comparison when needed; multi-turn dialogue; (bonus) auto-create orders via API on confirmation.
Must-have Requirements
- MUST use BurgerPrints API v2.0 (no hardcode, no scraping)
- MUST be a conversational agent (not a static filter form)
- Setup ≤ 10 minutes on judge's machine
- Seller-facing UI (web/mobile/CLI/Telegram/Discord, your choice)
- No API keys in public repo
Suggested Tech Stack
Any LLM (Claude / GPT / Gemini / Llama / Mistral / Qwen / DeepSeek) · Any framework (LangChain / LlamaIndex / CrewAI / AutoGen / custom) · Any pattern (RAG / function-calling / multi-agent / hybrid)
Sample Scenarios
- "I want to sell T-shirts for the US market, base cost under $8, ship under 5 days, which factory, which SKU?"
- "Compare hoodie prices across factories, who ships cheapest to EU?"
- "I plan to sell at $24.99 with 40% minimum margin, suggest suitable products."
Judging Criteria
Results-only judging. Live test ~10-15 questions in semi-finals, open questions in finals. UX evaluation by judges acting as real sellers. (Order-creation bonus = extra points.)
Deliverables to Submit
GitHub · README (1-2 pages) with architecture & setup ≤ 10 min · 3-5 min demo video · Slide deck · (optional) live demo URL · (bonus) order creation flow
Difficulty
⭐⭐⭐ (3/5) Medium
Tags
print-on-demand ai-agent burgerprints api-integration seller-tools

---
BP2 - BurgerMockup (AI Lifestyle Mockup Engine)
Sponsor: BurgerPrints
One-liner: From a flat design to a story customers want to live in, let your agent be the photographer, stylist, and art director.
The Problem
Default POD mockups (white background, hanger) don't sell on Etsy/Amazon. Customers are 60% more likely to buy when products are shown in lifestyle context. Lifestyle mockups today require Placeit (14−29/mo,repetitivetemplates),designers(14−29/mo,repetitivetemplates),designers(50-200/product), or hours in Photoshop. A seller with 50-200 listings needs thousands of mockups.
Target User
POD sellers on BurgerPrints with 50-500+ listings selling on Etsy / Amazon / TikTok Shop / Shopify, need high-quality lifestyle mockups without hiring a designer.
The Mission
Build an AI Mockup Agent that turns flat 2D design files into high-quality lifestyle mockups via natural language. CORE REQUIREMENT: design on product must be preserved 100% from the original file.
Input
Design file (PNG/JPG/SVG, transparent or colored bg); target product from BurgerPrints API catalog; scene/model/lighting/mood/niche description (VN/EN); multi-turn refinement.
Expected Output
Mockup ≥ 1500×1500 px ready for listings; design integrity SSIM > 0.92 (flat) / > 0.85 (lifestyle); multi-variant scenes; (bonus) multi-product apply, persona library, Shopify/Etsy publish.
Must-have Requirements
- MUST use BurgerPrints API v2.0 (product info, print area coordinates, base mockups)
- MUST be a conversational agent (not static upload form)
- Setup ≤ 15 min (BTC provides Gemini/Replicate credit for finals)
- UI must display images (not text-only)
- Output ≥ 1500×1500 px
- NO real brand logos / celebrity faces, point deduction
Suggested Tech Stack
Image: Nano Banana 2/Pro · Flux Kontext · SDXL+ControlNet · SD 3.5 · Ideogram · Recraft | LLM: any | CV: rembg, SAM2, MediaPipe, BiRefNet | Pipeline: Sharp / Pillow+OpenCV / ComfyUI · Hybrid (AI scene + composite original design) > pure AI redraw
Sample Scenarios
- "I just uploaded a cat T-shirt design for the US market, create 5 lifestyle mockups: cafe girl, streetwear, cozy living room, flat-lay with accessories, outdoor picnic."
- "I have 30 Christmas shirt listings, generate 3 holiday scenes each, keeping the design intact."
- "That mockup is nice, but the model doesn't fit my yoga/wellness niche, switch to middle-aged woman in a yoga studio at sunrise."
Judging Criteria
Live test with sample designs + prompts (semi-finals). Edge cases in finals: text-heavy, AOP, multi-print, complex colors. Side-by-side vs Placeit. Objective metrics: Design Integrity SSIM, latency p50/p95, cost per mockup. UX evaluation as real seller.
Deliverables to Submit
GitHub · README (design-integrity strategy + architecture + pipeline + setup ≤ 15 min + ≥ 10 mockup samples with prompt/time/cost) · 3-5 min demo (≥ 3 use cases with multi-turn refinement) · Slide deck · (optional) live demo · (bonus) multi-product / persona library / Shopify-Etsy publish / brand consistency
Difficulty
⭐⭐⭐⭐⭐ (5/5) Hard
Tags
mockup-generation image-ai design-integrity print-on-demand burgerprints

---
BX-T1 - Content Creation Video Factory
Sponsor: BytePlus × TRAE
One-liner: Brief in, 2 publish-ready TikTok variants out in under 60 minutes, ≥80% editor-rated publishable.
The Problem
Creators and brand teams burn 8-20 hours producing a single 60s TikTok. Designers/editors/copywriters become bottlenecks for every A/B test. Generic AI video tools speed up one step but produce output that doesn't match brand or platform conventions.
Target User
Solo creators, in-house content teams (5-20 people), and SME marketing managers in e-commerce / F&B / services across SEA.
The Mission
Build a TRAE-orchestrated agentic content factory: one creator brief in → a complete content pack out (hook variants, full script, storyboard frames, A-roll/B-roll, voiceover, hard subtitles, cover art, title, caption, platform-specific cuts). At least 2 creative directions per brief with a measurable A/B test setup.
Input
Brief (theme, brand tone, audience, platform, hard constraints: length / claims / compliance); brand kit (logo, palette, fonts, product photos); optional reference moodboard.
Expected Output
≥ 1 finished 15-30s video for TikTok / FB Reels / YouTube Shorts; 2 creative direction variants; 9:16 + 1:1 exports (minimum); reusable TRAE workflow template (judges can clone & run).
Must-have Requirements
- Seedance 2.0 (COMPULSORY), video gen (T2V/I2V/R2V)
- Seed 2.0 (ModelArk), optional (script, hook, caption, title A/B)
- TRAE orchestration must be visible in workflow
- Target: brief → 2 variants in < 60 minutes
Suggested Tech Stack
Seedance 2.0 (mandatory) · Seed 2.0 (ModelArk) · TRAE · ElevenLabs / TTS for voice · Whisper + burn-in for subtitles
Sample Scenarios
- F&B brand brief → 2 variants 20s (emotional storytelling + product-led demo) for TikTok + Reels.
- Skincare brief → hook variants A/B/C + winner gets full video.
- Change one input (audience from 'Gen Z' → 'Millennial mom') → output changes meaningfully.
Judging Criteria
Brief→content plan→production→final video pipeline cleanliness. Style/tone consistency across variants. Fast revision loops. ≥ 80% editor-rated publishable. Workflow reusability.
Deliverables to Submit
GitHub repo + demo video + 1-page workflow doc · ≥ 1 finished publish-ready video · 2 creative variants · 9:16 + 1:1 exports · Reusable TRAE workflow template
Difficulty
⭐⭐⭐⭐ (4/5) Hard
Tags
seedance-2.0 trae agentic-pipeline content-creation byteplus

---
BX-T4 - Video Intelligence Engine (Hour-to-Answer)
Sponsor: BytePlus × TRAE 
One-liner: Raw e-commerce video at scale — live stream recordings, UGC reviews, ad variants, influencer deliverables — into a queryable, grounded knowledge surface, with cross-modal reasoning over audio + visual + dialogue in SEA languages.
The Problem 
SEA e-commerce sellers, brands, and aggregators sit on a growing mountain of video they can't analyze. Live commerce hosts run 3–6 hour streams daily on TikTok Live / Shopee Live / Lazada Live, 5–7 days a week — nobody watches the recordings back. UGC product reviews pile up on TikTok Shop and Shopee, thousands per popular SKU. Ad variant libraries accumulate — a brand running 200 creatives per campaign has no way to autopsy what's in the winners vs the losers. Influencer deliverables go unaudited — brands pay creators thousands of dollars and often can't verify the spoken claim or on-screen overlay was delivered as briefed. Today: a team scrubs at 2× speed and takes notes; at scale, not feasible. Transcript-only search misses everything visual — the product reveal, the on-screen price overlay, the camera angle, the chat reaction. Existing tools collapse on Vietnamese, Thai, Bahasa, code-switching, and the cross-modal nature of commerce video where what's shown matters as much as what's said.
Target User 
AI engineers and founders building tools for SEA cross-border sellers, brand aggregators, MCN agencies, live commerce platforms, and influencer compliance / performance teams.
The Mission 
Ship a product that ingests e-commerce video at scale — live stream recordings, UGC reviews, ad variants, influencer deliverables — and turns it into a queryable, navigable surface where sellers and brands can ask grounded questions and get answers tied to real timestamps and frame evidence. No clip rendering as primary output; the value is the answer. Built and shipped on TRAE. 
Input 
One or more e-commerce video files or URLs (MP4, MOV, HLS; live stream recordings, UGC reviews, ad variants, influencer deliverables; 10-15 minutes); optional context kit (SKU list with product images, banned and required claims per market, brand mentions, target languages, host / creator names).
Expected Output
Live product where judges upload ≥ 10-15 min of e-commerce video and get within the demo window:
- Indexed timeline: scenes, dialogue with timestamps, audio events (purchase-sound jingles, laughter, host energy peaks, chat-cheer audio), on-screen text (price tags, "FREE SHIP" overlays, countdown timers, discount stamps), entities (products visible, host, packaging), energy / emotion curve
- Multilingual transcript explorer (≥ 2 SEA languages) with text search
- Product / SKU timeline: when each SKU is shown, mentioned, demonstrated, priced, compared
- Natural-language Q&A grounded with timestamp + frame thumbnail, rationale citing audio + visual + dialogue
- Claim-vs-visual verification: "host said X — is the visual evidence consistent?" with frame proof
- Temporal retrieval for compliance and performance queries: "find every moment X happens while Y"
Must-have Requirements
- Seed 2.0 mini omni (Seed-2.0-mini-260428, mandatory) — drives ALL cross-modal reasoning: scene description, multilingual ASR + translation, audio event detection, product / host tracking, on-screen OCR, NL Q&A, claim-vs-visual alignment. 
- Built and shipped on TRAE (mandatory)
- Grounded answers — every Q&A response ties to ≥ 1 timestamp AND ≥ 1 frame thumbnail; ungrounded answers are not allowed
- Claim-vs-visual verification — explicit support for at least one workflow where the model checks whether a spoken claim is visually consistent, with frame citation
- Multilingual — ≥ 2 SEA languages handled (Vietnamese, Thai, Bahasa Indonesia, Tagalog, Mandarin, English)
- Cost + latency dashboard live during demo

Suggested Tech Stack 
Seed 2.0 mini/lite model for video understanding· ffmpeg for frame extraction and window slicing at index time (no clip rendering needed — windows are virtual timestamp ranges in metadata) · PySceneDetect for shot boundaries · S3 / TOS for source video storage · TRAE as the development environment
Sample Scenarios
- TikTok Shop seller uploads a 4-hr Vietnamese TikTok Live recording → asks "when did the host demo product 27?" → grounded answer at 02:14:08 with thumbnail; "show every price mention with the product back visible" → 6 results ranked by visibility; "compliance check: did the host say 'cam kết chính hãng' (authenticity guarantee) without showing the certificate within 5s?" → 3 violations flagged with paired audio + frame evidence.
- Brand uploads 200 ad variants from last quarter, with performance CSV → "what visual + audio pattern do the top 10% performers share in the first 3 seconds?" → clustered hook archetypes with example clips per cluster; "which variants fail the FTC-style disclosure check?" → 23 variants flagged with the failing modality (no spoken disclosure / no visible overlay / overlay < 3s).

Judging Criteria 
Grounded Q&A with real timestamps (±3s) and frame thumbnails. Cross-modal rationale citing ≥ 2 of audio/visual/dialogue per answer. Claim-vs-visual verification on held-out compliance cases. SKU/product timeline precision across cuts and reframes. Multilingual coverage (≥ 2 SEA languages) with code-switching. Cost / latency / throughput transparency. TRAE-native dev workflow.

Deliverables to Submit
- Live product with web/app interface (judges upload e-commerce video and ask questions on the day)
- Cost / latency / throughput dashboard
- GitHub repo
- TRAE workspace link or screencast of TRAE-native dev workflow
- Pre-rendered demo: at least one ≥ 10-min e-commerce video (live, UGC batch, or ad-variant batch) indexed end-to-end with ≥ 10 example questions and ≥ 3 claim-vs-visual verifications, viewable in one page.
Difficulty
⭐⭐⭐⭐ (4/5) Hard
Tags
seed-2.0 video-understanding video-intelligence ecommerce byteplus

---
E2 - ViralScore
Sponsor: Ecomdy Media
One-liner: Predict if your TikTok video will viral before you post it. 73% accuracy across 7 dimensions, powered by 50M+ posts.
The Problem
US creator ad spend $37B in 2025 (+26% YoY); 16.4M monthly active TikTok creators. 80%+ of videos miss viral threshold, entire investment wasted. 'Post-and-pray' is the only strategy. TikTok 2026 algorithm changes (completion-rate threshold 50% to 70%, follower-first testing, shares/saves outweigh likes) make manual adaptation impossible; reach drops 18% for non-adapters. Trending audio peaks 3-7 days but brands discover it too late.
Target User
Brands, agencies, in-house content teams, and individual creators spending 500−500−5,000/video on TikTok content, who need to know if a video will viral BEFORE posting.
The Mission
Predict virality pre-publication across 7 dimensions (hook strength, completion-rate prediction, shares/saves probability, sound trend timing, search/keyword relevance, early engagement velocity, content-niche fit), with specific actionable fixes, not generic tips.
Input
TikTok video (MP4) or storyboard + script; brand niche, target audience, planned posting time; optional past performance data for personalized baseline.
Expected Output
ViralScore 0-100 + 7-dimension breakdown with per-dim explanation + specific actionable fixes + predicted reach range with confidence interval; (bonus) auto-rewrite script/caption variants.
Must-have Requirements
- Pre-post analysis (MANDATORY), before publishing, not after
- 7-dimension analysis (not just 1-2)
- Actionable fixes (not general tips)
- Setup ≤ 10 minutes
- Creator-facing UI
Suggested Tech Stack
Gemini 2.5 Flash / Claude 3.5 Sonnet (multimodal video) · Whisper / YAMNet (audio + sound trends) · OpenCV / MediaPipe (hook scoring) · CLIP / OpenL3 (content-niche fit) · FastAPI / Node.js
Sample Scenarios
- Upload a cat T-shirt promo video → "Score 42/100. Hook weak (first 3s = camera pan). Sound 'Espresso Remix' peaked 3 days ago. Recommend: add voiceover question + switch to sound XYZ (ascending phase)."
- "I plan to post 8pm Vietnam time, 28s video, predict reach."
- "Compare 3 versions of the same hook, which one wins?"
Judging Criteria
Prediction accuracy on 100-video holdout (35) · Actionability (25) · 7-dimension coverage (15) · Speed <30s per video (15) · Explainability (10) = 100 pts
Deliverables to Submit
GitHub · README · 3-5 min demo (≥3 live analyses) · Backtest accuracy report · Slide deck · (bonus) live demo URL
Difficulty
⭐⭐⭐ (3/5) Medium