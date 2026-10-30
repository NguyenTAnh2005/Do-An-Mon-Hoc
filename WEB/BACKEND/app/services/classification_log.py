from datetime import date, datetime, time, timedelta, timezone

from fastapi import status
from sqlalchemy.orm import Session

from app.core.app_exception import AppException
from app.crud import classification_log as log_crud
from app.schemas.classification_log import ClassificationLogItem, ClassificationLogPage, BatchDeleteResult

import io
from fastapi import UploadFile
from app.core.cloudinary import upload_image, destroy_image

IMAGE_FOLDER = "Waste_Classification/classification_log"
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

# Nếu bên statistics đã khai báo hằng số này, import dùng lại thay vì khai báo trùng
VN_TZ = timezone(timedelta(hours=7))


def _build_time_range(from_date: date | None, to_date: date | None):
    """
    Đổi khoảng ngày VN thành 2 mốc thời gian có múi giờ.
    Ví dụ from=26/10, to=27/10 -> [26/10 00:00 VN, 28/10 00:00 VN)
    """
    if from_date is not None and to_date is not None and from_date > to_date:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_DATE_RANGE",
            message=f"❌ from_date không được lớn hơn to_date!"
        )

    start_time = None
    end_time = None

    if from_date is not None:
        start_time = datetime.combine(from_date, time.min, tzinfo=VN_TZ)

    if to_date is not None:
        next_day = to_date + timedelta(days=1)
        end_time = datetime.combine(next_day, time.min, tzinfo=VN_TZ)

    return start_time, end_time


def _to_item(log) -> ClassificationLogItem:
    return ClassificationLogItem(
        id=log.id,
        log_id=log.log_id,
        area_id=log.area_id,
        area_name=log.area.location_description,
        detected_waste_type=log.detected_waste_type,
        confidence=log.confidence,
        image_url=log.image_url,
        confirmation_result=log.confirmation_result,
        created_at=log.created_at,
    )


def list_logs(db: Session, page, page_size, area_id, waste_type, confirmation_result, has_image, from_date, to_date):
    offset = (page - 1) * page_size
    start_time, end_time = _build_time_range(from_date, to_date)

    logs = log_crud.get_logs(db, area_id, waste_type, confirmation_result, has_image, start_time, end_time, offset, page_size)
    total = log_crud.count_logs(db, area_id, waste_type, confirmation_result, has_image, start_time, end_time)

    items = []
    for log in logs:
        items.append(_to_item(log=log))

    return ClassificationLogPage(items=items, total=total, page=page, page_size=page_size)


def _get_log_or_404(db: Session, record_id: int):
    log = log_crud.get_log_by_id(db, record_id)
    if log is None:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CLASSIFICATION_LOG_NOT_FOUND",
            message="❌ Không tìm thấy bản ghi phân loại!"
        )
    return log


def get_log_detail(db: Session, record_id: int):
    log = _get_log_or_404(db, record_id)
    return _to_item(log)


def update_confirmation(db: Session, record_id: int, new_result):
    log = _get_log_or_404(db, record_id)
    updated_log = log_crud.update_confirmation(db, log, new_result)
    return _to_item(updated_log)


def upload_log_image(db: Session, record_id: int, file: UploadFile):
    log = _get_log_or_404(db, record_id)

    # Chỉ cho upload khi bản ghi chưa có ảnh
    if log.image_url is not None:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            error_code="IMAGE_ALREADY_EXISTS",
            message="❌ Bản ghi này đã có ảnh!"
        )

    # Kiểm tra loại file
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_IMAGE_TYPE",
            message="❌ Chỉ chấp nhận ảnh jpg, png hoặc webp!"
        )

    # Đọc tối đa MAX + 1 byte: nếu vượt MAX thì biết file quá lớn mà không phải đọc hết
    data = file.file.read(MAX_IMAGE_SIZE + 1)
    if len(data) == 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="EMPTY_IMAGE",
            message="❌ File ảnh rỗng!"
        )
    if len(data) > MAX_IMAGE_SIZE:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="IMAGE_TOO_LARGE",
            message="❌ Ảnh vượt quá 5MB!"
        )

    # Tên ảnh trên Cloudinary = id của bản ghi
    uploaded = upload_image(IMAGE_FOLDER, io.BytesIO(data), public_id=str(log.id))

    updated_log = log_crud.update_image(
        db, log, uploaded["secure_url"], uploaded["public_id"]
    )

    return _to_item(updated_log)


def _destroy_log_image(log):
    # Bản ghi chưa có ảnh thì không có gì để xóa trên Cloudinary
    if log.cloudinary_public_id:
        destroy_image(log.cloudinary_public_id)


def delete_log(db: Session, record_id: int):
    log = _get_log_or_404(db, record_id)
    _destroy_log_image(log)
    log_crud.delete_log(db, log)


def batch_delete_logs(db: Session, ids: list[int]):
    unique_ids = list(set(ids))  # bỏ id trùng nếu FE gửi lặp
    logs = log_crud.get_logs_by_ids(db, unique_ids)

    found_ids = {log.id for log in logs}
    not_found_ids = sorted(i for i in unique_ids if i not in found_ids)

    for log in logs:
        _destroy_log_image(log)
    log_crud.delete_logs(db, logs)

    return BatchDeleteResult(deleted_count=len(logs), not_found_ids=not_found_ids)










