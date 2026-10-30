from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import Area, TrashBin
from app.schemas import dashboard as schemas_dashboard
from app.db_connection import connect_db
from app.core import jwt as jwt_service
from app.core.config import settings

BASE_URL = settings.BASE_API_URL
router = APIRouter(
    prefix=BASE_URL
)


@router.get("/dashboard/snapshot", response_model=schemas_dashboard.DashboardSnapshot)
def get_dashboard_snapshot(
    db: Session = Depends(connect_db),
    current_user=Depends(jwt_service.get_current_account),
):
    # Bước 1: lấy toàn bộ khu vực và toàn bộ thùng từ DB
    all_areas = db.execute(select(Area).order_by(Area.id)).scalars().all()
    all_bins = db.execute(select(TrashBin)).scalars().all()

    # Bước 2: tạo danh sách kết quả, ban đầu rỗng
    area_list = []

    # Bước 3: với mỗi khu vực, tìm các thùng thuộc về khu vực đó
    for area in all_areas:
        trash_bin_list = []

        for trash_bin in all_bins:
            if trash_bin.area_id == area.id:
                trash_bin_item = schemas_dashboard.BinSnapshot(
                    area_id=trash_bin.area_id,
                    waste_type=trash_bin.waste_type.value,
                    current_fill_percent=trash_bin.current_fill_percent,
                )
                trash_bin_list.append(trash_bin_item)

        area_item = schemas_dashboard.AreaSnapshot(
            id=area.id,
            location_description=area.location_description,
            iot_online=area.iot_online,
            ai_online=area.ai_online,
            trash_bins=trash_bin_list,
        )
        area_list.append(area_item)

    # Bước 4: trả kết quả
    return schemas_dashboard.DashboardSnapshot(areas=area_list)