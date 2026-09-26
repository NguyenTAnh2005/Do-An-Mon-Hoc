from sqlalchemy.orm import Session

from app.models.models import TrashBin, Area, WasteType

DEFAULT_HEIGHT_CM = 50.0

WASTE_TYPE_SLUG = {
    WasteType.RECYCLABLE: "taiche",
    WasteType.ORGANIC: "huuco",
    WasteType.INORGANIC: "voco",
}


def seed_trash_bin(db: Session):
    """Each area gets 3 bins: recyclable / organic / inorganic.

    Requires area to already have an id (db.flush() after seed_area before calling this).
    """
    area_list = db.query(Area).order_by(Area.id).all()
    if not area_list:
        print("⚠️ No areas found, run seed_area (and flush) first.")
        return

    count = 0
    for area in area_list:
        area_n = area.mqtt_topic_classification.split("/")[1]  # "khu1", "khu2", ...
        for waste_type, slug in WASTE_TYPE_SLUG.items():
            topic = f"truong/{area_n}/mucday/{slug}"
            existing = db.query(TrashBin).filter(TrashBin.mqtt_topic_fill_level == topic).first()
            if existing:
                continue
            db.add(
                TrashBin(
                    area_id=area.id,
                    waste_type=waste_type,
                    mqtt_topic_fill_level=topic,
                    height_cm=DEFAULT_HEIGHT_CM,
                    current_fill_percent=0.0,
                )
            )
            count += 1
    print(f"✅ seed_trash_bin ready ({count} new bins)!")
