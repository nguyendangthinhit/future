"""
Factory router — endpoint mới cho BX-T1 content factory.

POST /api/v1/factory/generate   — chạy 1 brief, trả 2+ variant
GET  /api/v1/factory/trace     — lấy trace gần nhất (đơn giản, in-memory)
"""

from __future__ import annotations

import json
import os
import time

import httpx
from fastapi import APIRouter, HTTPException

from models.brief import Brief
from services.orchestrator import run_full_factory, run_plan_stage, run_variant_stage, run_finalize_stage


router = APIRouter()

# Trace in-memory — production nên ghi Sheets hoặc file
_LAST_TRACE: list[dict] = []


@router.post("/generate")
async def generate(payload: dict) -> dict:
    """
    Body: dict matching Brief schema (xem models/brief.py).
    Returns: full pack (plan + brand_lock + variants[]).
    """
    try:
        brief = Brief(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid Brief: {e}")

    t0 = time.time()
    try:
        result = await run_full_factory(brief)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Factory fail: {e}")

    result["elapsed_s"] = round(time.time() - t0, 2)
    _LAST_TRACE.clear()
    _LAST_TRACE.extend(result.get("trace", []))
    _write_last_pack(result)
    return result


@router.get("/trace")
async def get_trace() -> dict:
    """Lấy trace gần nhất (dùng cho UI live-DAG)."""
    return {"trace": _LAST_TRACE}


@router.get("/last-pack")
async def get_last_pack() -> dict:
    output_path = _last_pack_path()
    if not os.path.exists(output_path):
        return {"pack": None}
    with open(output_path, "r", encoding="utf-8") as file:
        return {"pack": json.load(file)}


@router.get("/samples")
async def get_samples() -> dict:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    briefs_dir = os.path.join(root, "briefs")
    samples = []
    if os.path.isdir(briefs_dir):
        for name in sorted(os.listdir(briefs_dir)):
            if not name.endswith(".json"):
                continue
            path = os.path.join(briefs_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as file:
                    payload = json.load(file)
                samples.append({
                    "file": name,
                    "theme": payload.get("theme", ""),
                    "brand": payload.get("brand", {}).get("name", ""),
                    "audience": payload.get("audience", {}).get("segment", ""),
                    "payload": payload,
                })
            except Exception:
                continue
    return {"samples": samples}


@router.post("/demo-one-input-change")
async def demo_one_input_change(payload: dict | None = None) -> dict:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    default_path = os.path.join(root, "briefs", "coffee-genz.json")
    if payload:
        base_payload = payload
    else:
        with open(default_path, "r", encoding="utf-8") as file:
            base_payload = json.load(file)

    changed_payload = json.loads(json.dumps(base_payload, ensure_ascii=False))
    changed_payload.setdefault("audience", {})
    changed_payload["audience"]["segment"] = "millennial mom Vietnam"
    changed_payload["audience"]["age"] = "30-42"

    before = await run_full_factory(Brief(**base_payload), include_vo=False, include_video=False)
    after = await run_full_factory(Brief(**changed_payload), include_vo=False, include_video=False)
    result = {"changed_field": "audience", "before": before, "after": after}

    output_dir = os.path.join(root, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "one_input_change_demo.json"), "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    return result


@router.post("/schedule-handoff")
async def schedule_handoff(payload: dict) -> dict:
    output_path = _last_pack_path()
    if not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="No factory pack available")

    with open(output_path, "r", encoding="utf-8") as file:
        pack = json.load(file)

    variant_id = payload.get("variant_id")
    variants = pack.get("publishable_variants") or pack.get("variants") or []
    variant = next((item for item in variants if item.get("variant_id") == variant_id), None)
    if variant is None:
        raise HTTPException(status_code=404, detail=f"Variant not found: {variant_id}")

    handoff = {
        "variant_id": variant_id,
        "platform": payload.get("platform", "tiktok"),
        "scheduled_at": payload.get("scheduled_at", ""),
        "caption": payload.get("caption") or variant.get("pack", {}).get("caption", ""),
        "title": variant.get("pack", {}).get("title", ""),
        "hashtags": variant.get("pack", {}).get("hashtags", []),
        "final_video_urls": variant.get("final_video_urls", []),
        "qa": variant.get("qa", {}),
        "source": "content_factory",
        "created_at": round(time.time()),
    }

    output_dir = os.path.join(os.path.dirname(output_path))
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "schedule_handoff.json"), "w", encoding="utf-8") as file:
        json.dump(handoff, file, ensure_ascii=False, indent=2)

    webhook_url = os.getenv("N8N_WEBHOOK_URL", "")
    if webhook_url and "your-n8n.com" not in webhook_url:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(webhook_url, json=handoff)
            handoff["n8n_status"] = "sent"
        except Exception as e:
            handoff["n8n_status"] = f"failed: {e}"
    else:
        handoff["n8n_status"] = "skipped"

    return {"handoff": handoff}


@router.post("/stage/plan")
async def stage_plan(payload: dict) -> dict:
    """
    Stage 1: Planner + Brand Steward
    Body: dict matching Brief schema
    Returns: plan + brand_lock + trace
    """
    try:
        brief = Brief(**payload)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid Brief: {e}")

    t0 = time.time()
    try:
        result = await run_plan_stage(brief)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan stage fail: {e}")

    result["elapsed_s"] = round(time.time() - t0, 2)
    _LAST_TRACE.extend(result.get("trace", []))
    return result


@router.post("/stage/variant")
async def stage_variant(payload: dict) -> dict:
    """
    Stage 2: Run one variant crew
    Body: {
        "brief": Brief dict,
        "brand_lock": dict,
        "variant": dict,
        "include_vo": bool (optional),
        "include_video": bool (optional)
    }
    Returns: variant result + trace
    """
    try:
        brief = Brief(**payload["brief"])
        brand_lock = payload["brand_lock"]
        variant = payload["variant"]
        include_vo = payload.get("include_vo", True)
        include_video = payload.get("include_video", True)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload: {e}")

    t0 = time.time()
    try:
        result = await run_variant_stage(
            brief, brand_lock, variant,
            include_vo=include_vo, include_video=include_video
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant stage fail: {e}")

    result["elapsed_s"] = round(time.time() - t0, 2)
    _LAST_TRACE.extend(result.get("trace", []))
    return result


@router.post("/stage/finalize")
async def stage_finalize(payload: dict) -> dict:
    """
    Stage 3: Finalize pack
    Body: {
        "brief": Brief dict,
        "variants": list[dict]
    }
    Returns: publishable_variants + trace
    """
    try:
        brief = Brief(**payload["brief"])
        variants = payload["variants"]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid payload: {e}")

    t0 = time.time()
    try:
        result = await run_finalize_stage(variants, brief)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Finalize stage fail: {e}")

    result["elapsed_s"] = round(time.time() - t0, 2)
    _LAST_TRACE.extend(result.get("trace", []))
    _write_last_pack({
        "brief": brief.to_dict() if hasattr(brief, "to_dict") else {},
        "variants": variants,
        "publishable_variants": result.get("publishable_variants"),
        "trace": _LAST_TRACE,
        "wall_s": result["elapsed_s"],
    })
    return result


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "router": "factory"}


def _write_last_pack(result: dict) -> None:
    try:
        output_path = _last_pack_path()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[factory] write output pack skipped: {e}")


def _last_pack_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root, "outputs", "last_factory_pack.json")
