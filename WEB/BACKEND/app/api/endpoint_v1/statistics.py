from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db_connection import connect_db
from app.core import jwt as jwt_service
from app.models.models import Account
from app.schemas.statistics import StatisticsOverview, StatisticsByArea, StatisticsTimeline, StatisticsAccuracyTimeline
from app.services import statistics as statistics_service
from app.core.config import settings as AppSettings

BASE_URL= AppSettings.BASE_API_URL

router = APIRouter(prefix=BASE_URL+"/statistics", tags=["Statistics"])


@router.get("/overview", response_model=StatisticsOverview)
def get_statistics_overview(
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account),
):
    """Số liệu tổng quan cho trang Thống kê."""
    overview = statistics_service.get_overview(db)
    return overview

@router.get("/by-area", response_model=StatisticsByArea)
def get_statistics_by_area(
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account),
):
    """Thống kê số lượt phân loại theo từng khu vực."""
    result = statistics_service.get_by_area(db)
    return result

@router.get("/timeline", response_model=StatisticsTimeline)
def get_statistics_timeline(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account),
):
    """Số lượt phân loại theo từng ngày trong N ngày gần nhất (giờ VN)."""
    result = statistics_service.get_timeline(db, days)
    return result

@router.get("/accuracy-timeline", response_model=StatisticsAccuracyTimeline)
def get_statistics_accuracy_timeline(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(connect_db),
    current_account: Account = Depends(jwt_service.get_current_account),
):
    """Độ chính xác và độ tin cậy trung bình của model theo từng ngày (giờ VN)."""
    result = statistics_service.get_accuracy_timeline(db, days)
    return result