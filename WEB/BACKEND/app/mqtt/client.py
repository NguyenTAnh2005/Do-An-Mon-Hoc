# File cấu hình mqtt cho backend
# + Kết nối đến broker, log khi có lỗi
# + subcribe các topic cần thiết 
# + Gắn vào vòng đời bằng lifespan ( main.py)
import logging
import json
import asyncio
from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from app.core.config import settings
from app.mqtt import parser as parser_service
from app.mqtt import handlers as handle_service

# Cấu hình Logger để theo dõi:
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(" MQTT-client")

# Cấu hình sẵn các topic backend subscribe
# tên topic, mức QOS
SUBSCRIBE_TOPICS = [
    ("school/+/fill_level/+", 0),
    ("school/+/classification", 1),
    ("school/+/status/+", 1),
]

# KHai báo hàm onconnect
def on_connect(client, userdata, flags, reason_code, properties = None):
    """
    Hàm callback được tự động gọi khi client kết nối thành công hoặc thất bại tới MQTT Broker.
    """
    # XỬ lý khi có lỗi trả về 
    if reason_code.is_failure:
        logger.error(f" [FAILED] Kết nối thất bại. Mã lỗi: {reason_code}")
        return 
    
    logger.info(f" [SUCCESS] Kết nối thành công tới EMQX. Client ID: {settings.CLIENT_ID}")
    # Connect thành công thì cho client subcribe các topic theo mức Qos tương ứng
    client.subscribe(SUBSCRIBE_TOPICS)
    logger.info(f" [SUBSCRIBE] Đã đăng ký {len(SUBSCRIBE_TOPICS)} topic")

# Khai báo hàm disconnect 
def on_disconnect(client, userdata, disconnect_flags, reason_code, properties = None):
    logger.warning(f" [DISCONNECTED] Mất kết nối tới broker. Mã: {reason_code}")

# Khai báo hàm on_message
def on_message(client, userdata, message):
    """
    message.payload là dữ liệu dạng bytes
    """
    try:
        parsed = parser_service.parse_topic(message.topic)
        if parsed is None:
            logger.warning(f" [WARNING] Topic khong hop le: {message.topic}")
            return
        kind, sub = parsed
        data = json.loads(message.payload.decode("utf-8"))
        
        result = None
        if kind == "fill_level":
            result = handle_service.handle_fill_level(
                    topic=message.topic,
                    data=data
            )
            # print(f" [SUBSCRIBE] Topic: {message.topic}, Value: {data}")
        elif kind == "classification":
            result = handle_service.handle_classification(
                    topic=message.topic,
                    data=data
            )
        elif kind == "status":
            result = handle_service.handle_status(
                    topic=message.topic,
                    sub=sub,
                    data=data
            )
        else:
            logger.warning(" [WARNING] Loai tin chua ho tro: %s", kind)
            return
        if result is None:
            return

        asyncio.run_coroutine_threadsafe(
            userdata["manager"].broadcast(result),
            userdata["loop"],
        )

    except Exception:
        logger.exception(f" [WARNING] on_message loi, topic={message.topic}")


# ============ KHỞI TẠO MQTT CLIENT 
# Callback API 
client = mqtt_client.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id=settings.CLIENT_ID
)
# Username, password
client.username_pw_set( username=settings.CLIENT_USERNAME, password=settings.CLIENT_PASSWORD)

# TLS 
client.tls_set()

# Gán các hàm call back
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

def start(loop, manager):
    client.user_data_set({
        "loop":loop,
        "manager": manager
    })
    # connect async không chặn: broker lỗi thì server vẫn khởi động, paho tự thử lại 
    client.connect_async(host=settings.BROKER_ADDRESS, port=settings.MQTT_PORT)
    client.loop_start() # mở thread riêng để nghe broker

def stop():
    client.disconnect() # Gửi gói disconnet đến broker
    client.loop_stop() # dừng thread



