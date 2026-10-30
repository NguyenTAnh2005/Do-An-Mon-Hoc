from datetime import date

from fastapi import APIRouter, Depends, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.models.models import WasteType, ConfirmationResult
from app.schemas.classification_log import ClassificationLogPage, ClassificationLogItem, ConfirmationUpdate, BatchDeleteRequest, BatchDeleteResult
from app.services import classification_log as log_service
from app.db_connection import connect_db
from app.core import jwt as jwt_service
from app.core.app_response import AppResponse
from app.core.config import settings as AppSettings

BASE_URL = AppSettings.BASE_API_URL


router = APIRouter(prefix=BASE_URL + "/classification-logs", tags=["Classification Logs"])


@router.get("/", response_model=AppResponse[ClassificationLogPage])
def get_classification_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    area_id: int | None = None,
    detected_waste_type: WasteType | None = None,
    confirmation_result: ConfirmationResult | None = None,
    has_image: bool | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API lấy danh sách lịch sử phân loại (có phân trang + bộ lọc)
        + from_date, to_date: định dạng YYYY-MM-DD, tính theo giờ VN, bao gồm cả hai đầu
        + Trả về AppResponse chứa ClassificationLogPage
    """
    result = log_service.list_logs(
        db, page, page_size, area_id, detected_waste_type,
        confirmation_result, has_image, from_date, to_date
    )

    return AppResponse(
        message="🎉 Lấy lịch sử phân loại thành công.",
        data=result
    )


@router.get("/{record_id}", response_model=AppResponse[ClassificationLogItem])
def get_classification_log_detail(
    record_id: int,
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API lấy chi tiết 1 bản ghi phân loại theo id
        + Không tồn tại: trả lỗi 404
    """
    result = log_service.get_log_detail(db, record_id)

    return AppResponse(
        message="🎉 Lấy chi tiết bản ghi phân loại thành công.",
        data=result
    )


@router.patch("/{record_id}/confirmation", response_model=AppResponse[ClassificationLogItem])
def update_classification_confirmation(
    record_id: int,
    body: ConfirmationUpdate,
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API đổi kết quả xác nhận của 1 bản ghi phân loại
        + Đổi tự do ở mọi trạng thái (unconfirmed / correct / incorrect)
        + Trả về bản ghi đã cập nhật (cùng dạng với GET by id)
    """
    result = log_service.update_confirmation(db, record_id, body.confirmation_result)

    return AppResponse(
        message="🎉 Cập nhật kết quả xác nhận thành công.",
        data=result
    )


@router.patch("/{record_id}/image", response_model=AppResponse[ClassificationLogItem])
def upload_classification_image(
    record_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API upload ảnh thủ công cho 1 bản ghi (chỉ khi bản ghi chưa có ảnh)
        + Gửi dạng multipart/form-data, field tên `file`
        + Chấp nhận jpg/png/webp, tối đa 5MB
        + Đã có ảnh: trả lỗi 409
    """
    result = log_service.upload_log_image(db, record_id, file)

    return AppResponse(
        message="🎉 Upload ảnh thành công.",
        data=result
    )


@router.delete("/{record_id}", response_model=AppResponse[None])
def delete_classification_log(
    record_id: int,
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API xóa 1 bản ghi phân loại (kèm xóa ảnh trên Cloudinary nếu có)
        + Không tồn tại: trả lỗi 404
    """
    log_service.delete_log(db, record_id)

    return AppResponse(message="🎉 Xóa bản ghi phân loại thành công.")


@router.post("/batch-delete", response_model=AppResponse[BatchDeleteResult])
def batch_delete_classification_logs(
    body: BatchDeleteRequest,
    db: Session = Depends(connect_db),
    current_account=Depends(jwt_service.get_current_account),
):
    """
    ## API xóa nhiều bản ghi phân loại cùng lúc (tối đa 50 id)
        + Id không tồn tại không gây lỗi, được liệt kê trong not_found_ids
    """
    result = log_service.batch_delete_logs(db, body.ids)

    return AppResponse(
        message=f"🎉 Đã xóa {result.deleted_count} bản ghi phân loại.",
        data=result
    )






