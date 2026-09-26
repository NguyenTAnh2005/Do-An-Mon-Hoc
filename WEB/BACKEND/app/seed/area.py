from sqlalchemy.orm import Session

from app.models.models import Area

AREA_DATA = [
    {
        "location_description": "Area 1 - Front yard",
        "mqtt_topic_classification": "truong/khu1/phanloai",
        "mqtt_topic_status_iot": "truong/khu1/trangthai/iot",
        "mqtt_topic_status_ai": "truong/khu1/trangthai/ai",
    },
    {
        "location_description": "Area 2 - Back yard",
        "mqtt_topic_classification": "truong/khu2/phanloai",
        "mqtt_topic_status_iot": "truong/khu2/trangthai/iot",
        "mqtt_topic_status_ai": "truong/khu2/trangthai/ai",
    },
]


def seed_area(db: Session):
    """Create 2 sample areas."""
    count = 0
    for data in AREA_DATA:
        existing = (
            db.query(Area)
            .filter(Area.mqtt_topic_classification == data["mqtt_topic_classification"])
            .first()
        )
        if existing:
            continue
        db.add(Area(**data))
        count += 1
    print(f"✅ seed_area ready ({count} new areas)!")
