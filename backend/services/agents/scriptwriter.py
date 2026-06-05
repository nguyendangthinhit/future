import os, json
from services.llm_manager import llm_manager

def _format_research_section(extra_data: str, duration: int) -> str:
    try:
        data = json.loads(extra_data)
        if "stages" not in data:
            raise ValueError("not structured research")
    except (json.JSONDecodeError, ValueError):
        return f"\n📰 DỮ LIỆU BỔ SUNG TỪ GOOGLE:\n{extra_data}"

    stages = data["stages"]
    num_stages = len(stages)
    seconds_per_stage = round(duration / num_stages) if num_stages else duration

    lines = [f"\n📚 DỮ LIỆU NGHIÊN CỨU CHỦ ĐỀ:"]
    if data.get("summary"):
        lines.append(f"Tóm tắt: {data['summary']}")
    lines.append(f"\nCác giai đoạn cần kể trong video (target ~{num_stages} stage cho ~{duration}s):")
    for s in stages:
        hint = f" [{s['duration_hint']}]" if s.get("duration_hint") else ""
        lines.append(f"  {s['id']}.{hint} {s['title']} — {s.get('detail', '')}")

    facts = data.get("key_facts", [])
    if facts:
        lines.append("\nSự kiện/dữ kiện then chốt:")
        for f in facts:
            lines.append(f"  • {f}")

    lines.append(f"\nYÊU CẦU: phân bổ scenes đều theo các giai đoạn trên, mỗi stage chiếm ~{seconds_per_stage}s.")
    return "\n".join(lines)

def get_model():
    return llm_manager.get_gemini_model()

def run_scriptwriter(
    raw_content: str,
    country_profile: dict,
    case_studies: list,
    duration: int = 60,
    video_type: str = "entertainment",
    extra_data: str = "",
    target_language: str = "Tiếng Việt",
) -> dict:
    """
    Agent 1: Biên Kịch
    Input: Ý tưởng thô + Context quốc gia + Case studies viral
    Output: Kịch bản chi tiết (từng scene, thoại, text overlay)
    """
    
    case_studies_text = json.dumps(case_studies, ensure_ascii=False, indent=2) if case_studies else "Không có"
    extra_section = _format_research_section(extra_data, duration) if extra_data else ""

    prompt = f"""
Bạn là một Biên Kịch sáng tạo chuyên nghiệp cho video mạng xã hội (TikTok/Facebook Reels).

=== NHIỆM VỤ ===
Viết kịch bản video {video_type} khoảng {duration} giây dựa trên:
- Ý tưởng của client
- Đặc điểm thị hiếu khán giả quốc gia {country_profile.get('country_name', '')}
- Phong cách video viral của quốc gia này

=== Ý TƯỞNG CỦA CLIENT ===
{raw_content}
{extra_section}

=== ĐẶC ĐIỂM KHÁN GIẢ {country_profile.get('country_name', '').upper()} ===
- Hook style: {country_profile.get('hook_style', '')}
- Nhịp điệu: {country_profile.get('pacing', '')}
- Visual: {country_profile.get('visual_vibe', '')}
- Âm nhạc: {country_profile.get('preferred_music', '')}
- Mô tả: {country_profile.get('description', '')}

=== CÁC VIDEO VIRAL THAM KHẢO TẠI ĐÂY ===
{case_studies_text}

=== YÊU CẦU ĐẦU RA ===
1. Độ dài: Phù hợp video ngắn {duration}s (tương đương 100-150 từ nếu là VoiceOver).
2. Ngôn ngữ (QUAN TRỌNG): TOÀN BỘ kịch bản, lời thoại (VoiceOver) và text hiển thị trên màn hình PHẢI ĐƯỢC VIẾT BẰNG NGÔN NGỮ: {target_language}.
3. Format output BẮT BUỘC trả về JSON chuẩn, không markdown bọc ngoài:
{{
  "title": "Tiêu đề gợi ý cho video",
  "hook_instruction": "Mô tả cụ thể cảnh mở đầu (0-5 giây) phải làm gì để giữ người xem",
  "scenes": [
    {{
      "scene_id": 1,
      "timestamp": "0s - 5s",
      "action": "Mô tả hành động/cảnh quay",
      "dialogue": "Thoại hoặc VoiceOver (nếu có)",
      "text_overlay": "Chữ hiện trên màn hình (nếu có)",
      "emotion": "Cảm xúc/tone của cảnh này"
    }}
  ],
  "background_music_mood": "Mô tả mood nhạc nền",
  "cta": "Call-to-action cuối video"
}}
"""
    
    response = llm_manager.generate_content_with_retry(prompt)
    if not response:
        raise Exception("Không nhận được phản hồi từ LLM (Agent Biên Kịch). Vui lòng thử lại.")

    text = response.text.strip()
    
    # Bóc tách JSON từ response
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("Lỗi parse JSON từ Gemini")
        return {"error": "Lỗi parse JSON"}
