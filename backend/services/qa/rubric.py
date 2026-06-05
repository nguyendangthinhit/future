"""
QA / Rubric — chấm điểm publishability theo 7 tiêu chí.

Hybrid: deterministic (regex / length) + LLM judge (khi có model).
Nếu không có model -> chỉ chấm deterministic, tổng tối đa ~60 điểm.
"""

from __future__ import annotations

import re
from typing import Any

from model_gateway import get_llm
from models.brief import QAResult, QAScore


# ---------------------------------------------------------------------------
# Deterministic checks
# ---------------------------------------------------------------------------
_FORBIDDEN_PATTERNS = [
    r"\bguaranteed?\b",          # claim bị cấm phổ biến
    r"\bcure[s]?\b",
    r"\b100%\s*effective\b",
]


def _check_compliance(vo_text: str, claims_forbidden: list[str]) -> int:
    """100 nếu không có claim cấm; trừ dần theo số vi phạm."""
    if not claims_forbidden:
        # fallback: check pattern mặc định
        violations = sum(
            1 for p in _FORBIDDEN_PATTERNS if re.search(p, vo_text, re.I)
        )
        return max(0, 100 - violations * 30)
    text = vo_text.lower()
    v = sum(1 for c in claims_forbidden if c.lower() in text)
    return max(0, 100 - v * 30)


def _check_hook(hook: str) -> int:
    """Hook mạnh nếu: 1-2 câu, có dấu chấm hỏi / số / "you" / "bạn"."""
    if not hook:
        return 0
    s = hook.strip()
    score = 50
    if 5 <= len(s.split()) <= 25:
        score += 20
    if re.search(r"\?|!|bạn|you|secret|bí mật|sốc|shocking", s, re.I):
        score += 20
    if re.search(r"\d+", s):
        score += 10
    return min(100, score)


def _check_pacing(scenes: list[dict]) -> int:
    """Pacing tốt nếu shot ngắn, đều, không có scene > 8s."""
    if not scenes:
        return 30
    durations = [
        float(s.get("t_end", 0)) - float(s.get("t_start", 0)) for s in scenes
    ]
    if any(d > 8 for d in durations):
        return 50
    if len(scenes) < 3:
        return 60
    return 90


def _check_caption(scenes: list[dict]) -> int:
    """Mỗi scene có text_overlay tối đa 7 từ -> 100."""
    if not scenes:
        return 50
    bad = [s for s in scenes if len(str(s.get("text_overlay", "")).split()) > 7]
    return max(0, 100 - len(bad) * 15)


def _check_cta(cta: str) -> int:
    if not cta:
        return 0
    s = cta.strip()
    score = 50
    if 3 <= len(s.split()) <= 12:
        score += 30
    if re.search(r"(mua|đăng ký|thử|click|xem|comment|share|save|follow)", s, re.I):
        score += 20
    return min(100, score)


# ---------------------------------------------------------------------------
# LLM judge cho hook strength (nếu có model)
# ---------------------------------------------------------------------------
def _llm_judge_hook(hook: str, brief_theme: str) -> int:
    """Hỏi LLM chấm hook 0-100. Nếu lỗi -> fallback deterministic."""
    if not hook:
        return 0
    prompt = (
        f"Chấm HOOK (câu mở đầu video ngắn) trên thang 0-100.\n"
        f"Brief theme: {brief_theme}\n"
        f"Hook: {hook}\n"
        "Tiêu chí: gây tò mò, sốc, relatable, dừng scroll.\n"
        "Chỉ trả 1 số nguyên 0-100, không giải thích."
    )
    try:
        r = get_llm().generate(prompt, temperature=0.2)
        m = re.search(r"\d+", r.text or "")
        return int(m.group(0)) if m else _check_hook(hook)
    except Exception:
        return _check_hook(hook)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def run_qa(
    *,
    hook: str,
    scenes: list[dict],
    cta: str,
    vo_text: str,
    brand_lock: dict,
    brief_theme: str,
    use_llm_judge: bool = True,
) -> QAResult:
    """
    Chấm điểm publishability.

    Tổng điểm theo trọng số (xem QAScore.total). Pass >= 80.
    """
    claims_forbidden = brand_lock.get("claims_compliance", {}).get("blacklist", [])
    hook_score = _llm_judge_hook(hook, brief_theme) if use_llm_judge else _check_hook(hook)

    score = QAScore(
        hook=hook_score,
        brand=int(brand_lock.get("__brand_hint", 80)),  # caller có thể override
        compliance=_check_compliance(vo_text, claims_forbidden),
        audio=70,                  # không đo LUFS trong skeleton
        pacing=_check_pacing(scenes),
        caption=_check_caption(scenes),
        cta=_check_cta(cta),
    )
    notes: list[str] = []
    if not score.passed:
        notes.append(f"Hook yếu ({score.hook}/100) — thử sốc hơn, có con số cụ thể.")
        if score.compliance < 80:
            notes.append("Có claim cấm trong VO — phải bỏ hoặc thay bằng whitelist.")
        if score.pacing < 70:
            notes.append("Shot quá dài (>8s) — chia nhỏ.")
        if score.cta < 60:
            notes.append("CTA không rõ — thêm 1 hành động duy nhất.")

    feedback = " | ".join(notes) if notes else "Đạt gate ≥80."
    return QAResult(score=score, notes=notes, feedback_for_director=feedback)
