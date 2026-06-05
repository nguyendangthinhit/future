"""
Brand Steward Agent — agent #2.

Nhiệm vụ: khóa brand guidelines (palette, font, logo placement, claim whitelist)
và cảnh báo claim nguy hiểm. Output được TIÊM vào mọi prompt downstream
nên mọi agent con đều thấy cùng 1 brand_lock.
"""

from __future__ import annotations

import json
import re
from typing import Any

from model_gateway import get_llm
from models.brief import Brief


SYSTEM_PROMPT = """Bạn là Brand Steward. Khóa bộ guidelines để mọi agent khác
phải tuân thủ. Output JSON:
{
  "tone_of_voice_rules": ["...", "..."],
  "palette_rules": {"must_use": ["#hex", ...], "avoid": ["#hex", ...]},
  "font_rules": {"display": "FontName", "body": "FontName"},
  "logo_placement": "top-right" | "top-left" | "bottom-right" | "bottom-left" | "watermark",
  "claims_compliance": {
    "whitelist": ["..."],          // claim được phép xuất hiện
    "blacklist": ["..."],          // claim bị cấm
    "rephrase_suggestions": {}     // claim cấm -> gợi ý thay thế
  },
  "do": ["..."],                   // hành động nên làm
  "dont": ["..."]                  // hành động tránh
}
JSON only. No prose, no markdown.
"""


def _try_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def _fallback(brief: Brief) -> dict:
    return {
        "tone_of_voice_rules": [brief.brand.toneOfVoice],
        "palette_rules": {
            "must_use": [brief.brand.palette.primary, brief.brand.palette.accent],
            "avoid": ["#FFFFFF"] if brief.brand.palette.bg == "#FFFFFF" else [],
        },
        "font_rules": {
            "display": brief.brand.fonts.display,
            "body": brief.brand.fonts.body,
        },
        "logo_placement": "top-right",
        "claims_compliance": {
            "whitelist": brief.brand.claimsAllowed,
            "blacklist": brief.brand.claimsForbidden,
            "rephrase_suggestions": {},
        },
        "do": brief.constraints.mustInclude,
        "dont": brief.constraints.mustAvoid,
    }


def run_brand_steward(brief: Brief) -> dict:
    user_prompt = (
        "BRIEF:\n" + brief.to_prompt_block()
        + "\nSinh brand_lock JSON theo schema trong system prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt, system=SYSTEM_PROMPT, json_mode=True, temperature=0.3,
        )
        data: Any = result.json or _try_json(result.text or "")
        if not data:
            raise ValueError("BrandSteward LLM không trả JSON")
        # Đảm bảo 4 field bắt buộc tồn tại
        for k in ("tone_of_voice_rules", "palette_rules", "font_rules", "logo_placement",
                  "claims_compliance", "do", "dont"):
            data.setdefault(k, [] if k in ("tone_of_voice_rules", "do", "dont") else {})
        return data
    except Exception as e:
        print(f"[brand_steward] fallback vì lỗi: {e}")
        return _fallback(brief)


def brand_lock_to_prompt(brand_lock: dict) -> str:
    """Serialize brand_lock thành 1 block text để inject vào mọi agent downstream."""
    cc = brand_lock.get("claims_compliance", {})
    return (
        "BRAND_LOCK (PHẢI TUÂN THỦ):\n"
        f"- Tone rules: {brand_lock.get('tone_of_voice_rules', [])}\n"
        f"- Palette must-use: {brand_lock.get('palette_rules', {}).get('must_use', [])}\n"
        f"- Logo placement: {brand_lock.get('logo_placement', 'top-right')}\n"
        f"- Claims allowed: {cc.get('whitelist', [])}\n"
        f"- Claims FORBIDDEN (auto-reject nếu xuất hiện): {cc.get('blacklist', [])}\n"
        f"- Do: {brand_lock.get('do', [])}\n"
        f"- Don't: {brand_lock.get('dont', [])}\n"
    )
