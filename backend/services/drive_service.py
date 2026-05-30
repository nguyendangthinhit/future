import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

async def upload_image(file) -> str:
    creds_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service_account.json")
    if not os.path.exists(creds_file) or not FOLDER_ID:
        print("Warning: Google Drive not configured. Skipping upload.")
        return "https://mock.url/image.jpg"

    creds = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    contents = await file.read()
    file_metadata = {
        'name': file.filename,
        'parents': [FOLDER_ID]
    }
    media = MediaIoBaseUpload(io.BytesIO(contents), mimetype=file.content_type, resumable=True)
    
    # Upload file
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    
    # Make it public
    drive_service.permissions().create(
        fileId=uploaded_file.get('id'),
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()

    return uploaded_file.get('webViewLink')
