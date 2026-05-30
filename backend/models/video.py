from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class CreateVideoRequest(BaseModel):
    video_type: str          # "entertainment" | "ads"
    channel: str             # "facebook" | "tiktok"
    scheduled_date: str
    raw_content: str
    style_id: str
    style_name: str
    duration: int            # 15, 30, 60, 90
    country_code: str        # "VN", "US", "TH"...
    use_google_data: bool = False
    search_keyword: Optional[str] = None
    mascot_image_url: Optional[str] = None

class VideoResponse(BaseModel):
    id: str
    status: str
    message: str

class VideoStatusResponse(BaseModel):
    id: str
    status: str
    video_url: Optional[str] = None
    error_log: Optional[str] = None

class ApproveRequest(BaseModel):
    edited_content: Optional[str] = None  # Nếu user muốn sửa trước khi approve
