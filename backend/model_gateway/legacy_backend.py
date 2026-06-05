"""
Legacy backend — wrap các service hiện có (Gemini + Ecomdy) vào interface mới.

KHÔNG đổi logic gốc, chỉ adapt. Khi có BytePlus key, không cần file này nữa.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Optional

from .interfaces import LLMClient, LLMResult, VideoClient, VideoJob


# ---------------------------------------------------------------------------
# LLM legacy  ->  dùng LLMManager (Gemini) có sẵn
# ---------------------------------------------------------------------------
class LegacyLLMClient(LLMClient):
    provider = "legacy-gemini"

    def __init__(self) -> None:
        # Lazy import để không kéo google.generativeai khi gateway import.
        # Nếu user chưa cài, sẽ chỉ fail khi gọi .generate() lần đầu.
        self._mgr = None

    def _manager(self):
        if self._mgr is None:
            from services.llm_manager import llm_manager
            self._mgr = llm_manager
        return self._mgr

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
        # Ghép system vào prompt nếu có (giữ tương thích code cũ)
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"

        # Nếu caller muốn JSON, ép model trả JSON
        if json_mode:
            full_prompt = (
                f"{full_prompt}\n\n"
                "IMPORTANT: Respond with valid JSON only. No prose, no markdown fences."
            )

        model_name = model or "gemini-2.5-flash"
        response = self._manager().generate_content_with_retry(
            full_prompt, model_name=model_name, max_retries=max_retries
        )
        text = (response.text or "").strip()

        parsed: Optional[dict] = None
        if json_mode:
            parsed = _try_parse_json(text)
        return LLMResult(text=text, json=parsed, raw=response,
                         provider=self.provider, model=model_name)


# ---------------------------------------------------------------------------
# Video legacy  ->  dùng ecomdy.py có sẵn
# ---------------------------------------------------------------------------
class LegacyVideoClient(VideoClient):
    provider = "legacy-ecomdy"

    async def submit(
        self,
        prompt: str,
        *,
        mode: str = "t2v",
        image_url: Optional[str] = None,
        reference_urls: Optional[list[str]] = None,
        avatar_id: Optional[str] = None,
        script: Optional[str] = None,
        duration_s: int = 5,
        aspect: str = "9:16",
        seed: Optional[int] = None,
    ) -> VideoJob:
        from services.ecomdy import generate_video, generate_avatar_video

        if mode == "avatar":
            payload = {"avatar_id": avatar_id, "script": script or prompt}
            job_id = await generate_avatar_video(payload)
        else:
            # Ecomdy Symphony BẮT BUỘC có image_url, fake fallback nếu thiếu
            payload = {
                "prompt": prompt,
                "image_url": image_url or "https://via.placeholder.com/1080x1920.png",
                "duration": duration_s,
                "aspect_ratio": aspect,
            }
            if seed is not None:
                payload["seed"] = seed
            job_id = await generate_video(payload)

        return VideoJob(job_id=job_id, provider=self.provider, mode=mode)

    async def poll(self, job_id: str, *, max_retries: int = 60, delay_seconds: int = 5) -> str:
        from services.ecomdy import poll_video_status
        return await poll_video_status(job_id, max_retries=max_retries, delay_seconds=delay_seconds)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _try_parse_json(text: str) -> Optional[dict]:
    import json
    # Cố gắng parse trực tiếp
    try:
        return json.loads(text)
    except Exception:
        pass
    # Tìm block ```json ... ``` nếu model lỡ wrap
    import re
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None
