from pydantic import BaseModel
from datetime import date
from app.models.models import WasteType


class WasteTypeCount(BaseModel):
    """Số lượt phân loại của một loại rác."""
    waste_type: WasteType
    count: int


class StatisticsOverview(BaseModel):
    """Số liệu tổng quan cho trang Thống kê."""
    total_logs: int
    by_waste_type: list[WasteTypeCount]

    confirmed_correct: int
    confirmed_incorrect: int
    unconfirmed: int

    # Tỉ lệ chính xác = correct / (correct + incorrect) * 100
    # None nếu chưa có bản ghi nào được xác nhận (tránh chia cho 0)
    accuracy_percent: float | None

    # None nếu bảng chưa có bản ghi nào
    average_confidence: float | None


class AreaStatistics(BaseModel):
    """Thống kê của một khu vực."""
    area_id: int
    location_description: str
    total_logs: int
    by_waste_type: list[WasteTypeCount]


class StatisticsByArea(BaseModel):
    """Thống kê của tất cả khu vực."""
    items: list[AreaStatistics]

class DailyCount(BaseModel):
    """Số lượt phân loại trong một ngày (theo giờ Việt Nam)."""
    date_vn: date
    count: int


class StatisticsTimeline(BaseModel):
    days: int
    items: list[DailyCount]


class DailyAccuracy(BaseModel):
    """Độ chính xác và độ tin cậy của model trong một ngày (giờ VN)."""
    date_vn: date
    confirmed_correct: int
    confirmed_incorrect: int
    # None nếu ngày đó chưa có bản ghi nào được xác nhận
    accuracy_percent: float | None
    # None nếu ngày đó không có bản ghi nào
    average_confidence: float | None


class StatisticsAccuracyTimeline(BaseModel):
    days: int
    items: list[DailyAccuracy]

