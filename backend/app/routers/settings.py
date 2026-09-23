from fastapi import APIRouter, HTTPException
from app.schemas.settings import SettingsUpdate
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.post("/settings")
def save_settings(body: SettingsUpdate):
    with PaintService() as s:
        try:
            return s.save_settings(body.model_dump(exclude_none=True))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
@router.get("/settings/history")
def settings_history(limit: int = 100):
    with PaintService() as s: return {"items": s.settings_history(limit)}
