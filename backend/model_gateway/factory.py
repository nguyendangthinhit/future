"""
Factory chọn backend theo env ``MODEL_BACKEND``.

- ``legacy``  (mặc định): Gemini + Ecomdy — dùng code hiện tại, không cần key mới.
- ``byteplus``: Seed 2.0 + Seedance 2.0 — bật khi có BYTEPLUS_*_API_KEY.

Cú pháp:
    from model_gateway import get_llm, get_video, current_backend
    backend_name = current_backend()   # "legacy" | "byteplus"
    llm = get_llm()
    video = get_video()
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from .interfaces import LLMClient, VideoClient


_VALID = ("legacy", "byteplus")


def current_backend() -> str:
    """Đọc env MODEL_BACKEND, mặc định 'legacy'."""
    name = os.getenv("MODEL_BACKEND", "legacy").strip().lower()
    if name not in _VALID:
        # Không crash — fallback về legacy để app vẫn chạy
        print(f"[model_gateway] MODEL_BACKEND={name!r} không hợp lệ. Fallback về 'legacy'.")
        return "legacy"
    return name


def reset_for_tests() -> None:
    """Xóa cache — dùng trong test khi đổi env động."""
    _get_llm_cached.cache_clear()
    _get_video_cached.cache_clear()


@lru_cache(maxsize=1)
def _get_llm_cached(backend: str) -> LLMClient:
    if backend == "byteplus":
        from .byteplus_backend import Seed2Client
        return Seed2Client()
    from .legacy_backend import LegacyLLMClient
    return LegacyLLMClient()


@lru_cache(maxsize=1)
def _get_video_cached(backend: str) -> VideoClient:
    if backend == "byteplus":
        from .byteplus_backend import SeedanceVideoClient
        return SeedanceVideoClient()
    from .legacy_backend import LegacyVideoClient
    return LegacyVideoClient()


def get_llm() -> LLMClient:
    """Trả về LLM client theo backend hiện tại. Singleton (cache)."""
    return _get_llm_cached(current_backend())


def get_video() -> VideoClient:
    """Trả về Video client theo backend hiện tại. Singleton (cache)."""
    return _get_video_cached(current_backend())
