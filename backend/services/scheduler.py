import asyncio
import json
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from models.brief import Brief
from services.orchestrator import run_full_factory
from services.sheets import create_video_record


scheduler = BackgroundScheduler()


def daily_auto_suggest():
    """Create verify-ready factory suggestions from local trending data."""
    print("[CRON] Starting daily auto suggest at 2:00 AM...")

    trending_path = os.path.join(os.path.dirname(__file__), "../data/trending_live.json")
    if not os.path.exists(trending_path):
        print("[CRON] trending_live.json not found. Skipping.")
        return

    with open(trending_path, "r", encoding="utf-8") as file:
        trending_data = json.load(file)

    created_count = 0
    for item in trending_data.get("topics", [])[:3]:
        country_code = item.get("country_code", "VN")
        topic = item.get("topic", "").strip()
        if not topic:
            continue

        brief = Brief(
            theme=f"Trending topic: {topic}",
            brand={
                "name": "MarkX",
                "toneOfVoice": "fast, social-first, trend-aware",
                "claimsAllowed": [],
                "claimsForbidden": [],
            },
            audience={"segment": country_code, "age": "18-34", "locale": "vi-VN"},
            platform="tiktok",
            constraints={
                "lengthSec": 30,
                "aspect": ["9:16"],
                "mustInclude": [topic],
                "mustAvoid": [],
            },
            variantsTarget=2,
        )

        factory_result = asyncio.run(
            run_full_factory(brief, include_vo=False, include_video=False)
        )
        plan = factory_result.get("plan", {})

        create_video_record({
            "video_type": "entertainment",
            "channel": "tiktok",
            "scheduled_date": "",
            "raw_content": topic,
            "style_id": "factory",
            "style_name": "Content Factory",
            "duration": 30,
            "country_hook": country_code,
            "final_prompt": json.dumps(plan, ensure_ascii=False),
            "status": "verify",
            "source": "factory_auto_suggest",
        })
        created_count += 1

    print(f"[CRON] Done. Created {created_count} factory suggestions.")


def start_scheduler():
    scheduler.add_job(
        daily_auto_suggest,
        trigger=CronTrigger(hour=2, minute=0, timezone="Asia/Ho_Chi_Minh"),
        id="daily_auto_suggest",
        replace_existing=True,
    )
    scheduler.start()
    print("[SCHEDULER] Registered daily auto suggest at 2:00 AM.")
