import os
import json
import uuid
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), service_account_file)
    
    if not os.path.exists(service_account_path):
        return None
    
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client

def get_sheet():
    client = get_client()
    if not client:
        return None
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        return None
    
    try:
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        
        # Init headers if empty
        if not worksheet.get_all_values():
            headers = [
                "id", "created_at", "scheduled_date", "channel", "video_type", 
                "duration", "raw_content", "style_id", "style_name", "extra_data", 
                "country_hook", "final_prompt", "image_urls", "status", "video_url", 
                "post_id", "source", "error_log", "approved_by", "approved_at"
            ]
            worksheet.append_row(headers)
        
        return worksheet
    except Exception as e:
        print(f"Lỗi kết nối Google Sheet: {e}")
        return None

def create_video_record(data: dict) -> str:
    record_id = f"vid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    worksheet = get_sheet()
    
    if not worksheet:
        print("Mock: create_video_record", record_id)
        return record_id

    row = [
        record_id,
        datetime.now().isoformat(),
        data.get("scheduled_date", ""),
        data.get("channel", ""),
        data.get("video_type", ""),
        str(data.get("duration", 60)),
        data.get("raw_content", ""),
        data.get("style_id", ""),
        data.get("style_name", ""),
        data.get("extra_data", ""),
        data.get("country_hook", ""),
        data.get("final_prompt", ""),
        json.dumps(data.get("image_urls", [])),
        data.get("status", "pending"),
        "", "", "", "", "", ""
    ]
    worksheet.append_row(row)
    return record_id

def update_video_status(record_id: str, status: str, extra_fields: dict = {}):
    worksheet = get_sheet()
    if not worksheet:
        print(f"Mock: update_video_status {record_id} -> {status}")
        return True

    try:
        cell = worksheet.find(record_id, in_column=1)
        if not cell:
            print(f"Không tìm thấy record_id: {record_id}")
            return False
            
        row_idx = cell.row
        headers = worksheet.row_values(1)
        
        updates = []
        try:
            col_idx = headers.index("status") + 1
            updates.append({'range': gspread.utils.rowcol_to_a1(row_idx, col_idx), 'values': [[status]]})
        except ValueError:
            pass
            
        for key, val in extra_fields.items():
            if key in ["video_url", "post_id", "error_log", "approved_by", "approved_at", "final_prompt"]:
                try:
                    col_idx = headers.index(key) + 1
                    updates.append({'range': gspread.utils.rowcol_to_a1(row_idx, col_idx), 'values': [[str(val)]]})
                except ValueError:
                    continue
                    
        if updates:
            worksheet.batch_update(updates)
            
        return True
    except Exception as e:
        print(f"Lỗi update_video_status: {e}")
        return False

def _parse_row(headers, row):
    d = {}
    for i, h in enumerate(headers):
        val = row[i] if i < len(row) else ""
        if h == "image_urls" and val:
            try:
                val = json.loads(val)
            except:
                val = []
        d[h] = val
    return d

def get_verify_list():
    worksheet = get_sheet()
    if not worksheet:
        return []
    try:
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return []
        headers = data[0]
        records = []
        for row in data[1:]:
            d = _parse_row(headers, row)
            if d.get("status") == "verify":
                records.append(d)
        
        records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return records
    except Exception as e:
        print(f"Lỗi get_verify_list: {e}")
        return []

def get_all_videos():
    worksheet = get_sheet()
    if not worksheet:
        return []
    try:
        data = worksheet.get_all_values()
        if len(data) <= 1:
            return []
        headers = data[0]
        records = []
        for row in data[1:]:
            d = _parse_row(headers, row)
            records.append(d)
            
        records.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return records
    except Exception as e:
        print(f"Lỗi get_all_videos: {e}")
        return []
