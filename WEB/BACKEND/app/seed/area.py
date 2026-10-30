from sqlalchemy.orm import Session

from app.models.models import Area

AREA_DATA = [
    {
        "location_description": "Area 1 - Front yard",
        "mqtt_topic_classification": "school/area1/classification",
        "mqtt_topic_status_iot": "school/area1/status/iot",
        "mqtt_topic_status_ai": "school/area1/status/ai",
    },
    {
        "location_description": "Area 2 - Back yard",
        "mqtt_topic_classification": "school/area2/classification",
        "mqtt_topic_status_iot": "school/area2/status/iot",
        "mqtt_topic_status_ai": "school/area2/status/ai",
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