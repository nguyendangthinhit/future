from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.sheets import get_all_videos, create_video_record
from services.agents.pipeline import run_full_pipeline, load_country_profile
import os, json, requests

scheduler = BackgroundScheduler()

def daily_auto_suggest():
    """
    Quy trình tự động hàng ngày:
    1. Crawl trending data (đọc từ file JSON được Data Member cập nhật)
    2. Chạy Agent tổng hợp ý tưởng mới
    3. Ghi vào Sheet với status='verify'
    """
    print("[CRON] Bắt đầu chạy Auto Suggest lúc 2:00 AM...")
    
    # Đọc trending data do Data Member crawl về (đặt sẵn vào file)
    trending_path = os.path.join(os.path.dirname(__file__), "../data/trending_live.json")
    if not os.path.exists(trending_path):
        print("[CRON] Không tìm thấy file trending_live.json. Bỏ qua.")
        return
    
    with open(trending_path, "r", encoding="utf-8") as f:
        trending_data = json.load(f)
    
    for item in trending_data.get("topics", [])[:3]:  # Xử lý tối đa 3 topic/lần
        country_code = item.get("country_code", "VN")
        topic = item.get("topic", "")
        
        pipeline_result = run_full_pipeline(
            raw_content=f"Tạo video về chủ đề đang trending: {topic}",
            country_code=country_code,
            style_name="Energetic Trending",
            duration=60,
        )
        
        create_video_record({
            "video_type": "entertainment",
            "channel": "tiktok",
            "scheduled_date": "",
            "raw_content": topic,
            "style_id": "style_001",
            "style_name": "Energetic Trending",
            "duration": 60,
            "country_hook": country_code,
            "final_prompt": pipeline_result["director_output"].get("global_style_prompt", ""),
            "status": "verify",
            "source": "auto_suggest",
        })
    
    print(f"[CRON] Hoàn thành! Đã tạo {len(trending_data.get('topics', [])[:3])} ý tưởng mới.")

def start_scheduler():
    scheduler.add_job(
        daily_auto_suggest,
        trigger=CronTrigger(hour=2, minute=0, timezone="Asia/Ho_Chi_Minh"),
        id="daily_auto_suggest",
        replace_existing=True,
    )
    scheduler.start()
    print("[SCHEDULER] Cron job đã được đăng ký: chạy lúc 2:00 AM hàng ngày")
