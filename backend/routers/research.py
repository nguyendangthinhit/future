from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.research import run_research

router = APIRouter()


class ResearchPreviewRequest(BaseModel):
    topic: str
    focus_points: str = ""
    duration: int = 60


@router.post("/preview")
async def research_preview(req: ResearchPreviewRequest):
    try:
        brief = await run_research(
            topic=req.topic,
            focus_points=req.focus_points,
            duration=req.duration,
        )
        return brief
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
