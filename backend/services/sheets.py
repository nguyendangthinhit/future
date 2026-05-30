import gspread
from google.oauth2.service_account import Credentials
import os, json
from datetime import datetime
import uuid

SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def get_sheet_client():
    creds_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
    if not os.path.exists(creds_file):
        print(f"Warning: {creds_file} not found. Google Sheets integration will fail.")
        return None
    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    client = gspread.authorize(creds)
    if not SHEET_ID:
        print("Warning: GOOGLE_SHEET_ID is not set in .env")
        return None
    return client.open_by_key(SHEET_ID)

def create_video_record(data: dict) -> str:
    """Ghi một record mới vào Sheet 'video_queue', trả về ID"""
    spreadsheet = get_sheet_client()
    if not spreadsheet:
        return f"mock_id_{uuid.uuid4().hex[:6]}"
    
    sheet = spreadsheet.worksheet("video_queue")
    
    record_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    row = [
        record_id,                          # A: id
        datetime.now().isoformat(),          # B: created_at
        data.get("scheduled_date", ""),      # C: scheduled_date
        data.get("channel", ""),             # D: channel
        data.get("video_type", ""),          # E: video_type
        data.get("duration", 60),            # F: duration
        data.get("raw_content", ""),         # G: raw_content
        data.get("style_id", ""),            # H: style_id
        data.get("style_name", ""),          # I: style_name
        data.get("extra_data", ""),          # J: extra_data
        data.get("country_hook", ""),        # K: country_hook
        data.get("final_prompt", ""),        # L: final_prompt
        json.dumps(data.get("image_urls", [])), # M: image_urls
        data.get("status", "pending"),       # N: status
        "", "", "",                          # O, P, Q: video_url, post_id, source
        "", "", "",                          # R, S, T: error_log, approved_by, approved_at
    ]
    sheet.append_row(row)
    return record_id

def update_video_status(record_id: str, status: str, extra_fields: dict = {}):
    """Cập nhật trạng thái một record"""
    spreadsheet = get_sheet_client()
    if not spreadsheet:
        return False
        
    sheet = spreadsheet.worksheet("video_queue")
    cell = sheet.find(record_id)
    if not cell:
        return False
    row = cell.row
    # Cập nhật cột N (status = index 14)
    sheet.update_cell(row, 14, status)
    for col_letter, value in extra_fields.items():
        col_map = {"video_url": 15, "post_id": 16, "error_log": 18}
        if col_letter in col_map:
            sheet.update_cell(row, col_map[col_letter], value)
    return True

def get_verify_list():
    """Lấy danh sách ý tưởng cần duyệt"""
    spreadsheet = get_sheet_client()
    if not spreadsheet:
        return []
    sheet = spreadsheet.worksheet("video_queue")
    records = sheet.get_all_records()
    return [r for r in records if r.get("status") == "verify"]

def get_all_videos():
    spreadsheet = get_sheet_client()
    if not spreadsheet:
        return []
    sheet = spreadsheet.worksheet("video_queue")
    return sheet.get_all_records()
