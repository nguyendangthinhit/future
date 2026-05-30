from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.sheets import get_verify_list, update_video_status
from services.agents.pipeline import run_full_pipeline
from services.ecomdy import generate_video, poll_video_status
import httpx, os

router = APIRouter()

async def process_verified_video_background(record_id: str, ecomdy_payload: dict, channel: str, caption: str, scheduled_date: str):
    try:
        # Cập nhật trạng thái
        update_video_status(record_id, "processing")
        
        # 1. Gọi Ecomdy API
        print(f"[{record_id}] Bắt đầu gọi Ecomdy API từ Verify...")
        job_id = await generate_video(ecomdy_payload)
        
        # 2. Polling
        print(f"[{record_id}] Ecomdy Job ID: {job_id}. Đang chờ render...")
        video_url = await poll_video_status(job_id)
        
        print(f"[{record_id}] Render xong! URL: {video_url}")
        
        # Cập nhật Sheet
        update_video_status(record_id, "rendered", {"video_url": video_url})
        
        # 3. Gửi sang n8n Webhook
        n8n_url = os.getenv("N8N_WEBHOOK_URL")
        if n8n_url and n8n_url != "http://your-n8n.com/webhook/create-video":
            n8n_payload = {
                "sheet_id": record_id,
                "channel": channel,
                "video_url": video_url,
                "caption": caption,
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


@router.get("/list")
def list_verify():
    return get_verify_list()

@router.post("/{record_id}/approve")
async def approve_video(record_id: str, background_tasks: BackgroundTasks, data: dict = {}):
    """User approve ý tưởng → Chạy Ecomdy ngầm → hệ thống tự động trigger n8n"""
    
    all_verify = get_verify_list()
    record = next((r for r in all_verify if r.get("id") == record_id), None)
    if not record:
        raise HTTPException(status_code=404, detail="Không tìm thấy ý tưởng")
    
    # Nếu user có sửa nội dung trước khi approve → chạy lại pipeline
    if data.get("edited_content"):
        pipeline_result = run_full_pipeline(
            raw_content=data["edited_content"],
            country_code=record.get("country_hook", "VN"),
            style_name=record.get("style_name", ""),
            duration=int(record.get("duration", 60)),
        )
        final_prompt = pipeline_result["director_output"].get("global_style_prompt", "")
        ecomdy_prompts = pipeline_result["director_output"].get("ecomdy_prompts", [])
        caption = pipeline_result.get("script", {}).get("title", record.get("raw_content", ""))
    else:
        final_prompt = record.get("final_prompt", "")
        ecomdy_prompts = []
        caption = record.get("raw_content", "")
        
    ecomdy_payload = {
        "prompt": final_prompt,
        "kling_prompts": ecomdy_prompts
    }
    
    # Cập nhật Sheet
    update_video_status(record_id, "pending")
    
    # Kích hoạt chạy ngầm
    background_tasks.add_task(
        process_verified_video_background,
        record_id=record_id,
        ecomdy_payload=ecomdy_payload,
        channel=record.get("channel", "tiktok"),
        caption=caption,
        scheduled_date=record.get("scheduled_date", "")
    )
    
    return {"message": f"Đã approve {record_id}, đang tạo video..."}

@router.post("/{record_id}/reject")
def reject_video(record_id: str):
    update_video_status(record_id, "rejected")
    return {"message": f"Đã reject {record_id}"}
