from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_trending():
    """Mock endpoint cho trending topics"""
    return {
        "topics": [
            {"id": "t1", "title": "AI Video Generation", "growth": "+150%"},
            {"id": "t2", "title": "Next.js 15 Features", "growth": "+80%"}
        ]
    }
