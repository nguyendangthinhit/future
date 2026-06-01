from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional
from pydantic import BaseModel
from services.agents.pipeline import run_full_pipeline
from services.sheets import create_video_record, update_video_status, get_all_videos
from services.drive_service import upload_image
from services.serper import search_google
from services.ecomdy import generate_video, poll_video_status
from services.research import run_research_sync
import httpx, os, json
import asyncio

router = APIRouter()


class PreviewPromptRequest(BaseModel):
    content: str
    video_type: str = "entertainment"
    style_name: str = ""
    duration: int = 60
    country_code: str = "VN"
    use_google_data: bool = False
    search_keyword: str = ""
    research_brief: str = ""


def _format_prompt(script: dict, director: dict) -> str:
    """Gộp output 2 agent thành 1 block text dễ đọc để hiển thị trên web."""
    lines = []
    if script.get("title"):
        lines.append(f"🎬 TIÊU ĐỀ: {script['title']}")
    if script.get("hook_instruction"):
        lines.append(f"\n🪝 HOOK (0-5s): {script['hook_instruction']}")

    scenes = script.get("scenes", [])
    if scenes:
        lines.append("\n📝 KỊCH BẢN THEO CẢNH:")
        for s in scenes:
            lines.append(f"  • [{s.get('timestamp','')}] {s.get('action','')}")
            if s.get("dialogue"):
                lines.append(f"      Thoại: {s['dialogue']}")
            if s.get("text_overlay"):
                lines.append(f"      Text overlay: {s['text_overlay']}")

    if script.get("background_music_mood"):
        lines.append(f"\n🎵 NHẠC NỀN: {script['background_music_mood']}")
    if script.get("cta"):
        lines.append(f"📣 CTA: {script['cta']}")

    if director.get("global_style_prompt"):
        lines.append(f"\n🎨 GLOBAL STYLE PROMPT:\n{director['global_style_prompt']}")

    ecomdy_prompts = director.get("ecomdy_prompts", [])
    if ecomdy_prompts:
        lines.append("\n🎥 CAMERA PROMPTS (gửi sang engine render):")
        for p in ecomdy_prompts:
            lines.append(f"  • Scene {p.get('scene_id','')} ({p.get('duration_seconds','')}s): {p.get('prompt','')}")
            if p.get("negative_prompt"):
                lines.append(f"      Negative: {p['negative_prompt']}")

    if director.get("recommended_aspect_ratio"):
        lines.append(f"\n📐 Tỉ lệ khung hình đề xuất: {director['recommended_aspect_ratio']}")

    return "\n".join(lines).strip()


@router.post("/preview-prompt")
def preview_prompt(req: PreviewPromptRequest):
    """Chạy CHỈ 2 agent (biên kịch + đạo diễn) và trả prompt — KHÔNG render, KHÔNG ghi Sheet.
    Dùng để xem trước chất lượng prompt trên web trước khi tạo video thật."""
    try:
        extra_data = ""
        if req.research_brief:
            extra_data = req.research_brief
        elif req.use_google_data and req.search_keyword:
            import json as _json
            brief = run_research_sync(req.search_keyword, req.content, req.duration)
            extra_data = _json.dumps(brief, ensure_ascii=False)

        result = run_full_pipeline(
            raw_content=req.content,
            country_code=req.country_code,
            style_name=req.style_name,
            duration=req.duration,
            video_type=req.video_type,
            extra_data=extra_data,
            mascot_image_url=None,
        )
        script = result.get("script", {})
        director = result.get("director_output", {})
        
        from services.api_key_manager import gemini_key_manager
        
        return {
            "prompt": _format_prompt(script, director),
            "script": script,
            "director_output": director,
            "source": "gemini" if gemini_key_manager.get_api_key() else "mock",
        }
    except Exception as e:
        import traceback
        print(f"[preview-prompt] ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

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
        # 1. Chạy Multi-Agent Pipeline (dùng to_thread để không block event loop của FastAPI)
        pipeline_result = await asyncio.to_thread(
            run_full_pipeline,
            raw_content=raw_content,
            country_code=country_code,
            style_name=style_name,
            duration=duration,
            video_type=video_type,
            extra_data=extra_data,
            mascot_image_url=mascot_image_url,
        )
        
        director_output = pipeline_result.get("director_output", {})

        # Cập nhật Sheet: Đang render Ecomdy và lưu prompt
        prompt_text = _format_prompt(pipeline_result.get("script", {}), director_output)
        update_video_status(record_id, "processing", {"final_prompt": prompt_text})

        # 2. Gửi request tạo video lên Ecomdy
        # Engine Ecomdy là image-to-video (Symphony/TikTok AIGC) -> BẮT BUỘC có image_url.
        image_url = (
            mascot_image_url
            or director_output.get("mascot_image_url")
            or ""
        )
        if not image_url:
            raise Exception(
                "Ecomdy yêu cầu image_url (engine image-to-video) nhưng không có ảnh mascot. "
                "Hãy đính kèm mascot_image khi gọi /create."
            )

        ecomdy_payload = {
            "image_url": image_url,
            "prompt": director_output.get("global_style_prompt", ""),
            "aspect_ratio": director_output.get("recommended_aspect_ratio", "9:16"),
            "kling_prompts": director_output.get("ecomdy_prompts", []),
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
    research_brief: str = Form(default=""),
    mascot_image: Optional[UploadFile] = File(default=None),
):
    try:
        # 1. Upload ảnh Mascot (nếu có) lên Google Drive ngay lập tức
        mascot_image_url = None
        if mascot_image and mascot_image.filename:
            mascot_image_url = await upload_image(mascot_image)

        # 2. Lấy data Google nếu user yêu cầu
        extra_data = ""
        if research_brief:
            extra_data = research_brief
        elif use_google_data and search_keyword:
            import json as _json
            brief = run_research_sync(search_keyword, raw_content, duration)
            extra_data = _json.dumps(brief, ensure_ascii=False)

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
        import traceback
        print(f"[/create] ERROR: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

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
