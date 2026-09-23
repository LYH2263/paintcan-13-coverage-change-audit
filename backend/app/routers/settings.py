from fastapi import APIRouter, HTTPException
from app.schemas.settings import SettingsUpdateRequest
from app.services.paint_service import PaintService
router = APIRouter()
@router.get("/settings")
def settings():
    with PaintService() as s: return s.settings()
@router.get("/settings/history")
def settings_history(limit: int = 50):
    with PaintService() as s: return {"items": s.settings_history(limit)}
@router.post("/settings")
def update_settings(body: SettingsUpdateRequest):
    changes = body.model_dump(exclude_none=True)
    try:
        with PaintService() as s:
            return s.update_settings(changes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
