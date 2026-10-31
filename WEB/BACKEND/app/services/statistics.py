from sqlalchemy.orm import Session

from app.crud import statistics as statistics_crud
from app.models.models import ConfirmationResult, WasteType
from app.schemas.statistics import (
    AreaStatistics,
    StatisticsByArea,
    StatisticsOverview,
    WasteTypeCount,
    StatisticsTimeline, 
    DailyCount,
    StatisticsAccuracyTimeline, 
    DailyAccuracy
)
from datetime import date, datetime, timedelta, timezone


def get_overview(db: Session) -> StatisticsOverview:
    # 1. Lấy dữ liệu thô từ crud
    total_logs = statistics_crud.count_total_logs(db)
    waste_type_rows = statistics_crud.count_logs_by_waste_type(db)
    confirmation_rows = statistics_crud.count_logs_by_confirmation(db)
    average_confidence = statistics_crud.get_average_confidence(db)

    # 2. Đổi các dòng (waste_type, count) thành dict để tra cứu theo loại rác
    waste_type_counts = {}
    for waste_type, count in waste_type_rows:
        waste_type_counts[waste_type] = count

    # 3. Duyệt đủ 3 loại rác, loại nào không có trong dict thì count = 0
    by_waste_type = []
    for waste_type in WasteType:
        count = waste_type_counts.get(waste_type, 0)
        by_waste_type.append(WasteTypeCount(waste_type=waste_type, count=count))

    # 4. Làm tương tự cho trạng thái xác nhận
    confirmation_counts = {}
    for confirmation_result, count in confirmation_rows:
        confirmation_counts[confirmation_result] = count

    confirmed_correct = confirmation_counts.get(ConfirmationResult.CORRECT, 0)
    confirmed_incorrect = confirmation_counts.get(ConfirmationResult.INCORRECT, 0)
    unconfirmed = confirmation_counts.get(ConfirmationResult.UNCONFIRMED, 0)

    # 5. Tỉ lệ chính xác, chỉ tính trên các bản ghi đã xác nhận
    confirmed_total = confirmed_correct + confirmed_incorrect
    if confirmed_total == 0:
        accuracy_percent = None
    else:
        accuracy_percent = confirmed_correct / confirmed_total * 100

    # 6. Làm tròn cho gọn khi hiển thị
    if accuracy_percent is not None:
        accuracy_percent = round(accuracy_percent, 1)
    if average_confidence is not None:
        average_confidence = round(average_confidence, 3)

    # 7. Ghép thành schema trả về
    return StatisticsOverview(
        total_logs=total_logs,
        by_waste_type=by_waste_type,
        confirmed_correct=confirmed_correct,
        confirmed_incorrect=confirmed_incorrect,
        unconfirmed=unconfirmed,
        accuracy_percent=accuracy_percent,
        average_confidence=average_confidence,
    )


def get_by_area(db: Session) -> StatisticsByArea:
    # 1. Lấy dữ liệu thô từ crud
    areas = statistics_crud.get_all_areas(db)
    rows = statistics_crud.count_logs_by_area_and_waste_type(db)

    # 2. Đổi các dòng (area_id, waste_type, count) thành dict hai tầng:
    #    counts[area_id][waste_type] = count
    counts = {}
    for area_id, waste_type, count in rows:
        if area_id not in counts:
            counts[area_id] = {}
        counts[area_id][waste_type] = count

    # 3. Duyệt từng khu vực, bù số 0 cho loại rác chưa có bản ghi
    items = []
    for area in areas:
        area_counts = counts.get(area.id, {})

        by_waste_type = []
        total_logs = 0
        for waste_type in WasteType:
            count = area_counts.get(waste_type, 0)
            by_waste_type.append(WasteTypeCount(waste_type=waste_type, count=count))
            total_logs += count

        items.append(
            AreaStatistics(
                area_id=area.id,
                location_description=area.location_description,
                total_logs=total_logs,
                by_waste_type=by_waste_type,
            )
        )

    # 4. Ghép thành schema trả về
    return StatisticsByArea(items=items)


VN_TZ = timezone(timedelta(hours=7))


def _get_start_date(days: int) -> date:
    """Ngày bắt đầu của khoảng N ngày gần nhất theo giờ VN (tính cả hôm nay)."""
    today = datetime.now(VN_TZ).date()
    start_date = today - timedelta(days=days - 1)
    return start_date

def get_timeline(db: Session, days: int) -> StatisticsTimeline:
    # 1. Tính khoảng ngày theo giờ VN: days ngày gần nhất, tính cả hôm nay
    start_date = _get_start_date(days=days)

    # 2. Lấy dữ liệu thô từ crud rồi đổi thành dict: {ngày: count}
    rows = statistics_crud.count_logs_by_day(db, start_date)
    day_counts = {}
    for day, count in rows:
        day_counts[day] = count

    # 3. Duyệt từng ngày trong khoảng, ngày nào không có bản ghi thì count = 0
    items = []
    for offset in range(days):
        current_day = start_date + timedelta(days=offset)
        count = day_counts.get(current_day, 0)
        items.append(DailyCount(date_vn=current_day, count=count))

    return StatisticsTimeline(days=days, items=items)


def get_accuracy_timeline(db: Session, days: int) -> StatisticsAccuracyTimeline:
    # 1. Khoảng ngày giống get_timeline
    start_date = _get_start_date(days=days)

    # 2. Lấy dữ liệu thô từ crud
    confirmation_rows = statistics_crud.count_confirmations_by_day(db, start_date)
    confidence_rows = statistics_crud.get_average_confidence_by_day(db, start_date)

    # 3. Dict hai tầng: confirmation_counts[ngày][trạng thái] = count
    confirmation_counts = {}
    for day, confirmation_result, count in confirmation_rows:
        if day not in confirmation_counts:
            confirmation_counts[day] = {}
        confirmation_counts[day][confirmation_result] = count

    # 4. Dict confidence: confidence_by_day[ngày] = avg
    confidence_by_day = {}
    for day, average_confidence in confidence_rows:
        confidence_by_day[day] = average_confidence

    # 5. Duyệt từng ngày, ngày nào thiếu dữ liệu thì để None / 0
    items = []
    for offset in range(days):
        current_day = start_date + timedelta(days=offset)

        day_counts = confirmation_counts.get(current_day, {})
        correct = day_counts.get(ConfirmationResult.CORRECT, 0)
        incorrect = day_counts.get(ConfirmationResult.INCORRECT, 0)

        confirmed_total = correct + incorrect
        if confirmed_total == 0:
            accuracy_percent = None
        else:
            accuracy_percent = round(correct / confirmed_total * 100, 1)

        average_confidence = confidence_by_day.get(current_day)
        if average_confidence is not None:
            average_confidence = round(average_confidence, 3)

        items.append(
            DailyAccuracy(
                date_vn=current_day,
                confirmed_correct=correct,
                confirmed_incorrect=incorrect,
                accuracy_percent=accuracy_percent,
                average_confidence=average_confidence,
            )
        )

    return StatisticsAccuracyTimeline(days=days, items=items)