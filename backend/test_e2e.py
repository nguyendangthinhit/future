"""
Test E2E Flow theo đúng cách User dùng:
1. Gọi POST /api/v1/video/create (đúng như Frontend gọi)
2. Nhận về record_id + status="pending"
3. Poll GET /api/v1/video/status/{id} để xem tiến trình
4. Khi status="rendered" → hiển thị video_url

Yêu cầu: Backend đang chạy tại http://localhost:8000
Chạy: python test_e2e.py
"""

import asyncio
import httpx
import os
import io

BACKEND_URL = "http://localhost:8000"

# ==============================
# Ảnh test: Con cún đen từ picsum (đã xác nhận luôn hoạt động với TikTok Symphony)
# ==============================
IMAGE_URL_FOR_TEST = "https://picsum.photos/id/237/720/1280.jpg"

async def download_test_image():
    """Tải ảnh về RAM để giả lập user upload file."""
    async with httpx.AsyncClient() as client:
        r = await client.get(IMAGE_URL_FOR_TEST, timeout=15, follow_redirects=True)
        r.raise_for_status()
        return r.content

async def run_e2e_test():
    print("=" * 55)
    print("  TEST E2E FLOW - MÔ PHỎNG ĐÚNG HÀNH VI USER")
    print("=" * 55)

    # ---- Kiểm tra Backend đang chạy chưa ----
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{BACKEND_URL}/docs", timeout=5)
        print("✅ Backend đang chạy tại", BACKEND_URL)
    except Exception:
        print(f"❌ Backend CHƯA chạy tại {BACKEND_URL}!")
        print("   Hãy mở terminal khác và chạy: uvicorn main:app --reload")
        return

    # ---- BƯỚC 1: User điền form và bấm "Tạo Video" ----
    print("\n📝 BƯỚC 1: User điền form và bấm 'Tạo Video'...")

    print("   Đang tải ảnh mascot về RAM để upload...")
    image_bytes = await download_test_image()

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{BACKEND_URL}/api/v1/video/create",
            data={
                "video_type":     "entertainment",
                "channel":        "tiktok",
                "scheduled_date": "2026-06-10",
                "raw_content":    "Một chú cún đen đáng yêu đang vui đùa trong nắng sớm, nhảy nhót, lắc đuôi, cực kỳ đáng yêu và sinh động.",
                "style_id":       "style_001",
                "style_name":     "Cinematic Cute",
                "duration":       "30",
                "country_code":   "VN",
                "use_google_data": "false",
                "search_keyword": "",
            },
            files={
                "mascot_image": ("puppy.jpg", image_bytes, "image/jpeg"),
            },
        )

        if response.status_code != 200:
            print(f"❌ Gọi /create thất bại! Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return

        result = response.json()
        record_id = result.get("id")
        print(f"✅ Hệ thống nhận yêu cầu! Record ID: {record_id}")
        print(f"   Message: {result.get('message')}")

    # ---- BƯỚC 2: Poll trạng thái (giả lập Frontend polling mỗi 5 giây) ----
    print(f"\n⏳ BƯỚC 2: Đang chờ Background Task xử lý (upload ảnh → AI → Ecomdy)...")
    print(f"   (Poll GET /api/v1/video/status/{record_id} mỗi 5 giây)\n")

    final_status = None
    for i in range(120):  # Tối đa 10 phút
        await asyncio.sleep(5)
        async with httpx.AsyncClient(timeout=10) as client:
            poll = await client.get(f"{BACKEND_URL}/api/v1/video/status/{record_id}")
            if poll.status_code != 200:
                continue
            data = poll.json()

        status = data.get("status", "unknown")
        video_url = data.get("video_url", "")
        error_log = data.get("error_log", "")

        print(f"   [{i+1}] status = {status.upper()}", end="")
        if video_url:
            print(f" | video_url = {video_url[:60]}...")
        else:
            print()

        if status in ("rendered", "done"):
            final_status = "success"
            print(f"\n🎉 THÀNH CÔNG! Video đã render xong.")
            print(f"   ▶  Video URL: {video_url}")
            break
        elif status == "failed":
            final_status = "failed"
            print(f"\n❌ THẤT BẠI! Lý do: {error_log}")
            break

    if final_status is None:
        print("\n⚠️  TIMEOUT sau 10 phút. Background task có thể vẫn đang chạy.")
        print(f"   Kiểm tra thủ công: GET {BACKEND_URL}/api/v1/video/status/{record_id}")

    # ---- BƯỚC 3: Xem danh sách video trong DB ----
    print(f"\n📋 BƯỚC 3: Kiểm tra danh sách video trong Database...")
    async with httpx.AsyncClient(timeout=10) as client:
        list_resp = await client.get(f"{BACKEND_URL}/api/v1/video/list")
        videos = list_resp.json()

    print(f"   Tổng số video trong DB: {len(videos)}")
    if videos:
        latest = videos[0]
        print(f"   Video mới nhất:")
        print(f"     - ID:        {latest.get('id')}")
        print(f"     - Status:    {latest.get('status')}")
        print(f"     - Channel:   {latest.get('channel')}")
        print(f"     - Created:   {latest.get('created_at')}")
        print(f"     - Video URL: {latest.get('video_url') or '(chưa có)'}")

    print("\n" + "=" * 55)
    print("  KẾT THÚC TEST E2E")
    print("=" * 55)

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
