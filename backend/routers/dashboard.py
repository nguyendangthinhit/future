from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats():
    """Mock endpoint cho dashboard"""
    return {
        "total_videos": 120,
        "total_views": 45000,
        "active_campaigns": 5,
        "pending_verifications": 3
    }
