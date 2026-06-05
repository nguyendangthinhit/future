"""
Planner Agent — agent #1 trong content factory.

Nhiệm vụ: đọc 1 brief, đề xuất ≥2 hướng sáng tạo (variant) khác biệt đủ rõ
để A/B test, kèm giả thuyết.

Output: PlanResult với list[VariantPlan].
"""

from __future__ import annotations

import json
import re
from typing import Any

from model_gateway import get_llm
from models.brief import Brief, PlanResult, VariantPlan


SYSTEM_PROMPT = """Bạn là Planner trong một BytePlus content factory.
Nhiệm vụ: đọc 1 brief và đề xuất các hướng sáng tạo KHÁC BIỆT đủ rõ để A/B test.

Quy tắc:
- Mỗi variant phải có 1 angle (góc kể) rõ ràng và khác hẳn các variant khác.
- Mỗi variant phải có 1 hypothesis có thể đo lường.
- Visual_motif phải gợi được style quay.
- TONE phải nhất quán với brand.toneOfVoice ở global_tone.

Output BẮT BUỘC là JSON theo schema:
{
  "global_tone": "<one sentence>",
  "variants": [
    {
      "id": "A",
      "angle": "<short label>",
      "hypothesis": "<measurable hypothesis>",
      "target_emotion": "<emotion>",
      "visual_motif": "<shot style>"
    },
    {"id": "B", ...}
  ]
}
JSON only. No prose, no markdown fences.
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


def _fallback_plan(brief: Brief) -> PlanResult:
    segment = f"{brief.audience.segment} {brief.audience.age}".lower()
    if "mom" in segment or "m?" in segment or "me " in segment or "30" in segment:
        angles = [
            ("busy-mom routine story", "audience thay san pham phu hop lich sinh hoat ban ron nen save/share cao hon"),
            ("family-safe product demo", "audience hieu loi ich thuc dung cho gia dinh nen CTR cao hon"),
        ]
        emotions = ["relief", "trust"]
        motifs = ["warm morning kitchen routine", "clean home product close-up"]
    elif "gen-z" in segment or "gen z" in segment or "18" in segment:
        angles = [
            ("trend-led Gen Z hook", "audience bi cuon vao 3 giay dau va comment cao hon"),
            ("product-led demo", "audience hieu tinh nang nhanh va CTR cao hon"),
        ]
        emotions = ["curiosity", "excitement"]
        motifs = ["fast first-person POV street style", "studio product hero with kinetic cuts"]
    else:
        angles = [
            ("emotional storytelling", "audience dong cam va share cao hon"),
            ("product-led demo", "audience hieu tinh nang ro va CTR cao hon"),
        ]
        emotions = ["curiosity", "trust"]
        motifs = ["first-person POV", "studio product hero"]

    variants = []
    for i in range(brief.variantsTarget):
        angle, hypothesis = angles[i % len(angles)]
        variants.append(VariantPlan(
            id=chr(ord("A") + i),
            angle=angle,
            hypothesis=hypothesis,
            target_emotion=emotions[i % len(emotions)],
            visual_motif=motifs[i % len(motifs)],
        ))
    return PlanResult(variants=variants, global_tone=brief.brand.toneOfVoice)


def run_planner(brief: Brief) -> PlanResult:
    user_prompt = (
        "BRIEF:\n" + brief.to_prompt_block()
        + f"\nSố variant cần sinh: {brief.variantsTarget}\n"
        + "Trả về JSON hợp lệ theo schema đã nêu trong system prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt, system=SYSTEM_PROMPT, json_mode=True, temperature=0.8,
        )
        data: Any = result.json or _try_json(result.text or "")
        if not data or "variants" not in data:
            raise ValueError("Planner LLM không trả JSON hợp lệ")
        variants = [VariantPlan.from_dict(v) for v in data["variants"][: brief.variantsTarget]]
        if not variants:
            raise ValueError("Plan rỗng")
        return PlanResult(variants=variants, global_tone=data.get("global_tone", ""))
    except Exception as e:
        print(f"[planner] fallback vì lỗi: {e}")
        return _fallback_plan(brief)
