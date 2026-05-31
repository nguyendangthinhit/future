import sys

# Windows consoles default to cp1252, which cannot encode the Vietnamese
# diacritics used throughout our print() logging. Force UTF-8 so startup
# logging (e.g. the scheduler banner) doesn't crash the app on Windows.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load .env BEFORE importing routers/services — several modules read env vars
# (GOOGLE_SHEET_ID, GOOGLE_DRIVE_FOLDER_ID) at import time, so .env must be
# loaded first or they capture None and silently fall back to mock mode.
load_dotenv()

from routers import video, verify, dashboard, trending, caption, research
from services.scheduler import start_scheduler

app = FastAPI(title="Auto Video Platform API", version="1.0.0")

# CORS – cho phép Next.js gọi sang
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router
app.include_router(video.router,     prefix="/api/v1/video",     tags=["Video"])
app.include_router(verify.router,    prefix="/api/v1/verify",    tags=["Verify"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(trending.router,  prefix="/api/v1/trending",  tags=["Trending"])
app.include_router(caption.router,   prefix="/api/v1/caption",   tags=["Caption"])
app.include_router(research.router,  prefix="/api/v1/research",  tags=["Research"])

@app.on_event("startup")
async def startup_event():
    start_scheduler()  # Khởi động cron job khi server lên

@app.get("/health")
def health_check():
    return {"status": "ok"}
