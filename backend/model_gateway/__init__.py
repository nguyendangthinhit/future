"""
model_gateway
=============

Lớp trừu tượng hóa model provider để dễ dàng swap giữa:
- legacy:  Gemini (LLM) + Ecomdy (video)  -- đang dùng hiện tại
- byteplus: Seed 2.0 / ModelArk (LLM) + Seedance 2.0 (video)  -- sẽ dùng khi có key

Chọn provider qua env var ``MODEL_BACKEND`` (mặc định: ``legacy``).

Usage:
    from model_gateway import get_llm, get_video
    llm = get_llm()                # trả về LLMClient (Gemini hoặc Seed2)
    video = get_video()            # trả về VideoClient (Ecomdy hoặc Seedance)

Mọi call site chỉ cần biết interface, KHÔNG cần biết provider đang chạy.
Khi có API BytePlus thật, chỉ cần:
  1. điền ``BYTEPLUS_*`` keys vào .env
  2. set ``MODEL_BACKEND=byteplus``
Không phải đụng vào code caller.
"""

from .factory import get_llm, get_video, current_backend, reset_for_tests

__all__ = ["get_llm", "get_video", "current_backend", "reset_for_tests"]
