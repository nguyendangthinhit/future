import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

ECOMDY_API_URL = "https://api.ecomdy.co/v1"

async def test_video_generation():
    print("=== TEST ECOMDY API - CINEMATIC QUALITY ===\n")
    
    api_key = os.getenv("ECOMDY_API_KEY")
    if not api_key:
        print("❌ ECOMDY_API_KEY chưa được cấu hình trong .env")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Vấn đề đã được xác định: Các server như Unsplash, Wikipedia chặn bot tải ảnh tự động, 
    # khiến TikTok không thể tải ảnh về được. 
    # Nhưng host picsum.photos thì luôn cho phép!
    # Lần này ta dùng ảnh cún con độ phân giải cao (tỷ lệ 9:16 cinematic) từ picsum.
    payload = {
        "prompt": "Cinematic close-up of a beautiful black puppy looking directly at the camera. Soft volumetric lighting, hyper-realistic 8k, slow motion. The puppy blinks its eyes softly and tilts its head gracefully. Highly detailed, Unreal Engine 5 render.",
        "image_url": "https://picsum.photos/id/237/720/1280.jpg",
    }
    
    print("Kịch bản (Prompt):")
    print(payload["prompt"])
    print(f"\nẢnh gốc: {payload['image_url']}\n")
    
    async with httpx.AsyncClient() as client:
        print("1. Gọi POST /video/generate ...")
        resp = await client.post(
            f"{ECOMDY_API_URL}/video/generate",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        
        if resp.status_code not in (200, 201, 202):
            print("❌ Gửi generate thất bại!")
            print(resp.text)
            return
        
        data = resp.json().get("data", {})
        job_id = data.get("job_id") or data.get("id")
        
        if not job_id:
            print("❌ Không nhận được job_id!")
            return
            
        print(f"✅ Gửi thành công! Job ID: {job_id}")
        
        print("2. Polling chờ render (có thể mất 1-3 phút)...\n")
        for i in range(60):
            await asyncio.sleep(5)
            
            poll_resp = await client.get(
                f"{ECOMDY_API_URL}/jobs/{job_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10.0,
            )
            
            poll_data = poll_resp.json().get("data", {})
            status = str(poll_data.get("status", "")).upper()
            output_url = poll_data.get("output_url")
            
            print(f"   [{i+1}] status={status} ...")
            
            if output_url:
                print(f"\n🎉 THÀNH CÔNG! Video URL: {output_url}")
                return
            
            if status in ("FAILED", "ERROR"):
                error = poll_data.get("error", {})
                print(f"\n❌ FAILED!")
                print(f"   Error: {error.get('message')}")
                return
        
        print("\n❌ TIMEOUT.")

if __name__ == "__main__":
    asyncio.run(test_video_generation())
