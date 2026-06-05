"""
Ví dụ dùng model_gateway (KHÔNG thay đổi code cũ — chỉ tham khảo).

Khi nào migrate từ legacy sang byteplus:
  1. thêm vào .env:
        MODEL_BACKEND=byteplus
        BYTEPLUS_SEED2_API_KEY=...
        BYTEPLUS_SEEDANCE_API_KEY=...
  2. set MODEL_BACKEND=legacy nếu muốn quay lại Gemini/Ecomdy.
"""

import asyncio
import os

from model_gateway import get_llm, get_video, current_backend


def demo_llm() -> None:
    print(f"[demo] backend = {current_backend()}")
    llm = get_llm()
    print(f"[demo] llm provider = {llm.provider}")
    result = llm.generate(
        "Trả về JSON với 1 key 'ping' và value 'pong'.",
        json_mode=True,
    )
    print("[demo] text:", result.text[:200])
    print("[demo] json:", result.json)


async def demo_video() -> None:
    video = get_video()
    print(f"[demo] video provider = {video.provider}")
    job = await video.submit(
        "A neon coffee cup spinning on a wet street, cinematic",
        mode="t2v",
        duration_s=5,
        aspect="9:16",
        seed=42,
    )
    print(f"[demo] job_id = {job.job_id}")
    url = await video.poll(job.job_id, max_retries=3, delay_seconds=2)
    print(f"[demo] video_url = {url}")


if __name__ == "__main__":
    demo_llm()
    asyncio.run(demo_video())
