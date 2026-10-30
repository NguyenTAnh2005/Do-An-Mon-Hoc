from pydantic import BaseModel

class BinSnapshot(BaseModel):
    area_id: int
    waste_type: str
    current_fill_percent: float

class AreaSnapshot(BaseModel):
    id: int
    location_description: str
    iot_online: bool
    ai_online: bool
    trash_bins: list[BinSnapshot]

class DashboardSnapshot(BaseModel):
    areas: list[AreaSnapshot]