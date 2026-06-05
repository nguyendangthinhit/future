"""
Packer Agent — agent #11 (cuối).

Sinh cover art (dùng LLM tạo prompt ảnh), caption, hashtags, title A/B,
schedule hint. Output: pack.json để UI render.
"""

from __future__ import annotations

import json
import re
from typing import Any

from model_gateway import get_llm
from models.brief import Brief


SYSTEM_PROMPT = """Bạn là Packer. Tổng hợp mọi thứ thành output cuối cùng.

Output JSON:
{
  "title_options": ["A: ...", "B: ...", "C: ..."],   // 3 phiên bản cho A/B
  "caption": "<3-5 câu, có emoji, có CTA, có 1-2 hashtag chính>",
  "hashtags": ["#tag1", "#tag2", ...],               // 5-8 hashtag phụ
  "cover_art_prompt": "<prompt ảnh tỉ lệ 9:16, brand-safe, 30-50 từ>",
  "best_posting_window": "<vd: 'Mon-Wed 7-9pm ICT'>",
  "variant_id": "A" | "B" | "C"
}

Quy tắc:
- Caption phải tự nhiên, dùng được ngay (không chứa placeholder).
- Hashtags mix Vi/Anh phù hợp platform.
- Cover_art_prompt mô tả 1 frame đẹp nhất của video, 9:16, 1080x1920.
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


def _fallback(brief: Brief, variant_id: str) -> dict:
    return {
        "title_options": [brief.theme, f"{brief.brand.name} - {brief.theme}", f"Khám phá {brief.theme}"],
        "caption": f"{brief.theme}? Bạn đã thử chưa. {brief.brand.name} mang đến trải nghiệm mới. 👉 Xem ngay!",
        "hashtags": ["#fyp", "#trending", "#brand", f"#{brief.brand.name.lower()}"],
        "cover_art_prompt": (
            f"Hero shot of {brief.brand.name} product, cinematic lighting, "
            f"9:16 vertical, vibrant colors, brand-safe"
        ),
        "best_posting_window": "Mon-Wed 7-9pm ICT",
        "variant_id": variant_id,
    }


def run_packer(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
    script: dict,
) -> dict:
    from .brand_steward import brand_lock_to_prompt

    user_prompt = (
        f"VARIANT: id={variant['id']}, angle={variant['angle']}\n\n"
        + brand_lock_to_prompt(brand_lock)
        + "\nSCRIPT:\n" + json.dumps(script, ensure_ascii=False)
        + "\n" + brief.to_prompt_block()
        + "\nSinh pack JSON theo schema system prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt, system=SYSTEM_PROMPT, json_mode=True, temperature=0.7,
        )
        data: Any = result.json or _try_json(result.text or "")
        if not data:
            raise ValueError("Packer LLM không trả JSON")
        data.setdefault("variant_id", variant["id"])
        return data
    except Exception as e:
        print(f"[packer] fallback vì lỗi: {e}")
        return _fallback(brief, variant["id"])
