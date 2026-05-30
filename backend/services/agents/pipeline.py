import json, os
from .scriptwriter import run_scriptwriter
from .director import run_director

def load_country_profile(country_code: str) -> dict:
    """Đọc thị hiếu của quốc gia từ file JSON tĩnh"""
    profile_path = os.path.join(os.path.dirname(__file__), "../../data/country_profiles.json")
    if not os.path.exists(profile_path):
        return {"country_name": country_code}
    with open(profile_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    return profiles.get(country_code, profiles.get("VN", {}))

def load_case_studies(country_code: str) -> list:
    """Load viral case studies phù hợp với quốc gia"""
    path = os.path.join(os.path.dirname(__file__), "../../data/viral_case_studies.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        all_cases = json.load(f)
    return [c for c in all_cases if c.get("country") == country_code][:2]

def run_full_pipeline(
    raw_content: str,
    country_code: str,
    style_name: str,
    duration: int = 60,
    video_type: str = "entertainment",
    extra_data: str = "",
    mascot_image_url: str = None,
) -> dict:
    """
    Orchestrator: Chạy toàn bộ Multi-Agent Pipeline
    Trả về dict chứa kịch bản + camera prompts + toàn bộ context để gửi sang n8n
    """
    
    # Bước 1: Load dữ liệu ngữ cảnh
    country_profile = load_country_profile(country_code)
    case_studies = load_case_studies(country_code)
    
    # Bước 2: Gọi Agent Biên Kịch
    print(f"[Agent 1 - Biên Kịch] Đang viết kịch bản cho: {raw_content[:50]}...")
    script = run_scriptwriter(
        raw_content=raw_content,
        country_profile=country_profile,
        case_studies=case_studies,
        extra_data=extra_data,
        video_type=video_type,
        duration=duration,
    )
    
    # Bước 3: Gọi Agent Đạo Diễn
    print(f"[Agent 2 - Đạo Diễn] Đang tạo Camera Prompts...")
    director_output = run_director(
        script=script,
        style_name=style_name,
        mascot_image_url=mascot_image_url,
        duration=duration,
    )
    
    return {
        "script": script,
        "director_output": director_output,
        "country_profile": country_profile,
        "final_prompt_summary": director_output.get("global_style_prompt", ""),
    }
