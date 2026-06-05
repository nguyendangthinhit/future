"""
Copywriter Agent — agent #3.

Input: brief + brand_lock + variant_plan (1 variant cụ thể).
Output: ScriptResult với hook + scenes + CTA + title options.
"""

from __future__ import annotations

import json
import re
from typing import Any

from model_gateway import get_llm
from models.brief import Brief, ScriptResult, ScriptScene


SYSTEM_PROMPT = """Bạn là Copywriter trong content factory. Viết kịch bản video ngắn
(TikTok / Reels / Shorts) theo 1 variant angle cụ thể.

Quy tắc:
- Tổng độ dài VO phải vừa {lengthSec}s khi đọc (~2.5 từ/giây cho tiếng Việt).
- Hook (3s đầu) phải gây tò mò / sốc / hài hước / relatable.
- Mỗi scene có 1 VO ngắn (<= 2 câu) và 1 text_overlay tối đa 7 từ.
- CTA cuối video phải rõ ràng, 1 hành động duy nhất.
- TUÂN THỦ brand_lock: không dùng claim cấm.
- Title options: 3 phiên bản để A/B test (≤ 60 ký tự mỗi cái).

Output JSON:
{
  "hook": "string",
  "scenes": [
    {
      "scene_id": 1,
      "t_start": 0.0, "t_end": 3.0,
      "action": "...",
      "voiceover": "...",
      "text_overlay": "...",
      "shot_id": "s1"
    }
  ],
  "cta": "string",
  "title_options": ["...", "...", "..."]
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


def _fallback(brief: Brief, variant_angle: str) -> ScriptResult:
    length_s = brief.constraints.lengthSec
    n_scenes = max(3, length_s // 5)
    audience = f"{brief.audience.segment} {brief.audience.age}".lower()
    is_mom = "mom" in audience or "m?" in audience or "me " in audience or "30" in audience
    is_genz = "gen-z" in audience or "gen z" in audience or "18" in audience

    if is_mom:
        hook = f"Mot phut yen tinh cho me ban ron: {brief.brand.name}."
        cta = "Luu lai de thu trong buoi sang mai."
        overlays = ["Nhanh gon cho me ban ron", "Hop routine gia dinh", "Thu hom nay"]
        voice_lines = [
            f"Khi buoi sang qua nhieu viec, {brief.brand.name} giup khoanh khac nho de de chiu hon.",
            "Cach dung don gian, thong diep ro rang, khong can noi qua da.",
            "Neu ban can mot lua chon nhanh va dang tin, hay thu ngay hom nay.",
        ]
    elif is_genz:
        if "product" in variant_angle.lower() or "demo" in variant_angle.lower():
            hook = f"Thu test nhanh {brief.brand.name}: co dang nhu loi don?"
            overlays = ["Test nhanh", "Can canh san pham", "Dang thu chu?"]
            voice_lines = [
                f"Day la phien ban demo nhanh de thay {brief.brand.name} xuat hien ro trong tung canh.",
                "Tap trung vao san pham, loi ich chinh va cach nguoi xem co the thu ngay.",
                "Neu ban muon mot lua chon gon va ro, day la diem can nho.",
            ]
        else:
            hook = f"Gen Z oi, {brief.theme} co dang viral vi dieu nay."
            overlays = ["Dung lai 3 giay", "Vibe nay qua quen", "Ban se thu chu?"]
            voice_lines = [
                f"Day la cach {brief.brand.name} bien mot khoanh khac quen thuoc thanh noi dung dang xem.",
                "Cat nhanh, mau ro, hook truc dien de giu nguoi xem tu dau.",
                "Neu thay dung vibe cua ban, comment de xem bien the tiep theo.",
            ]
        cta = "Comment neu ban muon xem ban tiep theo."
    else:
        hook = f"Ban co biet {brief.theme}?"
        cta = "Thu ngay hom nay."
        overlays = ["Diem dang chu y", "Loi ich chinh", "Thu ngay"]
        voice_lines = [
            f"Day la cau chuyen ngan ve {brief.brand.name} va nhu cau cua nguoi xem.",
            "Noi dung tap trung vao loi ich chinh va dieu can nho.",
            "Ket thuc bang mot hanh dong ro rang de nguoi xem lam tiep.",
        ]

    scenes = []
    for i in range(n_scenes):
        t0 = i * (length_s / n_scenes)
        t1 = (i + 1) * (length_s / n_scenes)
        scenes.append(ScriptScene(
            scene_id=i + 1,
            t_start=round(t0, 2),
            t_end=round(t1, 2),
            action=f"{variant_angle}: scene {i + 1} for {brief.audience.segment}",
            voiceover=voice_lines[i % len(voice_lines)],
            text_overlay=overlays[i % len(overlays)],
            shot_id=f"s{i+1}",
        ))

    return ScriptResult(
        hook=hook,
        scenes=scenes,
        cta=cta,
        title_options=[
            f"{brief.brand.name}: {variant_angle}",
            f"{brief.audience.segment} - {brief.brand.name}",
            f"{brief.theme[:48]}",
        ],
    )


def run_copywriter(
    brief: Brief,
    brand_lock: dict,
    variant: dict,
) -> ScriptResult:
    from .brand_steward import brand_lock_to_prompt
    user_prompt = (
        f"VARIANT: id={variant.get('id')}, angle={variant.get('angle')}, "
        f"target_emotion={variant.get('target_emotion')}\n\n"
        + brand_lock_to_prompt(brand_lock)
        + "\n" + brief.to_prompt_block()
        + f"\nLength: {brief.constraints.lengthSec}s\n"
        + "Sinh script JSON theo schema system prompt."
    )
    try:
        result = get_llm().generate(
            user_prompt,
            system=SYSTEM_PROMPT.replace("{lengthSec}", str(brief.constraints.lengthSec)),
            json_mode=True, temperature=0.85,
        )
        data: Any = result.json or _try_json(result.text or "")
        if not data or "scenes" not in data:
            raise ValueError("Copywriter LLM không trả JSON hợp lệ")
        return ScriptResult.from_dict(data)
    except Exception as e:
        print(f"[copywriter] fallback vì lỗi: {e}")
        return _fallback(brief, variant.get("angle", ""))
