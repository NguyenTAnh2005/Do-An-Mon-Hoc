import logging 
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from app.models.models import TrashBin, Area, ClassificationLog, WasteType
from app.db_connection import connect_db

logger = logging.getLogger(" MQTT-handler")

# ============= HANDLE XỬ LÝ FILL LEVEL 
def compute_percent(d:float, height_cm: float)->float:
    percent = (height_cm - d) * 100 /height_cm

    # 1. Giới hạn sàn (Không cho phép nhỏ hơn 0)
    if percent < 0.0:
        percent = 0.0
    # 2. Giới hạn trần (Không cho phép lớn hơn 100)
    elif percent > 100.0:
        percent = 100.0
        
    # 3. Làm tròn và trả về kết quả đến chữ số thập phân thứ nhất
    return round(percent, 1)

def handle_fill_level(topic:str, data: dict) -> dict|None: 
    """
    Giả sử message là:
        {
            "distance_cm": 12.5,
            "timestamp": "2026-09-10T14:32:05Z"
        }
    """
    d = data.get("distance_cm")
    # Nếu d không phải là int hay float
    if not isinstance(d, (int, float)):
        logger.warning(" [WARNING] fill_level thieu truong d: %s", data)
        return None

    db = next(connect_db())
    try:
        db_trash_bin = db.execute(
            select(TrashBin).where(TrashBin.mqtt_topic_fill_level == topic)
        ).scalar_one_or_none()
        if db_trash_bin is None:
            logger.warning(" [WARNING] Khong tim thay thung cho topic %s", topic)
            return None
        percent = compute_percent(d = d, height_cm=db_trash_bin.height_cm)
        db_trash_bin.current_fill_percent = percent
        db_trash_bin.updated_at = datetime.now(timezone.utc)
        db.commit()
        return{
            "type": "fill_level",
            "area_id": db_trash_bin.area_id,
            "waste_type": db_trash_bin.waste_type.value,
            "current_fill_percent": percent,
            "timestamp": data.get("timestamp"),
        }
    finally:
        db.close()

# ============== HANDLE XỬ LÝ STATUS IOT, AI
# Message publish giả định là 
# topic school/area1/status/iot
# topic school/area1/status/ai
# {"status": "online"} hoặc {"status": "offline"}

def handle_status(topic: str, sub:str | None, data:dict)-> dict|None:
    status_text = data.get("status")
    
    if status_text == "online":
        online = True
    elif status_text == "offline":
        online = False
    else:
        logger.warning(" [WARNING] status loi o truong status: %s", data)
        return None

    if sub == "iot":
        topic_column = Area.mqtt_topic_status_iot
        online_field = "iot_online"
        last_online_field = "iot_last_online"
    elif sub == "ai":
        topic_column = Area.mqtt_topic_status_ai
        online_field = "ai_online"
        last_online_field = "ai_last_online"

    else:
        logger.warning(" [WARNING] status khong ro nguon: %s", sub)
        return None

    db = next(connect_db())

    try:
        db_area = db.execute(
            select(Area).where(topic_column == topic)
        ).scalar_one_or_none()
        if db_area  is None:
            logger.warning(" [WARNING] Khong tim thay khu vuc cho topic %s", topic)
            return None
        # Biến online lấy ở bên trên
        was_online = getattr(db_area, online_field)
        setattr(db_area, online_field, online)
        if online or was_online:
            setattr(db_area, last_online_field, datetime.now(timezone.utc))

        db.commit()
        return{
            "type":"status",
            "area_id": db_area.id,
            "source":sub,
            "online":online
        }
    finally:
        db.close()

# =========== HANDLER CHO CLASSIFICATION_LOG
# Giả định message gửi là:
# {"log_id": "...", "waste_type": "...", "confidence": 0.92, "timestamp": "..."}
# topic mqtt vd: school/area1/classification

def handle_classification(topic:str, data:dict) -> dict|None:
    try:
        # Đưa về obj uuid, nếu sai định dạng có thê bắt lỗi
        # sau đó lấy lại ở dạng str vì model database là varchar
        log_id_obj = uuid.UUID(str(data.get("log_id")))
        log_id = str(log_id_obj)

        waste_type = WasteType(data.get("waste_type"))
        # fromisoformat để đối time iso sang datetime python

        timestamp = datetime.fromisoformat(data.get("timestamp"))
    except(ValueError, TypeError):
        logger.warning(" [WARNING] classification sai log_id, waste_type hoac timestamp: %s", data)
        return

    confidence = data.get("confidence")
    if not isinstance(confidence, (int, float)):
        logger.warning(" [WARNING] classification sai confidence: %s", data)
        return

    db = next(connect_db())
    try:
        db_area = db.execute(
            select(Area).where(Area.mqtt_topic_classification == topic)
        ).scalar_one_or_none()
        if db_area is None:
            logger.warning(" [WARNING] Khong tim thay khu vuc cho topic %s", topic)
            return
        # Vì QOS của classification topic là 1 nên có thể bị gửi trùng nhiều lần 
        # Mà log_id là unique vậy nên cần check thêm, nếu trùng thì không thêm nữa.
        existed = db.execute(
            select(ClassificationLog).where(ClassificationLog.log_id == log_id)
        ).scalar_one_or_none()

        if existed is not None:
            logger.info(" [INFO] Bo qua tin classification trung log_id=%s", log_id)
            return
        new_classification_log = ClassificationLog(
            log_id = log_id,
            area_id = db_area.id,
            detected_waste_type = waste_type,
            confidence = confidence,
            created_at = timestamp
        )
        db.add(new_classification_log)
        db.commit()
        logger.info(" [INFO] Da luu classification log_id=%s", log_id)

    finally:
        db.close()


