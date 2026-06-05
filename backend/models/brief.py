"""
Brief schema — nguồn sự thật duy nhất cho cả frontend và backend.

Dùng dataclass thuần (không phụ thuộc pydantic) để có thể chạy được trong
mọi môi trường. Khi deploy production có thể thay bằng pydantic.BaseModel
mà không phải đổi call site (cùng __init__ signature).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal, Optional


# ---------------------------------------------------------------------------
# Input brief
# ---------------------------------------------------------------------------
@dataclass
class BrandPalette:
    primary: str = "#000000"
    accent: str = "#FFFFFF"
    bg: str = "#000000"


@dataclass
class BrandFonts:
    display: str = "Arial"
    body: str = "Arial"


@dataclass
class Brand:
    name: str = ""
    toneOfVoice: str = "neutral"
    palette: BrandPalette = field(default_factory=BrandPalette)
    fonts: BrandFonts = field(default_factory=BrandFonts)
    logoUrl: Optional[str] = None
    voiceId: Optional[str] = None
    claimsAllowed: list[str] = field(default_factory=list)
    claimsForbidden: list[str] = field(default_factory=list)


@dataclass
class Audience:
    segment: str = "general"
    age: str = "all"
    locale: str = "vi-VN"


@dataclass
class Constraints:
    lengthSec: int = 20
    aspect: list[str] = field(default_factory=lambda: ["9:16"])
    mustInclude: list[str] = field(default_factory=list)
    mustAvoid: list[str] = field(default_factory=list)


@dataclass
class Brief:
    """Brief đầu vào cho content factory. 1 brief → ≥2 variant."""

    theme: str = ""
    brand: Brand = field(default_factory=Brand)
    audience: Audience = field(default_factory=Audience)
    platform: str = "tiktok"  # tiktok | reels | shorts | all
    constraints: Constraints = field(default_factory=Constraints)
    moodboardUrls: list[str] = field(default_factory=list)
    variantsTarget: int = 2

    def __post_init__(self) -> None:
        if not self.theme or not str(self.theme).strip():
            raise ValueError("theme không được rỗng")
        self.variantsTarget = max(1, min(2, int(self.variantsTarget or 1)))
        # Tự động nhận dict cho nested fields nếu caller truyền từ JSON
        if isinstance(self.brand, dict):
            d = dict(self.brand)
            d.setdefault("palette", {})
            d.setdefault("fonts", {})
            pal = d.pop("palette", {})
            fnt = d.pop("fonts", {})
            self.brand = Brand(
                **{k: v for k, v in d.items() if k in Brand.__dataclass_fields__},
                palette=BrandPalette(**{k: v for k, v in pal.items() if k in BrandPalette.__dataclass_fields__}) if pal else BrandPalette(),
                fonts=BrandFonts(**{k: v for k, v in fnt.items() if k in BrandFonts.__dataclass_fields__}) if fnt else BrandFonts(),
            )
        if isinstance(self.audience, dict):
            self.audience = Audience(**{k: v for k, v in self.audience.items() if k in Audience.__dataclass_fields__})
        if isinstance(self.constraints, dict):
            self.constraints = Constraints(**{k: v for k, v in self.constraints.items() if k in Constraints.__dataclass_fields__})

    def to_prompt_block(self) -> str:
        """Serialize ngắn gọn để nhét vào prompt."""
        return (
            f"Theme: {self.theme}\n"
            f"Brand: {self.brand.name} (tone: {self.brand.toneOfVoice})\n"
            f"Platform: {self.platform} | Length: {self.constraints.lengthSec}s\n"
            f"Audience: {self.audience.segment} ({self.audience.age}, {self.audience.locale})\n"
            f"ClaimsAllowed: {self.brand.claimsAllowed}\n"
            f"ClaimsForbidden: {self.brand.claimsForbidden}\n"
            f"MustInclude: {self.constraints.mustInclude}\n"
            f"MustAvoid: {self.constraints.mustAvoid}\n"
        )

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Output schema cho các agent
# ---------------------------------------------------------------------------
@dataclass
class VariantPlan:
    id: str                       # "A" | "B" | ...
    angle: str
    hypothesis: str
    target_emotion: str = ""
    visual_motif: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "VariantPlan":
        return cls(
            id=str(d.get("id", "A")),
            angle=d.get("angle", ""),
            hypothesis=d.get("hypothesis", ""),
            target_emotion=d.get("target_emotion", ""),
            visual_motif=d.get("visual_motif", ""),
        )


@dataclass
class PlanResult:
    variants: list[VariantPlan]
    global_tone: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "PlanResult":
        return cls(
            variants=[VariantPlan.from_dict(v) for v in d.get("variants", [])],
            global_tone=d.get("global_tone", ""),
        )


@dataclass
class ScriptScene:
    scene_id: int
    t_start: float
    t_end: float
    action: str = ""
    voiceover: str = ""
    text_overlay: str = ""
    shot_id: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "ScriptScene":
        return cls(
            scene_id=int(d.get("scene_id", 1)),
            t_start=float(d.get("t_start", 0.0)),
            t_end=float(d.get("t_end", 1.0)),
            action=d.get("action", ""),
            voiceover=d.get("voiceover", "") or d.get("dialogue", ""),
            text_overlay=d.get("text_overlay", ""),
            shot_id=d.get("shot_id", ""),
        )


@dataclass
class ScriptResult:
    hook: str
    scenes: list[ScriptScene]
    cta: str = ""
    title_options: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "ScriptResult":
        return cls(
            hook=d.get("hook", ""),
            scenes=[ScriptScene.from_dict(s) for s in d.get("scenes", [])],
            cta=d.get("cta", ""),
            title_options=d.get("title_options", []),
        )

    def to_dict(self) -> dict:
        return {
            "hook": self.hook,
            "scenes": [asdict(s) for s in self.scenes],
            "cta": self.cta,
            "title_options": self.title_options,
        }


@dataclass
class ShotSpec:
    shot_id: str
    duration_s: int
    mode: str = "t2v"  # t2v | i2v | r2v
    visual_prompt: str = ""
    needs_reference: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "ShotSpec":
        return cls(
            shot_id=str(d.get("shot_id", "s1")),
            duration_s=int(d.get("duration_s", 5)),
            mode=d.get("mode", "t2v"),
            visual_prompt=d.get("visual_prompt", ""),
            needs_reference=bool(d.get("needs_reference", False)),
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StoryboardResult:
    shots: list[ShotSpec]
    transitions: list[str] = field(default_factory=list)
    pacing: str = "normal"

    @classmethod
    def from_dict(cls, d: dict) -> "StoryboardResult":
        return cls(
            shots=[ShotSpec.from_dict(s) for s in d.get("shots", [])],
            transitions=d.get("transitions", []),
            pacing=d.get("pacing", "normal"),
        )

    def to_dict(self) -> dict:
        return {
            "shots": [s.to_dict() for s in self.shots],
            "transitions": self.transitions,
            "pacing": self.pacing,
        }


# ---------------------------------------------------------------------------
# QA
# ---------------------------------------------------------------------------
@dataclass
class QAScore:
    hook: int = 0
    brand: int = 0
    compliance: int = 0
    audio: int = 0
    pacing: int = 0
    caption: int = 0
    cta: int = 0

    @property
    def total(self) -> int:
        weights = {
            "hook": 0.25, "brand": 0.20, "compliance": 0.20,
            "audio": 0.10, "pacing": 0.10, "caption": 0.10, "cta": 0.05,
        }
        return int(round(sum(getattr(self, k) * w for k, w in weights.items())))

    @property
    def passed(self) -> bool:
        return self.total >= 80

    def to_dict(self) -> dict:
        return asdict(self) | {"total": self.total, "passed": self.passed}


@dataclass
class QAResult:
    score: QAScore
    notes: list[str] = field(default_factory=list)
    feedback_for_director: str = ""

    def to_dict(self) -> dict:
        return {
            "score": self.score.to_dict(),
            "notes": self.notes,
            "feedback_for_director": self.feedback_for_director,
        }
