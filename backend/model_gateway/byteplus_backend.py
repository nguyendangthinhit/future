"""
BytePlus backend — Seed 2.0 (ModelArk) cho LLM + Seedance 2.0 cho video.

Hiện tại chưa có API key, nên file này ở trạng thái SKELETON:
- Interface đã đầy đủ.
- Logic gọi API thật được tách riêng, raise NotImplementedError rõ ràng.
- KHÔNG ảnh hưởng tới legacy backend khi chưa bật.

Khi có key, chỉ cần:
  1. pip install byteplus-sdk  (hoặc dùng httpx như skeleton dưới)
  2. điền BYTEPLUS_*_API_KEY vào .env
  3. set MODEL_BACKEND=byteplus
  4. điền phần TODO trong _call_seed2() và _call_seedance()
"""

from __future__ import annotations

import os
from typing import Any, Optional

from .interfaces import LLMClient, LLMResult, VideoClient, VideoJob


# ---------------------------------------------------------------------------
# Seed 2.0 (ModelArk)  --  text generation
# ---------------------------------------------------------------------------
class Seed2Client(LLMClient):
    provider = "byteplus-seed2"

    def __init__(self) -> None:
        self.api_key = os.getenv("BYTEPLUS_SEED2_API_KEY", "")
        self.endpoint = os.getenv(
            "BYTEPLUS_SEED2_ENDPOINT",
            "https://ark.ap-southeast.bytepluses.com/api/v3/chat/completions",  # TODO: đổi sang endpoint chính thức khi có key
        )
        self.default_model = os.getenv("BYTEPLUS_SEED2_MODEL", "seed-2-0-pro")

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
        if not self.api_key:
            raise RuntimeError(
                "BYTEPLUS_SEED2_API_KEY chưa được set. "
                "Điền key vào .env hoặc tạm thời set MODEL_BACKEND=legacy."
            )

        # TODO: thay bằng SDK chính thức khi BytePlus công bố.
        # Skeleton dưới đây theo OpenAI-compatible schema mà ModelArk hay dùng.
        import json
        import requests

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        last_err: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                r = requests.post(self.endpoint, headers=headers, json=payload, timeout=60)
                if r.status_code != 200:
                    raise RuntimeError(f"Seed2 HTTP {r.status_code}: {r.text[:300]}")
                data = r.json()
                text = data["choices"][0]["message"]["content"]
                parsed = None
                if json_mode:
                    try:
                        parsed = json.loads(text)
                    except Exception:
                        parsed = None
                return LLMResult(
                    text=text, json=parsed, raw=data,
                    provider=self.provider, model=payload["model"],
                )
            except Exception as e:
                last_err = e
                if attempt + 1 >= max_retries:
                    break
        raise RuntimeError(f"Seed2 failed after {max_retries} attempts: {last_err}")


# ---------------------------------------------------------------------------
# Seedance 2.0  --  video generation (T2V / I2V / R2V)
# ---------------------------------------------------------------------------
class SeedanceVideoClient(VideoClient):
    provider = "byteplus-seedance"

    def __init__(self) -> None:
        self.api_key = os.getenv("BYTEPLUS_SEEDANCE_API_KEY", "")
        self.submit_endpoint = os.getenv(
            "BYTEPLUS_SEEDANCE_SUBMIT_URL",
            "https://ark.ap-southeast.bytepluses.com/api/v3/video/generations",  # TODO: chính thức
        )
        self.poll_endpoint_template = os.getenv(
            "BYTEPLUS_SEEDANCE_POLL_URL",
            "https://ark.ap-southeast.bytepluses.com/api/v3/video/generations/{job_id}",  # TODO: chính thức
        )

    async def submit(
        self,
        prompt: str,
        *,
        mode: str = "t2v",                  # t2v | i2v | r2v
        image_url: Optional[str] = None,
        reference_urls: Optional[list[str]] = None,
        avatar_id: Optional[str] = None,
        script: Optional[str] = None,
        duration_s: int = 5,
        aspect: str = "9:16",
        seed: Optional[int] = None,
    ) -> VideoJob:
        if not self.api_key:
            raise RuntimeError(
                "BYTEPLUS_SEEDANCE_API_KEY chưa được set. "
                "Điền key vào .env hoặc tạm thời set MODEL_BACKEND=legacy."
            )
        if mode == "avatar":
            raise NotImplementedError("Seedance chưa hỗ trợ avatar mode; dùng Ecomdy (legacy).")
        if mode in ("i2v", "r2v") and not (image_url or reference_urls):
            raise ValueError(f"Seedance mode={mode} cần image_url hoặc reference_urls.")

        import httpx

        payload: dict[str, Any] = {
            "model": "seedance-2-0",
            "prompt": prompt,
            "mode": mode,
            "duration": duration_s,
            "aspect_ratio": aspect,
        }
        if image_url:
            payload["image_url"] = image_url
        if reference_urls:
            payload["reference_urls"] = reference_urls
        if seed is not None:
            payload["seed"] = seed

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(self.submit_endpoint, json=payload, headers=headers)
            if r.status_code not in (200, 201, 202):
                raise RuntimeError(f"Seedance submit HTTP {r.status_code}: {r.text[:300]}")
            data = r.json()
            job_id = data.get("id") or data.get("job_id") or data.get("data", {}).get("job_id")
            if not job_id:
                raise RuntimeError(f"Seedance: không thấy job_id: {r.text[:300]}")
            return VideoJob(job_id=job_id, provider=self.provider, mode=mode, extra=data)

    async def poll(self, job_id: str, *, max_retries: int = 60, delay_seconds: int = 5) -> str:
        import asyncio
        import httpx

        url = self.poll_endpoint_template.format(job_id=job_id)
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(max_retries):
                r = await client.get(url, headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    status = str(data.get("status", "")).upper()
                    video_url = data.get("output_url") or data.get("video_url")
                    if video_url and status in ("COMPLETED", "SUCCESS", "SUCCEEDED", "DONE"):
                        return video_url
                    if status in ("FAILED", "ERROR"):
                        raise RuntimeError(f"Seedance job failed: {data}")
                await asyncio.sleep(delay_seconds)
        raise RuntimeError("Seedance polling timeout.")
