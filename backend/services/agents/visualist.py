"""
Visualist Agent — agent #5.

Refine visual_prompt từ Director thành prompt chất lượng cao cho Seedance 2.0.
Thêm chi tiết camera, lighting, style để model hiểu rõ hơn.
"""

from __future__ import annotations

import json
import re

from model_gateway import get_llm
from models.brief import Brief, StoryboardResult, ShotSpec


SYSTEM_PROMPT = """Bạn là Visualist. Nhiệm vụ: refine danh sách visual_prompt
để TỐI ƯU cho Seedance 2.0 (T2V / I2V / R2V).

Quy tắc refine mỗi prompt:
- Bắt đầu bằng subject cụ thể.
- Thêm camera: shot type, camera motion.
- Thêm lighting: cinematic, golden hour, neon, studio softbox...
- Thêm style: 9:16 vertical, photorealistic, 24fps, 30fps, product-shot, UGC-style.
- Tránh abstract, tránh text trong frame, tránh brand name cụ thể.
- Độ dài prompt: 25-60 từ.

Output JSON giữ nguyên cấu trúc shots[], chỉ thay visual_prompt.
"""


def run_visualist(
    brief: Brief,
    brand_lock: dict,
    storyboard: StoryboardResult,
) -> StoryboardResult:
    from .brand_steward import brand_lock_to_prompt

    payload = storyboard.to_dict()
    user_prompt = (
        brand_lock_to_prompt(brand_lock)
        + f"\nTHEME: {brief.theme}\n"
        + f"LengthSec={brief.constraints.lengthSec}\n"
        + f"STORYBOARD:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
        + "Trả về JSON cùng cấu trúc, chỉ thay visual_prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt, system=SYSTEM_PROMPT, json_mode=True, temperature=0.5,
        )
        data = result.json
        if not data:
            m = re.search(r"\{[\s\S]*\}", result.text or "")
            data = json.loads(m.group(0)) if m else None
        if not data or "shots" not in data:
            raise ValueError("Visualist không trả JSON hợp lệ")
        shots = [ShotSpec.from_dict(s) for s in data["shots"][:6]]
        return StoryboardResult(
            shots=shots,
            transitions=data.get("transitions", storyboard.transitions),
            pacing=data.get("pacing", storyboard.pacing),
        )
    except Exception as e:
        print(f"[visualist] giữ nguyên prompt gốc vì lỗi: {e}")
        return storyboard
