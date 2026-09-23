from pydantic import BaseModel

class SettingsUpdateRequest(BaseModel):
    coverage: float | None = None
    coats: int | None = None
