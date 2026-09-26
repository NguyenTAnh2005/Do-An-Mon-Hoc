import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.models import ClassificationLog, Area, WasteType, ConfirmationResult

SAMPLE_COUNT = 150
DAYS_BACK = 30


def seed_classification_log(db: Session):
    """Generate ~150 fake classification log rows spread over the last 30 days.

    Purpose: enough data to test FE (dashboard, list, filter by area/waste type/time).
    Requires area to already have an id (db.flush() after seed_area before calling this).
    """
    area_ids = [a.id for a in db.query(Area.id).all()]
    if not area_ids:
        print("⚠️ No areas found, run seed_area (and flush) first.")
        return

    now = datetime.now(timezone.utc)
    waste_type_list = list(WasteType)

    count = 0
    for _ in range(SAMPLE_COUNT):
        created_at = now - timedelta(
            days=random.uniform(0, DAYS_BACK),
            seconds=random.randint(0, 86400),
        )
        waste_type = random.choice(waste_type_list)
        confidence = round(random.uniform(0.55, 0.99), 2)
        log_id = str(uuid.uuid4())

        # 15% missing image — simulates a row still waiting for the HTTP upload (separate image channel)
        has_image = random.random() > 0.15

        # Manual confirmation: mostly unconfirmed, remainder mostly correct / some incorrect
        roll = random.random()
        if roll < 0.6:
            confirmation_result = ConfirmationResult.UNCONFIRMED
        elif roll < 0.85:
            confirmation_result = ConfirmationResult.CORRECT
        else:
            confirmation_result = ConfirmationResult.INCORRECT

        db.add(
            ClassificationLog(
                log_id=log_id,
                area_id=random.choice(area_ids),
                detected_waste_type=waste_type,
                confidence=confidence,
                image_url=(
                    f"https://res.cloudinary.com/df5mtvzkn/image/upload/v1790302346/Phan_loai_rac/journey-18-09_tyh0kk.jpg"
                    if has_image
                    else None
                ),
                cloudinary_public_id=f"seed_{log_id}" if has_image else None,
                confirmation_result=confirmation_result,
                created_at=created_at,
            )
        )
        count += 1

    print(f"✅ seed_classification_log ready ({count} rows)!")
