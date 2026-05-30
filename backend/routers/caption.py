from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
import json

router = APIRouter()

class CaptionRequest(BaseModel):
    content: str
    style_name: str
    channel: str

@router.post("/generate")
async def generate_caption(req: CaptionRequest):
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        prompt = f"""
        Bạn là một chuyên gia sáng tạo nội dung mạng xã hội.
        Nhiệm vụ: Viết 3 lựa chọn caption cho một video sắp đăng tải lên {req.channel}.
        
        Thông tin video:
        - Ý tưởng chính: {req.content}
        - Phong cách (Style): {req.style_name}
        
        Yêu cầu:
        - Nếu kênh là TikTok: Caption ngắn gọn (dưới 150 chữ), sử dụng nhiều hashtag trending, có kêu gọi hành động (Call to action).
        - Nếu kênh là Facebook: Caption dài hơn một chút, thân thiện, phân đoạn dễ đọc.
        - Trả về đúng định dạng JSON bên dưới, KHÔNG giải thích gì thêm:
        {{
            "captions": [
                "Lựa chọn 1...",
                "Lựa chọn 2...",
                "Lựa chọn 3..."
            ]
        }}
        """
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        return json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
