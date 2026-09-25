from sqlalchemy.orm import Session

from app.models.models import KhuVuc

KHU_VUC_DATA = [
    {
        "mo_ta_vi_tri": "Khu vực 1 - Sân trước",
        "mqtt_topic_phanloai": "truong/khu1/phanloai",
        "mqtt_topic_trangthai_iot": "truong/khu1/trangthai/iot",
        "mqtt_topic_trangthai_ai": "truong/khu1/trangthai/ai",
    },
    {
        "mo_ta_vi_tri": "Khu vực 2 - Sân sau",
        "mqtt_topic_phanloai": "truong/khu2/phanloai",
        "mqtt_topic_trangthai_iot": "truong/khu2/trangthai/iot",
        "mqtt_topic_trangthai_ai": "truong/khu2/trangthai/ai",
    },
]


def seed_khu_vuc(db: Session):
    """Tạo 2 khu vực mẫu."""
    count = 0
    for data in KHU_VUC_DATA:
        existing = (
            db.query(KhuVuc)
            .filter(KhuVuc.mqtt_topic_phanloai == data["mqtt_topic_phanloai"])
            .first()
        )
        if existing:
            continue
        db.add(KhuVuc(**data))
        count += 1
    print(f"✅ seed_khu_vuc sẵn sàng ({count} khu vực mới)!")