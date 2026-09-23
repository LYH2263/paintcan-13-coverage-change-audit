from pydantic import BaseModel

class SettingsUpdate(BaseModel):
    coverage: float | None = None
    coats: int | None = None
