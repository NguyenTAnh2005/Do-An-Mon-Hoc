# Giả lập MỘT thiết bị IoT (khu vực 1) để thử LWT
# Tắt đột ngột tiến trình này để broker tự publish tin offline

import json
import time
import paho.mqtt.client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from app.core.config import settings as AppSettings

BROKER_HOST = AppSettings.BROKER_ADDRESS
BROKER_PORT = AppSettings.MQTT_PORT
CLIENT_ID = "simulate_lwt_iot_area1"
USER = "Simulate_Publish"
PASS = "simulate_publish_123"

STATUS_TOPIC = "school/area1/status/iot"
ONLINE_PAYLOAD = json.dumps({"status": "online"})    # đổi cho khớp payload ở publish_status
OFFLINE_PAYLOAD = json.dumps({"status": "offline"})  # cùng định dạng với tin offline thật

client = mqtt_client.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id=CLIENT_ID
)
client.username_pw_set(username=USER, password=PASS)
client.tls_set()

# Đăng ký di chúc TRƯỚC khi connect
client.will_set(STATUS_TOPIC, OFFLINE_PAYLOAD, qos=1, retain=True)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[LWT] Đã kết nối broker: {reason_code}")
    client.publish(STATUS_TOPIC, ONLINE_PAYLOAD, qos=1, retain=True)
    print(f"[LWT] {STATUS_TOPIC} -> {ONLINE_PAYLOAD} (retained)")


client.on_connect = on_connect

if __name__ == "__main__":
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=10)
    client.loop_start()
    print("[LWT] Đang chạy. Tắt đột ngột (đóng cửa sổ terminal hoặc kill tiến trình) để thử LWT")

    # Cố ý KHÔNG có disconnect() ở bất kỳ đâu trong file này
    while True:
        time.sleep(1)