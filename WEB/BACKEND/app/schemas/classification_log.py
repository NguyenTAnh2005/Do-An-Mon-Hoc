from datetime import datetime
from pydantic import BaseModel, Field

from app.models.models import WasteType, ConfirmationResult


class ClassificationLogItem(BaseModel):
    id: int
    log_id: str
    area_id: int
    area_name: str
    detected_waste_type: WasteType
    confidence: float
    image_url: str | None
    confirmation_result: ConfirmationResult
    created_at: datetime


class ClassificationLogPage(BaseModel):
    items: list[ClassificationLogItem]
    total: int
    page: int
    page_size: int


class ConfirmationUpdate(BaseModel):
    confirmation_result: ConfirmationResult


class BatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=50)


class BatchDeleteResult(BaseModel):
    deleted_count: int
    not_found_ids: list[int]
