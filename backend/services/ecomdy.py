import os
import httpx
import asyncio

ECOMDY_API_URL = "https://api.ecomdy.co/v1"


async def generate_video(prompt_data: dict) -> str:
    """
    Gọi Ecomdy API để yêu cầu tạo video. Trả về job_id để polling.

    Lưu ý (xác minh trực tiếp với API live):
    - Engine là image-to-video (Symphony / TikTok AIGC) -> prompt_data BẮT BUỘC
      có "image_url", thiếu sẽ fail ở phía engine ("image_url is required").
    - Response 202: {"success":true,"data":{"job_id":"...","status":"PENDING",
      "status_url":"..."},"meta":{"credits_used":10,...}}  -> job_id nằm ở data.data.job_id.
    - Mỗi lần generate tốn ~10 credits.
    """
    api_key = os.getenv("ECOMDY_API_KEY")
    if not api_key:
        print("Warning: ECOMDY_API_KEY is not set. Simulating generation.")
        return "mock_job_id"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ECOMDY_API_URL}/video/generate",
            json=prompt_data,
            headers=headers,
            timeout=30.0,
        )

        if response.status_code in (200, 201, 202):
            data = response.json().get("data", {})
            job_id = data.get("job_id") or data.get("id")
            if not job_id:
                raise Exception(f"Ecomdy: không tìm thấy job_id trong response: {response.text}")
            return job_id
        else:
            print(f"Error calling Ecomdy API: {response.text}")
            raise Exception(f"Ecomdy API failed with status {response.status_code}: {response.text}")


async def poll_video_status(job_id: str, max_retries: int = 60, delay_seconds: int = 5) -> str:
    """
    Polling Ecomdy API để đợi kết quả video. Trả về video_url khi hoàn thành.

    Response GET /jobs/{id} -> {"success":true,"data":{"id":"...","status":"PENDING|
    PROCESSING|COMPLETED|FAILED","output_url":null|"...","error":{"message":"..."}}}.
    Status viết HOA. Tín hiệu hoàn thành đáng tin nhất là có output_url.
    """
    if job_id == "mock_job_id":
        await asyncio.sleep(5)
        return "https://www.w3schools.com/html/mov_bbb.mp4"

    api_key = os.getenv("ECOMDY_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        for _ in range(max_retries):
            response = await client.get(
                f"{ECOMDY_API_URL}/jobs/{job_id}",
                headers=headers,
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                status = str(data.get("status", "")).upper()
                output_url = data.get("output_url")

                if output_url and status in ("COMPLETED", "SUCCESS", "SUCCEEDED", "DONE", "FINISHED"):
                    return output_url
                if output_url and status not in ("PENDING", "PROCESSING", "QUEUED", "RUNNING"):
                    return output_url
                if status in ("FAILED", "ERROR"):
                    error_data = data.get("error", {})
                    err_msg = error_data.get("message", "Unknown error")
                    err_code = error_data.get("code", "")
                    
                    # Dịch và giải thích lỗi cho User dễ hiểu
                    user_friendly_err = f"Lỗi render Ecomdy ({err_code}): {err_msg}"
                    
                    if "TikTok task failed" in err_msg or "incompatible with the image-animation model" in err_msg:
                        user_friendly_err = (
                            "Lỗi kiểm duyệt hoặc không tương thích ảnh từ TikTok AIGC. "
                            "Nguyên nhân thường gặp:\n"
                            "- Ảnh chứa khuôn mặt người thật bị chặn bởi chính sách Deepfake.\n"
                            "- Ảnh quá mờ, độ phân giải thấp, hoặc sai tỷ lệ.\n"
                            "👉 Cách khắc phục: Hãy thử đổi sang ảnh hoạt hình, 3D mascot, hoặc phong cảnh không có mặt người thật."
                        )
                    elif "image_url is required" in err_msg:
                        user_friendly_err = "Thiếu link ảnh. Engine TikTok Symphony bắt buộc phải có ảnh đầu vào (image_url) để tạo video."

                    # Log raw ra terminal cho Dev
                    print(f"[ECOMDY ERROR] Raw JSON: {response.text}")
                    
                    # Ném lỗi thân thiện cho User/Frontend
                    raise Exception(user_friendly_err)

            await asyncio.sleep(delay_seconds)

        raise Exception("Polling timeout: Video generation took too long.")
