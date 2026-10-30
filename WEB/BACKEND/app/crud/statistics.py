from sqlalchemy import func, select, cast, Date
from sqlalchemy.orm import Session
from datetime import date


from app.models.models import ClassificationLog, Area, ConfirmationResult


def count_total_logs(db: Session) -> int:
    """Đếm tổng số bản ghi phân loại."""
    query = select(func.count(ClassificationLog.id))
    total = db.execute(query).scalar_one()
    return total


def count_logs_by_waste_type(db: Session):
    """Đếm số bản ghi theo từng loại rác.
    Trả về list các dòng (waste_type, count)."""
    query = (
        select(
            ClassificationLog.detected_waste_type,
            func.count(ClassificationLog.id),
        )
        .group_by(ClassificationLog.detected_waste_type)
    )
    rows = db.execute(query).all()
    return rows


def count_logs_by_confirmation(db: Session):
    """Đếm số bản ghi theo trạng thái xác nhận.
    Trả về list các dòng (confirmation_result, count)."""
    query = (
        select(
            ClassificationLog.confirmation_result,
            func.count(ClassificationLog.id),
        )
        .group_by(ClassificationLog.confirmation_result)
    )
    rows = db.execute(query).all()
    return rows


def get_average_confidence(db: Session) -> float | None:
    """Confidence trung bình. Trả về None nếu bảng chưa có bản ghi nào."""
    query = select(func.avg(ClassificationLog.confidence))
    average = db.execute(query).scalar_one()
    return average


def get_all_areas(db: Session):
    """Lấy toàn bộ khu vực, sắp xếp theo id."""
    query = select(Area).order_by(Area.id)
    areas = db.execute(query).scalars().all()
    return areas


def count_logs_by_area_and_waste_type(db: Session):
    """Đếm số bản ghi theo (khu vực, loại rác).
    Trả về list các dòng (area_id, waste_type, count)."""
    query = (
        select(
            ClassificationLog.area_id,
            ClassificationLog.detected_waste_type,
            func.count(ClassificationLog.id),
        )
        .group_by(
            ClassificationLog.area_id,
            ClassificationLog.detected_waste_type,
        )
    )
    rows = db.execute(query).all()
    return rows


def count_logs_by_day(db: Session, start_date: date):
    """Đếm số bản ghi theo từng ngày (giờ VN), từ start_date trở đi.
    Trả về list các dòng (ngày, count). Ngày không có bản ghi sẽ không xuất hiện."""
    vn_time = func.timezone("Asia/Ho_Chi_Minh", ClassificationLog.created_at)
    day = cast(vn_time, Date).label("day")

    query = (
        select(day, func.count(ClassificationLog.id))
        .where(cast(vn_time, Date) >= start_date)
        .group_by(day)
        .order_by(day)
    )
    rows = db.execute(query).all()
    return rows

def count_confirmations_by_day(db: Session, start_date: date):
    """Đếm số bản ghi theo (ngày VN, trạng thái xác nhận), bỏ qua UNCONFIRMED.
    Trả về list các dòng (ngày, confirmation_result, count)."""
    vn_time = func.timezone("Asia/Ho_Chi_Minh", ClassificationLog.created_at)
    day = cast(vn_time, Date).label("day")

    query = (
        select(day, ClassificationLog.confirmation_result, func.count(ClassificationLog.id))
        .where(cast(vn_time, Date) >= start_date)
        .where(ClassificationLog.confirmation_result != ConfirmationResult.UNCONFIRMED)
        .group_by(day, ClassificationLog.confirmation_result)
    )
    rows = db.execute(query).all()
    return rows


def get_average_confidence_by_day(db: Session, start_date: date):
    """Confidence trung bình theo ngày VN (tính trên mọi bản ghi).
    Trả về list các dòng (ngày, avg_confidence)."""
    vn_time = func.timezone("Asia/Ho_Chi_Minh", ClassificationLog.created_at)
    day = cast(vn_time, Date).label("day")

    query = (
        select(day, func.avg(ClassificationLog.confidence))
        .where(cast(vn_time, Date) >= start_date)
        .group_by(day)
    )
    rows = db.execute(query).all()
    return rows