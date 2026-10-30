from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.models.models import ClassificationLog


def _apply_filters(stmt, area_id, waste_type, confirmation_result, has_image, start_time, end_time):
    if area_id is not None:
        stmt = stmt.where(ClassificationLog.area_id == area_id)
    if waste_type is not None:
        stmt = stmt.where(ClassificationLog.detected_waste_type == waste_type)
    if confirmation_result is not None:
        stmt = stmt.where(ClassificationLog.confirmation_result == confirmation_result)
    if has_image is True:
        stmt = stmt.where(ClassificationLog.image_url.is_not(None))
    elif has_image is False:
        stmt = stmt.where(ClassificationLog.image_url.is_(None))

    # Lọc theo khoảng thời gian: lấy từ start_time (bao gồm) đến end_time (không bao gồm)
    if start_time is not None:
        stmt = stmt.where(ClassificationLog.created_at >= start_time)
    if end_time is not None:
        stmt = stmt.where(ClassificationLog.created_at < end_time)
    return stmt


def get_logs(db: Session, area_id, waste_type, confirmation_result, has_image, start_time, end_time, offset, limit):
    stmt = select(ClassificationLog).options(joinedload(ClassificationLog.area))
    stmt = _apply_filters(stmt, area_id, waste_type, confirmation_result, has_image, start_time, end_time)
    stmt = stmt.order_by(ClassificationLog.created_at.desc(), ClassificationLog.id.desc())
    stmt = stmt.offset(offset).limit(limit)
    return list(db.execute(stmt).scalars().all())


def count_logs(db: Session, area_id, waste_type, confirmation_result, has_image, start_time, end_time):
    stmt = select(func.count()).select_from(ClassificationLog)
    stmt = _apply_filters(stmt, area_id, waste_type, confirmation_result, has_image, start_time, end_time)
    return db.execute(stmt).scalar_one()


def get_log_by_id(db: Session, record_id: int):
    stmt = (
        select(ClassificationLog)
        .options(joinedload(ClassificationLog.area))
        .where(ClassificationLog.id == record_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def update_confirmation(db: Session, log, new_result):
    log.confirmation_result = new_result
    db.commit()
    db.refresh(log)
    return log


def update_image(db: Session, log, image_url, public_id):
    log.image_url = image_url
    log.cloudinary_public_id = public_id
    db.commit()
    db.refresh(log)
    return log


def get_logs_by_ids(db: Session, ids):
    stmt = select(ClassificationLog).where(ClassificationLog.id.in_(ids))
    return list(db.execute(stmt).scalars().all())


def delete_log(db: Session, log):
    db.delete(log)
    db.commit()


def delete_logs(db: Session, logs):
    for log in logs:
        db.delete(log)
    db.commit()


