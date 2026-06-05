"""
Interfaces chung cho LLM + Video provider.

Mọi backend (legacy / byteplus) phải implement đúng 2 interface này.
Caller chỉ phụ thuộc vào interface, không phụ thuộc vào backend cụ thể.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
@dataclass
class LLMResult:
    """Kết quả trả về từ LLM — luôn có .text, optional .json (parsed)."""
    text: str
    json: Optional[dict] = None
    raw: Any = None
    provider: str = ""
    model: str = ""


class LLMClient(ABC):
    """Interface cho mọi text-generation provider (Gemini, Seed2, FPT, ...)."""

    provider: str = "abstract"

    @abstractmethod
    def generate(
        self,
        prompt: str,
        *,
        system: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False,
        max_retries: int = 3,
    ) -> LLMResult:
        """Sinh text từ prompt. Nếu json_mode=True, ép model trả JSON hợp lệ."""


# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------
@dataclass
class VideoJob:
    """Một job render video — provider-agnostic."""
    job_id: str
    provider: str
    mode: str = "t2v"            # t2v | i2v | r2v | avatar
    extra: Optional[dict] = None  # status_url, raw response, ...


class VideoClient(ABC):
    """Interface cho mọi video render provider (Ecomdy, Seedance, ...)."""

    provider: str = "abstract"

    @abstractmethod
    async def submit(
        self,
        prompt: str,
        *,
        mode: str = "t2v",                # t2v | i2v | r2v | avatar
        image_url: Optional[str] = None,
        reference_urls: Optional[list[str]] = None,
        avatar_id: Optional[str] = None,
        script: Optional[str] = None,
        duration_s: int = 5,
        aspect: str = "9:16",
        seed: Optional[int] = None,
    ) -> VideoJob:
        """Submit một job render, trả về job_id để polling."""

    @abstractmethod
    async def poll(self, job_id: str, *, max_retries: int = 60, delay_seconds: int = 5) -> str:
        """Poll cho tới khi xong, trả về video_url. Throw nếu fail/timeout."""
