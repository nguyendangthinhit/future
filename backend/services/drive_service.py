import os
import io
from fastapi import UploadFile
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# URL ảnh mặc định khi không có key hoặc upload lỗi
FALLBACK_IMAGE_URL = "https://fastly.picsum.photos/id/237/720/1280.jpg?hmac=qHgXtu5ruh9UZ-PKeZhdhXjwUyf1i9n5Qc8PqcpaBqg"

def get_drive_service():
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service-account.json")
    service_account_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), service_account_file)
    
    if not os.path.exists(service_account_path):
        return None
    
    creds = Credentials.from_service_account_file(service_account_path, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

async def upload_image(file: UploadFile) -> str:
    """Upload ảnh lên Google Drive và trả về URL trực tiếp."""
    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
    service = get_drive_service()
    
    contents = await file.read()
    
    if not service or not folder_id:
        print("⚠️ Warning: GOOGLE_DRIVE_FOLDER_ID hoặc service-account.json chưa cấu hình. Dùng ảnh mặc định.")
        return FALLBACK_IMAGE_URL
        
    try:
        file_metadata = {
            "name": file.filename or "upload.png",
            "parents": [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(contents), mimetype=file.content_type or "image/png", resumable=True)
        
        # Upload file
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
        
        file_id = uploaded_file.get("id")
        
        # Share công khai để AI Engine có thể tải về
        service.permissions().create(
            fileId=file_id,
            body={"type": "anyone", "role": "reader"}
        ).execute()
        
        # Link tải trực tiếp
        direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"✅ Ảnh đã upload lên Google Drive: {direct_url}")
        return direct_url
        
    except Exception as e:
        print(f"⚠️ Google Drive upload exception: {e}. Dùng ảnh mặc định.")
        return FALLBACK_IMAGE_URL
