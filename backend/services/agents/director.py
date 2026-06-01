import google.generativeai as genai
import os, json

from services.api_key_manager import gemini_key_manager

def get_model():
    return gemini_key_manager.get_model()

def run_director(
    script: dict,
    style_name: str,
    mascot_image_url: str = None,
    duration: int = 60,
) -> dict:
    """
    Agent 2: Đạo Diễn
    Input: Kịch bản từ Biên Kịch + Style + Mascot Image
    Output: Camera Prompts chuyên dụng cho Ecomdy API
    """
    
    mascot_section = ""
    if mascot_image_url:
        mascot_section = f"""
=== NHÂN VẬT CỐ ĐỊNH (AUTOCAMEO) ===
Video này phải sử dụng nhân vật/sản phẩm từ ảnh sau làm nhân vật chính xuyên suốt:
Image URL: {mascot_image_url}
Yêu cầu: Giữ nguyên khuôn mặt/hình dạng nhân vật trong tất cả các cảnh.
"""
    
    scenes_text = json.dumps(script.get("scenes", []), ensure_ascii=False, indent=2)

    prompt = f"""
Bạn là Đạo Diễn hình ảnh chuyên nghiệp, chuyên chuyển đổi kịch bản sang Camera Prompts cho AI Video Generator (Ecomdy API).

=== KỊCH BẢN CẦN DỊCH ===
Tiêu đề: {script.get('title', '')}
Hook: {script.get('hook_instruction', '')}
Mood nhạc: {script.get('background_music_mood', '')}

Chi tiết từng cảnh:
{scenes_text}
{mascot_section}
=== PHONG CÁCH VIDEO (STYLE) ===
{style_name}

=== NHIỆM VỤ ===
Dịch từng cảnh trong kịch bản thành Camera Prompt tiếng Anh chuyên dụng cho Ecomdy API.
Mỗi Prompt phải bao gồm: loại cảnh quay (shot type) + chuyển động camera + ánh sáng + màu sắc + tốc độ.

=== OUTPUT JSON ===
{{
  "ecomdy_prompts": [
    {{
      "scene_id": 1,
      "duration_seconds": 5,
      "prompt": "Camera prompt tiếng Anh đầy đủ cho Ecomdy API",
      "negative_prompt": "Những gì không muốn xuất hiện trong cảnh này"
    }}
  ],
  "global_style_prompt": "Prompt phong cách chung áp dụng cho toàn bộ video",
  "recommended_aspect_ratio": "9:16",
  "mascot_image_url": "{mascot_image_url or ''}"
}}
"""
    
    response = gemini_key_manager.generate_content_with_retry(prompt)
    if not response:
        # Mock response if no API key or generation failed completely
        return {
            "ecomdy_prompts": [
                {
                    "scene_id": 1,
                    "duration_seconds": 5,
                    "prompt": "Mock camera prompt",
                    "negative_prompt": "ugly, blurry"
                }
            ],
            "global_style_prompt": "Mock global style",
            "recommended_aspect_ratio": "9:16",
            "mascot_image_url": mascot_image_url or ""
        }

    text = response.text.strip()
    
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("Lỗi parse JSON từ Gemini")
        return {"error": "Lỗi parse JSON"}
