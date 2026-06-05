"""
Director Agent — agent #4.

Input: brief + brand_lock + variant + script.
Output: StoryboardResult với shots[] (A-roll/B-roll, transitions, pacing).
"""

from __future__ import annotations

import json
import re
from typing import Any

from model_gateway import get_llm
from models.brief import Brief, StoryboardResult, ShotSpec


SYSTEM_PROMPT = """Bạn là Director. Từ script đã có, hãy lên shot list cụ thể.

Mỗi shot phải có:
- shot_id: "s1", "s2", ...
- duration_s: số nguyên (tổng tất cả shot = lengthSec)
- mode: "t2v" | "i2v" | "r2v"
- visual_prompt: prompt tiếng Anh tối ưu cho Seedance 2.0
- needs_reference: true nếu cần brand reference

Quy tắc:
- Tối đa 6 shot / variant.
- Shot đầu tiên NÊN là t2v (set visual world).
- Shot demo sản phẩm NÊN là i2v.
- B-roll lifestyle NÊN là r2v.

Output JSON:
{
  "shots": [
    {"shot_id": "s1", "duration_s": 4, "mode": "t2v", "visual_prompt": "...",
     "needs_reference": false}
  ],
  "transitions": ["cut", "swipe", "fade"],
  "pacing": "fast" | "normal" | "slow"
}
JSON only.
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


def _fallback(brief: Brief) -> StoryboardResult:
    L = brief.constraints.lengthSec
    n = min(6, max(3, L // 5))
    per = L // n
    modes = ["t2v", "i2v", "r2v", "t2v", "i2v", "t2v"]
    shots = []
    for i in range(n):
        shots.append(ShotSpec(
            shot_id=f"s{i+1}",
            duration_s=per,
            mode=modes[i % len(modes)],
            visual_prompt=(
                f"{brief.theme} cinematic shot {i+1}, "
                f"9:16 vertical, professional lighting, brand-safe"
            ),
            needs_reference=(i % 3 == 2),
        ))
    return StoryboardResult(
        shots=shots, transitions=["cut", "swipe"], pacing="normal",
    )


def run_director(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
    script: dict,
) -> StoryboardResult:
    from .brand_steward import brand_lock_to_prompt

    script_text = json.dumps(script, ensure_ascii=False, indent=2)
    user_prompt = (
        f"VARIANT: id={variant.get('id')}, angle={variant.get('angle')}\n\n"
        + brand_lock_to_prompt(brand_lock)
        + "\nSCRIPT (đã có từ copywriter):\n" + script_text
        + f"\nLength: {brief.constraints.lengthSec}s\n"
        + "Lên shot list JSON theo schema system prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt, system=SYSTEM_PROMPT, json_mode=True, temperature=0.6,
        )
        data: Any = result.json or _try_json(result.text or "")
        if not data or "shots" not in data:
            raise ValueError("Director LLM không trả JSON hợp lệ")
        shots = [ShotSpec.from_dict(s) for s in data["shots"][:6]]
        if not shots:
            raise ValueError("Director trả shots rỗng")
        return StoryboardResult(
            shots=shots,
            transitions=data.get("transitions", []),
            pacing=data.get("pacing", "normal"),
        )
    except Exception as e:
        print(f"[director] fallback vì lỗi: {e}")
        return _fallback(brief)
