from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import video, verify, dashboard, trending, caption
from services.scheduler import start_scheduler
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Auto Video Platform API", version="1.0.0")

# CORS – cho phép Next.js gọi sang
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
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

@app.on_event("startup")
async def startup_event():
    start_scheduler()  # Khởi động cron job khi server lên

@app.get("/health")
def health_check():
    return {"status": "ok"}
