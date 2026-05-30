from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from services.agents.pipeline import run_full_pipeline
from services.sheets import create_video_record, update_video_status, get_all_videos
from services.drive_service import upload_image
from services.serper import search_google
from services.ecomdy import generate_video, poll_video_status
import httpx, os, json
import asyncio

router = APIRouter()

async def process_video_background(
    record_id: str,
    raw_content: str,
    country_code: str,
    style_name: str,
    duration: int,
    video_type: str,
    extra_data: str,
    mascot_image_url: str,
    channel: str,
    scheduled_date: str,
):
    try:
        # 1. Chạy Multi-Agent Pipeline
        pipeline_result = run_full_pipeline(
            raw_content=raw_content,
            country_code=country_code,
            style_name=style_name,
            duration=duration,
            video_type=video_type,
            extra_data=extra_data,
            mascot_image_url=mascot_image_url,
        )
        
        director_output = pipeline_result.get("director_output", {})
        
        # Cập nhật Sheet: Đang render Ecomdy
        update_video_status(record_id, "processing")
        
        # 2. Gửi request tạo video lên Ecomdy
        ecomdy_payload = {
            "prompt": director_output.get("global_style_prompt", ""),
            "kling_prompts": director_output.get("ecomdy_prompts", [])
        }
        
        print(f"[{record_id}] Bắt đầu gọi Ecomdy API...")
        job_id = await generate_video(ecomdy_payload)
        
        # 3. Polling đợi kết quả
        print(f"[{record_id}] Ecomdy Job ID: {job_id}. Đang chờ render...")
        video_url = await poll_video_status(job_id)
        
        print(f"[{record_id}] Render xong! URL: {video_url}")
        
        # Cập nhật Sheet: Đã render xong
        update_video_status(record_id, "rendered", {"video_url": video_url})
        
        # 4. Gửi sang n8n Webhook để lên lịch đăng bài
        n8n_url = os.getenv("N8N_WEBHOOK_URL")
        if n8n_url and n8n_url != "http://your-n8n.com/webhook/create-video":
            n8n_payload = {
                "sheet_id": record_id,
                "channel": channel,
                "video_url": video_url,
                "caption": pipeline_result.get("script", {}).get("title", ""),
                "scheduled_date": scheduled_date,
                "callback_url": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/video/callback",
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                try:
                    await client.post(n8n_url, json=n8n_payload)
                    print(f"[{record_id}] Đã đẩy sang n8n thành công.")
                except Exception as e:
                    print(f"Warning: Failed to call n8n webhook: {e}")
                    
    except Exception as e:
        print(f"[{record_id}] Error in background processing: {e}")
        update_video_status(record_id, "failed", {"error_log": str(e)})


@router.post("/create")
async def create_video(
    background_tasks: BackgroundTasks,
    video_type: str = Form(...),
    channel: str = Form(...),
    scheduled_date: str = Form(...),
    raw_content: str = Form(...),
    style_id: str = Form(...),
    style_name: str = Form(...),
    duration: int = Form(...),
    country_code: str = Form(default="VN"),
    use_google_data: bool = Form(default=False),
    search_keyword: str = Form(default=""),
    mascot_image: UploadFile = File(default=None),
):
    try:
        # 1. Upload ảnh Mascot (nếu có) lên Google Drive ngay lập tức
        mascot_image_url = None
        if mascot_image and mascot_image.filename:
            mascot_image_url = await upload_image(mascot_image)

        # 2. Lấy data Google nếu user yêu cầu
        extra_data = ""
        if use_google_data and search_keyword:
            extra_data = search_google(search_keyword)

        # 3. Tạo record rỗng (trạng thái pending) trong Sheet
        record_data = {
            "video_type": video_type,
            "channel": channel,
            "scheduled_date": scheduled_date,
            "raw_content": raw_content,
            "style_id": style_id,
            "style_name": style_name,
            "duration": duration,
            "country_hook": country_code,
            "status": "pending",
        }
        record_id = create_video_record(record_data)
        
        # 4. Giao việc nặng cho Background Task
        background_tasks.add_task(
            process_video_background,
            record_id=record_id,
            raw_content=raw_content,
            country_code=country_code,
            style_name=style_name,
            duration=duration,
            video_type=video_type,
            extra_data=extra_data,
            mascot_image_url=mascot_image_url,
            channel=channel,
            scheduled_date=scheduled_date
        )
        
        return {
            "id": record_id,
            "status": "pending",
            "message": "Video đang được tạo ngầm (Background Task). Hệ thống sẽ thông báo khi hoàn tất.",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/callback")
async def video_callback(data: dict):
    """n8n gọi vào endpoint này sau khi render & đăng xong"""
    sheet_id = data.get("sheet_id")
    status = data.get("status", "done")
    video_url = data.get("video_url", "")
    post_id = data.get("post_id", "")
    
    update_video_status(sheet_id, status, {
        "video_url": video_url,
        "post_id": post_id,
    })
    return {"message": "Callback nhận thành công"}

@router.get("/list")
def list_videos():
    return get_all_videos()

@router.get("/status/{record_id}")
def get_video_status(record_id: str):
    all_videos = get_all_videos()
    for v in all_videos:
        if v.get("id") == record_id:
            return v
    raise HTTPException(status_code=404, detail="Video không tìm thấy")
