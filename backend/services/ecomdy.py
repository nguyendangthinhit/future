import os
import httpx
import asyncio

ECOMDY_API_URL = "https://api.ecomdy.co/v1"

async def generate_video(prompt_data: dict) -> str:
    """
    Gọi Ecomdy API để yêu cầu tạo video.
    Trả về job_id để polling trạng thái.
    """
    api_key = os.getenv("ECOMDY_API_KEY")
    if not api_key:
        print("Warning: ECOMDY_API_KEY is not set. Simulating generation.")
        return "mock_job_id"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # Tùy thuộc vào spec của Ecomdy, payload sẽ chứa prompt, style,...
        # Dữ liệu prompt_data sẽ chứa các ecomdy_prompts và global_style_prompt
        response = await client.post(
            f"{ECOMDY_API_URL}/video/generate",
            json=prompt_data,
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code in (200, 201, 202):
            data = response.json()
            return data.get("id")
        else:
            print(f"Error calling Ecomdy API: {response.text}")
            raise Exception(f"Ecomdy API failed with status {response.status_code}")

async def poll_video_status(job_id: str, max_retries: int = 60, delay_seconds: int = 5) -> str:
    """
    Polling Ecomdy API để đợi kết quả video (polling mỗi {delay_seconds} giây).
    Trả về video_url khi hoàn thành.
    """
    if job_id == "mock_job_id":
        await asyncio.sleep(5)
        return "https://www.w3schools.com/html/mov_bbb.mp4"
        
    api_key = os.getenv("ECOMDY_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    async with httpx.AsyncClient() as client:
        for _ in range(max_retries):
            response = await client.get(
                f"{ECOMDY_API_URL}/jobs/{job_id}",
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    return data.get("output_url")
                elif status in ["failed", "error"]:
                    raise Exception("Video generation failed on Ecomdy side.")
                    
            # Đợi trước khi poll lại
            await asyncio.sleep(delay_seconds)
            
        raise Exception("Polling timeout: Video generation took too long.")
