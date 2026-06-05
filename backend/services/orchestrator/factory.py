"""
Orchestrator cho content factory.

Đây là tầng trung gian giữa router và agents — chịu trách nhiệm:
- Chuẩn bị render (submit job Seedance/Ecomdy cho mỗi shot trong storyboard).
- Sinh VO (gọi voice service).
- Sinh sub (transcribe + burn-in).
- Edit (concat, color grade, logo overlay, export aspect).
- QA gate (rubric -> publishable >= 80?).
- Trace log cho TRAE UI.

Khi tất cả xong -> trả pack với URL video (9:16 + 1:1) + metadata.
"""

from __future__ import annotations

import asyncio
import os
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Optional

from model_gateway import get_video
from models.brief import Brief

from services.agents import brand_steward, copywriter, director, packer, planner, visualist
from services.voice import extract_voiceover_from_script, synthesize
from services.subtitles import build_srt_from_vo, burn_subtitles
from services.brand_kit import apply_color_grade, apply_logo, brand_lock_check
from services.qa import run_qa


# ---------------------------------------------------------------------------
# Trace event — UI / TRAE có thể stream realtime
# ---------------------------------------------------------------------------
@dataclass
class TraceEvent:
    agent: str
    status: str = "started"        # started | done | failed
    variant_id: Optional[str] = None
    elapsed_s: float = 0.0
    detail: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 1 crew (1 variant) — từ brief + brand_lock + variant_plan
# ---------------------------------------------------------------------------
async def _render_one_variant(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
    trace: list[TraceEvent],
    *,
    include_vo: bool = True,
    include_video: bool = True,
) -> dict:
    """
    Chạy đầy đủ 1 variant: copywriter -> director -> visualist -> (render, VO, sub)
    -> edit -> QA. Trả về dict variant_out.
    """
    t0 = time.time()
    vid = variant.get("id", "?")
    out: dict[str, Any] = {
        "variant_id": vid,
        "variant_angle": variant.get("angle", ""),
    }

    try:
        # ---- Copywriter
        t = time.time()
        script_obj = copywriter.run_copywriter(brief, brand_lock, variant)
        script = script_obj.to_dict() if hasattr(script_obj, "to_dict") else {
            "hook": getattr(script_obj, "hook", ""),
            "scenes": [vars(s) for s in getattr(script_obj, "scenes", [])],
            "cta": getattr(script_obj, "cta", ""),
        }
        trace.append(TraceEvent("copywriter", "done", vid, time.time() - t))

        # ---- Director
        t = time.time()
        storyboard = director.run_director(brief, brand_lock, variant, script)
        trace.append(TraceEvent("director", "done", vid, time.time() - t))

        # ---- Visualist
        t = time.time()
        refined = visualist.run_visualist(brief, brand_lock, storyboard)
        trace.append(TraceEvent("visualist", "done", vid, time.time() - t))
    except Exception as e:
        trace.append(TraceEvent("crew_text", "failed", vid, time.time() - t0,
                                {"error": str(e)}))
        raise

    out["script"] = script
    out["storyboard"] = refined.to_dict() if hasattr(refined, "to_dict") else {"shots": []}

    # ---- Renderer (Seedance 2.0 / Ecomdy) — song song giữa các shot
    clip_urls: list[str] = []
    if include_video and refined.shots:
        video = get_video()
        t = time.time()
        try:
            jobs = await asyncio.gather(*(
                video.submit(
                    s.visual_prompt,
                    mode=s.mode,
                    image_url=_image_url_for_mode(brief, s.mode),
                    reference_urls=_reference_urls_for_mode(brief, s.mode),
                    duration_s=s.duration_s,
                    aspect="9:16",
                    seed=hash(f"{brief.theme}-{vid}-{s.shot_id}") % (2**31),
                )
                for s in refined.shots
            ), return_exceptions=True)
            for j in jobs:
                if isinstance(j, Exception):
                    print(f"[renderer] shot fail: {j}")
                    continue
                # Poll từng job (vì provider có thể khác nhau)
                try:
                    url = await video.poll(j.job_id, max_retries=2, delay_seconds=2)
                    if url:
                        clip_urls.append(url)
                except Exception as e:
                    print(f"[renderer] poll fail: {e}")
            trace.append(TraceEvent("renderer", "done", vid, time.time() - t,
                                    {"clips": len(clip_urls), "shots": len(refined.shots)}))
        except Exception as e:
            trace.append(TraceEvent("renderer", "failed", vid, time.time() - t,
                                    {"error": str(e)}))
    out["clip_urls"] = clip_urls

    # ---- Voice
    vo_text = extract_voiceover_from_script(script)
    vo_info: Optional[dict] = None
    if include_vo and vo_text:
        t = time.time()
        try:
            vo_info = await synthesize(vo_text, voice_id=brief.brand.voiceId)
            trace.append(TraceEvent("voice", "done", vid, time.time() - t))
        except Exception as e:
            trace.append(TraceEvent("voice", "failed", vid, time.time() - t,
                                    {"error": str(e)}))
    out["voice"] = vo_info
    out["vo_text"] = vo_text

    # ---- Subtitles (heuristic — không có Whisper thì chia đều)
    total_s = vo_info.get("duration_s", brief.constraints.lengthSec) if vo_info else brief.constraints.lengthSec
    srt = build_srt_from_vo(vo_text, total_s) if vo_text else ""
    out["srt"] = srt
    trace.append(TraceEvent("subtitler", "done", vid, 0.0, {
        "has_srt": bool(srt),
        "duration_s": total_s,
    }))

    # ---- Edit (concat nếu có clip, color grade, logo overlay) — best effort
    final_urls: dict[str, str] = {}
    if clip_urls:
        from services.edit import concat_clips, export_aspect
        t = time.time()
        edited = concat_clips(clip_urls, transitions=getattr(refined, "transitions", []))
        if edited:
            subtitled = burn_subtitles(
                edited,
                srt,
                font=brief.brand.fonts.display,
                output_path=edited.rsplit(".", 1)[0] + "_subs.mp4",
            )
            branded = apply_logo(
                subtitled,
                brief.brand.logoUrl,
                placement=brand_lock.get("logo_placement", "top-right"),
            )
            palette = {
                "primary": brief.brand.palette.primary,
                "accent": brief.brand.palette.accent,
                "bg": brief.brand.palette.bg,
            }
            graded = apply_color_grade(branded, palette)
            for aspect in brief.constraints.aspect:
                final_urls[aspect] = export_aspect(graded, aspect)
            trace.append(TraceEvent("editor", "done", vid, time.time() - t, {
                "aspects": list(final_urls.keys()),
                "subtitles": bool(srt),
                "logo": bool(brief.brand.logoUrl),
            }))
        else:
            trace.append(TraceEvent("editor", "failed", vid, time.time() - t, {
                "reason": "no local clips after materialization",
            }))
    if include_video and not final_urls:
        from services.edit.local_render import render_publish_ready_video

        t = time.time()
        output_root = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "outputs")
        pack_preview = packer.run_packer(brief, brand_lock, variant, script)
        final_urls = render_publish_ready_video(
            brief,
            variant,
            script,
            pack_preview,
            output_root=output_root,
        )
        trace.append(TraceEvent("editor", "done", vid, time.time() - t, {
            "aspects": [aspect for aspect in final_urls.keys() if aspect != "cover"],
            "cover": final_urls.get("cover"),
            "mode": "local_publish_ready_fallback",
            "subtitles": bool(srt),
        }))
    out["final_video_urls"] = final_urls

    # ---- Brand lock check (deterministic)
    blc = brand_lock_check(brand_lock, refined.to_dict() if hasattr(refined, "to_dict") else {"shots": []})
    out["brand_lock_check"] = blc

    # ---- QA gate
    qa = run_qa(
        hook=script.get("hook", ""),
        scenes=script.get("scenes", []),
        cta=script.get("cta", ""),
        vo_text=vo_text,
        brand_lock={**brand_lock, "__brand_hint": blc.get("score", 80)},
        brief_theme=brief.theme,
        use_llm_judge=False,   # tắt LLM judge trong skeleton để chạy mock
    )
    if not qa.score.passed:
        t = time.time()
        script = _repair_script_for_qa(script, qa.feedback_for_director)
        storyboard = director.run_director(brief, brand_lock, variant, script)
        refined = visualist.run_visualist(brief, brand_lock, storyboard)
        vo_text = extract_voiceover_from_script(script)
        blc = brand_lock_check(brand_lock, refined.to_dict() if hasattr(refined, "to_dict") else {"shots": []})
        qa = run_qa(
            hook=script.get("hook", ""),
            scenes=script.get("scenes", []),
            cta=script.get("cta", ""),
            vo_text=vo_text,
            brand_lock={**brand_lock, "__brand_hint": blc.get("score", 80)},
            brief_theme=brief.theme,
            use_llm_judge=False,
        )
        out["script"] = script
        out["storyboard"] = refined.to_dict() if hasattr(refined, "to_dict") else {"shots": []}
        out["vo_text"] = vo_text
        out["brand_lock_check"] = blc
        trace.append(TraceEvent("qa_retry", "done", vid, time.time() - t, {
            "passed": qa.score.passed,
            "score": qa.score.total,
        }))
    out["qa"] = qa.to_dict() if hasattr(qa, "to_dict") else vars(qa)
    out["qa_passed"] = qa.score.passed

    # ---- Packer
    pack = packer.run_packer(brief, brand_lock, variant, script)
    out["pack"] = pack

    out["total_s"] = round(time.time() - t0, 2)
    return out


# ---------------------------------------------------------------------------
# Stage-based functions — for TRAE orchestration
# ---------------------------------------------------------------------------
async def run_plan_stage(brief: Brief) -> dict:
    """
    Stage 1: Planner + Brand Steward
    """
    trace: list[TraceEvent] = []
    t = time.time()
    plan = planner.run_planner(brief)
    variants = [v.to_dict() if hasattr(v, "to_dict") else {
        "id": v.id, "angle": v.angle, "hypothesis": v.hypothesis,
        "target_emotion": getattr(v, "target_emotion", ""),
        "visual_motif": getattr(v, "visual_motif", ""),
    } for v in plan.variants]
    trace.append(TraceEvent("planner", "done", elapsed_s=time.time() - t))

    t = time.time()
    lock = brand_steward.run_brand_steward(brief)
    trace.append(TraceEvent("brand_steward", "done", elapsed_s=time.time() - t))

    return {
        "plan": {"global_tone": plan.global_tone, "variants": variants},
        "brand_lock": lock,
        "trace": [ev.__dict__ for ev in trace],
    }


async def run_variant_stage(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
    *,
    include_vo: bool = True,
    include_video: bool = True,
) -> dict:
    """
    Stage 2: Run one variant crew (Copywriter → Director → Visualist → Renderer → Voice → Subtitle → Editor → QA → Packer)
    """
    trace: list[TraceEvent] = []
    result = await _render_one_variant(
        brief, brand_lock, variant, trace,
        include_vo=include_vo, include_video=include_video
    )
    result["trace"] = [ev.__dict__ for ev in trace]
    return result


async def run_finalize_stage(variants: list[dict], brief: Brief) -> dict:
    """
    Stage 3: Finalize pack and schedule handoff
    """
    trace: list[TraceEvent] = []
    t = time.time()
    trace.append(TraceEvent("finalize", "started", elapsed_s=0.0))

    publishable = [v for v in variants if v.get("qa_passed")]
    trace.append(TraceEvent("finalize", "done", elapsed_s=time.time() - t, {
        "total_variants": len(variants),
        "publishable": len(publishable),
    }))

    return {
        "publishable_variants": publishable,
        "trace": [ev.__dict__ for ev in trace],
    }


# ---------------------------------------------------------------------------
# Main entry — public
# ---------------------------------------------------------------------------
async def run_full_factory(
    brief: Brief,
    *,
    include_vo: bool = True,
    include_video: bool = True,
) -> dict:
    """
    Chạy toàn bộ content factory cho 1 brief:
    1. Planner
    2. Brand Steward
    3. 2+ crew song song
    4. Aggregate pack
    """
    trace: list[TraceEvent] = []
    wall_t0 = time.time()

    # 1. Plan
    t = time.time()
    plan = planner.run_planner(brief)
    variants = [v.to_dict() if hasattr(v, "to_dict") else {
        "id": v.id, "angle": v.angle, "hypothesis": v.hypothesis,
        "target_emotion": getattr(v, "target_emotion", ""),
        "visual_motif": getattr(v, "visual_motif", ""),
    } for v in plan.variants]
    trace.append(TraceEvent("planner", "done", elapsed_s=time.time() - t))

    # 2. Brand lock
    t = time.time()
    lock = brand_steward.run_brand_steward(brief)
    trace.append(TraceEvent("brand_steward", "done", elapsed_s=time.time() - t))

    # 3. Crew song song
    t = time.time()
    crews = await asyncio.gather(
        *(_render_one_variant(brief, lock, v, trace,
                              include_vo=include_vo,
                              include_video=include_video) for v in variants),
        return_exceptions=True,
    )
    trace.append(TraceEvent("crew_factory", "done", elapsed_s=time.time() - t))

    out_variants: list[dict] = []
    for v, crew in zip(variants, crews):
        if isinstance(crew, Exception):
            print(f"[factory] variant {v.get('id')} fail: {type(crew).__name__}: {crew}")
            print(traceback.format_exc())
            continue
        out_variants.append(crew)

    return {
        "plan": {"global_tone": plan.global_tone, "variants": variants},
        "brand_lock": lock,
        "variants": out_variants,
        "publishable_variants": [v for v in out_variants if v.get("qa_passed")],
        "trace": [ev.__dict__ for ev in trace],
        "wall_s": round(time.time() - wall_t0, 2),
        "brief": brief.to_dict() if hasattr(brief, "to_dict") else {},
    }


def _repair_script_for_qa(script: dict, feedback: str) -> dict:
    repaired = {
        **script,
        "hook": script.get("hook") or script.get("hook_instruction") or "Ban co biet dieu nay se thay doi cach ban nhin van de?",
        "cta": script.get("cta") or "Follow de xem them.",
        "qa_repair_feedback": feedback,
    }

    if len(str(repaired["hook"]).split()) < 5:
        repaired["hook"] = f"Ban co biet: {repaired['hook']}?"
    if len(str(repaired["cta"]).split()) < 3:
        repaired["cta"] = "Follow de xem them."

    scenes = []
    for index, scene in enumerate(script.get("scenes", []), start=1):
        patched = dict(scene)
        overlay = str(patched.get("text_overlay", "")).strip()
        if not overlay:
            overlay = f"Ly do {index}"
        words = overlay.split()
        patched["text_overlay"] = " ".join(words[:7])
        scenes.append(patched)
    repaired["scenes"] = scenes
    return repaired


def _image_url_for_mode(brief: Brief, mode: str) -> Optional[str]:
    if str(mode).lower() != "i2v":
        return None
    return _first_external_reference(brief)


def _reference_urls_for_mode(brief: Brief, mode: str) -> Optional[list[str]]:
    if str(mode).lower() != "r2v":
        return None
    refs = [url for url in brief.moodboardUrls if str(url).startswith(("http://", "https://"))]
    return refs or None


def _first_external_reference(brief: Brief) -> Optional[str]:
    for url in brief.moodboardUrls:
        if str(url).startswith(("http://", "https://")):
            return url
    return None
