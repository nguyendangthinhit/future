"""
Pipeline — điểm vào cho content factory.

Hai entry point:
1. ``run_full_pipeline(...)`` — giữ NGUYÊN signature cũ để code cũ
   (routers/video.py) vẫn gọi được. Bên trong wrap lại theo format mới.
2. ``run_full_factory(brief)`` — entry point mới cho routers/factory.py.
   Planner → 2 crew song song (copywriter → director → visualist → ...)
   → brand_steward inject vào mọi agent.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any, Optional

from models.brief import Brief

# Agent mới
from . import brand_steward, copywriter, director, packer, planner, visualist


# ---------------------------------------------------------------------------
# Entry point mới — dùng bởi routers/factory.py
# ---------------------------------------------------------------------------
async def run_variant_crew(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
) -> dict:
    """
    Chạy 1 crew (copywriter -> director -> visualist -> packer) cho 1 variant.
    Trả về dict đầy đủ để merge vào pack cuối.
    """
    # Copywriter (đồng bộ — gọi LLM)
    script_obj = copywriter.run_copywriter(brief, brand_lock, variant)
    script = script_obj.to_dict() if hasattr(script_obj, "to_dict") else {
        "hook": getattr(script_obj, "hook", ""),
        "scenes": [vars(s) for s in getattr(script_obj, "scenes", [])],
        "cta": getattr(script_obj, "cta", ""),
    }

    # Director
    storyboard = director.run_director(brief, brand_lock, variant, script)

    # Visualist (refine prompts)
    refined = visualist.run_visualist(brief, brand_lock, storyboard)

    # Packer
    pack = packer.run_packer(brief, brand_lock, variant, script)

    return {
        "variant_id": variant["id"],
        "variant_angle": variant.get("angle", ""),
        "script": script,
        "storyboard": refined.to_dict() if hasattr(refined, "to_dict") else {"shots": []},
        "pack": pack,
    }


async def run_full_factory(brief: Brief) -> dict:
    """
    Pipeline chính của content factory:
    1. Planner -> 2+ variants
    2. Brand Steward -> brand_lock (chia sẻ)
    3. asyncio.gather: 2 crew chạy song song
    4. Aggregate pack.json cho UI render
    """
    # 1. Plan
    plan = planner.run_planner(brief)
    variants = [
        {
            "id": v.id, "angle": v.angle, "hypothesis": v.hypothesis,
            "target_emotion": getattr(v, "target_emotion", ""),
            "visual_motif": getattr(v, "visual_motif", ""),
        }
        for v in plan.variants
    ]

    # 2. Brand lock (chia sẻ cho mọi crew)
    lock = brand_steward.run_brand_steward(brief)

    # 3. Song song
    crews = await asyncio.gather(
        *(run_variant_crew(brief, lock, v) for v in variants),
        return_exceptions=True,
    )

    # 4. Aggregate
    out_variants = []
    for v, crew_out in zip(variants, crews):
        if isinstance(crew_out, Exception):
            print(f"[factory] crew {v['id']} fail: {crew_out}")
            continue
        out_variants.append(crew_out)

    return {
        "plan": {"global_tone": plan.global_tone, "variants": variants},
        "brand_lock": lock,
        "variants": out_variants,
        "brief": brief.to_dict() if hasattr(brief, "to_dict") else {},
    }


# ---------------------------------------------------------------------------
# Entry point cũ — wrap lại để tương thích ngược với routers/video.py
# ---------------------------------------------------------------------------
def run_full_pipeline(
    raw_content: str,
    country_code: str,
    style_name: str,
    duration: int = 60,
    video_type: str = "entertainment",
    extra_data: str = "",
    mascot_image_url: Optional[str] = None,
    target_language: str = "Tiếng Việt",
) -> dict:
    """
    Backward-compatible wrapper. Cố gắng map các tham số cũ sang Brief
    rồi gọi pipeline mới (chạy sync 1 lần).
    """
    from . import scriptwriter as legacy_sw

    # Thử load country profile & case studies (giống code cũ)
    try:
        country_profile = _load_country_profile(country_code)
        case_studies = _load_case_studies(country_code)
    except Exception:
        country_profile, case_studies = {"country_name": country_code}, []

    # Chạy agents cũ (giữ nguyên để code cũ hoạt động)
    try:
        script = legacy_sw.run_scriptwriter(
            raw_content=raw_content,
            country_profile=country_profile,
            case_studies=case_studies,
            duration=duration,
            video_type=video_type,
            extra_data=extra_data,
            target_language=target_language,
        )
    except Exception as e:
        print(f"[legacy_pipeline] scriptwriter fallback: {e}")
        script = _fallback_legacy_script(raw_content, duration, target_language)

    if "error" in script:
        script = _fallback_legacy_script(raw_content, duration, target_language)

    director_output = _run_legacy_director(
        script=script,
        style_name=style_name,
        mascot_image_url=mascot_image_url,
        duration=duration,
        target_language=target_language,
    )
    return {
        "script": script,
        "director_output": director_output,
        "country_profile": country_profile,
        "final_prompt_summary": director_output.get("global_style_prompt", ""),
    }


# ---------------------------------------------------------------------------
# helpers (mirror code cũ)
# ---------------------------------------------------------------------------
def _load_country_profile(country_code: str) -> dict:
    import json
    profile_path = os.path.join(os.path.dirname(__file__), "../data/country_profiles.json")
    if not os.path.exists(profile_path):
        return {"country_name": country_code}
    with open(profile_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    return profiles.get(country_code, profiles.get("VN", {}))


def _load_case_studies(country_code: str) -> list:
    import json
    path = os.path.join(os.path.dirname(__file__), "../data/viral_case_studies.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        all_cases = json.load(f)
    return [c for c in all_cases if c.get("country") == country_code][:2]


def _fallback_legacy_script(raw_content: str, duration: int, target_language: str) -> dict:
    scene_count = max(3, min(6, duration // 5 if duration else 3))
    seconds_per_scene = max(3, round(duration / scene_count)) if scene_count else duration
    scenes = []
    for idx in range(scene_count):
        start = idx * seconds_per_scene
        end = duration if idx == scene_count - 1 else min(duration, (idx + 1) * seconds_per_scene)
        scenes.append({
            "scene_id": idx + 1,
            "timestamp": f"{start}s - {end}s",
            "action": f"Visual scene {idx + 1} based on: {raw_content}",
            "dialogue": raw_content if idx == 0 else f"Key point {idx + 1} for {target_language} audience.",
            "text_overlay": f"Point {idx + 1}",
            "emotion": "curious",
        })
    return {
        "title": raw_content[:80] or "Auto generated video",
        "hook_instruction": f"Open with a strong visual hook about: {raw_content}",
        "scenes": scenes,
        "background_music_mood": "upbeat social video",
        "cta": "Follow for more.",
    }


def _run_legacy_director(
    *,
    script: dict,
    style_name: str,
    mascot_image_url: Optional[str],
    duration: int,
    target_language: str,
) -> dict:
    fallback = _fallback_legacy_director(
        script, style_name, mascot_image_url, duration, target_language
    )

    try:
        from model_gateway import get_llm

        prompt = f"""
You are a video director. Convert this short-video script into Ecomdy/Kling camera prompts.

STYLE: {style_name}
TARGET LANGUAGE FOR ANY TEXT: {target_language}
MASCOT IMAGE URL: {mascot_image_url or ""}
SCRIPT JSON:
{json.dumps(script, ensure_ascii=False)}

Return valid JSON only:
{{
  "ecomdy_prompts": [
    {{
      "scene_id": 1,
      "duration_seconds": 5,
      "prompt": "English camera prompt with subject, action, camera, lighting, color, motion",
      "negative_prompt": "Chinese text, Asian characters, watermarks, wrong fonts, gibberish"
    }}
  ],
  "global_style_prompt": "overall English visual style prompt",
  "recommended_aspect_ratio": "9:16",
  "mascot_image_url": "{mascot_image_url or ""}"
}}
"""
        result = get_llm().generate(prompt, json_mode=True, temperature=0.5)
        data = result.json or _try_parse_json(result.text or "")
        if not data or "ecomdy_prompts" not in data:
            return fallback
        data.setdefault("global_style_prompt", fallback["global_style_prompt"])
        data.setdefault("recommended_aspect_ratio", "9:16")
        data.setdefault("mascot_image_url", mascot_image_url or "")
        return data
    except Exception as e:
        print(f"[legacy_pipeline] director fallback: {e}")
        return fallback


def _fallback_legacy_director(
    script: dict,
    style_name: str,
    mascot_image_url: Optional[str],
    duration: int,
    target_language: str,
) -> dict:
    scenes = script.get("scenes", []) or []
    scene_duration = max(3, round(duration / max(1, len(scenes)))) if duration else 5
    prompts = []
    for idx, scene in enumerate(scenes, start=1):
        action = scene.get("action", "")
        overlay = scene.get("text_overlay", "")
        text_instruction = (
            f" Render text in {target_language} clearly: {overlay}."
            if overlay else ""
        )
        prompts.append({
            "scene_id": scene.get("scene_id", idx),
            "duration_seconds": scene_duration,
            "prompt": (
                f"{style_name or 'social video'} vertical 9:16 shot, {action}, "
                "dynamic camera movement, polished lighting, clear subject, "
                f"mobile-first composition.{text_instruction}"
            ),
            "negative_prompt": "Chinese text, Asian characters, watermarks, wrong fonts, gibberish",
        })
    return {
        "ecomdy_prompts": prompts,
        "global_style_prompt": (
            f"{style_name or 'Modern social video'}, vertical 9:16, fast paced, "
            "brand-safe, clear subject, high retention opening."
        ),
        "recommended_aspect_ratio": "9:16",
        "mascot_image_url": mascot_image_url or "",
    }


def _try_parse_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        pass
    import re
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None
