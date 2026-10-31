# File dùng để bắn publish nhiều topic với nhiều message liên tục
# Hỗ trợ giả lập dữ liệu

import uuid
import random
from datetime import datetime, timezone
import json
import time
from paho.mqtt import client as mqtt_client
from paho.mqtt.enums import CallbackAPIVersion
from app.core.config import settings as AppSettings


# Cấu hình Broker 
BROKER_HOST = AppSettings.BROKER_ADDRESS
BROKER_PORT = AppSettings.MQTT_PORT
SIMULATE_ID = "simulate_001"
SIMULATE_USER = "Simulate_Publish"
SIMULATE_PASS = "simulate_publish_123"

# Cấu hình giả lập
AREA_IDS = [1, 2]
WASTE_TYPES = ["recyclable", "organic", "inorganic"]
BIN_HEIGHT_CM = 11.5            
START_DISTANCE_CM = 11.5        # thùng gần như trống
STEP_CM = 1                   # mỗi lần publish, khoảng cách giảm 2cm
MIN_DISTANCE_CM = 4           # gần đầy thì reset
PUBLISH_INTERVAL_SEC = 5

CLASSIFY_EVERY_N_LOOPS = 2    # cứ 4 vòng (20 giây) publish một classification

# Giá trị khoảng cách ban đầu của từng thùng, mỗi thùng lệch nhau để dashboard có nhiều mức % khác nhau
distances = {}
initial_distance = START_DISTANCE_CM
for area_id in AREA_IDS:
    for waste_type in WASTE_TYPES:
        distances[(area_id, waste_type)] = initial_distance
        initial_distance -= STEP_CM
        if initial_distance < MIN_DISTANCE_CM:
            initial_distance = START_DISTANCE_CM


# Cấu hình Client MQTT
client = mqtt_client.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id=SIMULATE_ID
)
client.username_pw_set(username=SIMULATE_USER, password=SIMULATE_PASS)
client.tls_set()


# Giả lập publish mức đầy 
def publish_fill_levels():
    for area_id in AREA_IDS:
        for waste_type in WASTE_TYPES:
            key = (area_id, waste_type)
            distance = distances[key]

            topic = f"school/area{area_id}/fill_level/{waste_type}"
            payload = json.dumps({
                "distance_cm": distance,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            client.publish(topic, payload, qos=0)
            print(f"[SIM] {topic} -> {payload}")

            # Thùng đầy lên: khoảng cách giảm; chạm mức tối thiểu thì coi như đã đổ rác
            new_distance = distance - STEP_CM
            if new_distance < MIN_DISTANCE_CM:
                new_distance = START_DISTANCE_CM
            distances[key] = new_distance
        print("===================")

#  Giả lập publish trạng thái ai, iot
def publish_status(online: bool):
    # Đổi payload cho khớp handler status của Backend
    payload = json.dumps({"status": "online" if online else "offline"})
    for area_id in AREA_IDS:
        for source in ["iot", "ai"]:
            topic = f"school/area{area_id}/status/{source}"
            client.publish(topic, payload, qos=1, retain=True)
            print(f"[SIM] {topic} -> {payload} (retained)")

# Giả lập publish phân loại rác
def publish_classification():
    area_id = random.choice(AREA_IDS)
    waste_type = random.choice(WASTE_TYPES)

    topic = f"school/area{area_id}/classification"
    payload = json.dumps({
        "log_id": str(uuid.uuid4()),
        "waste_type": waste_type,
        "confidence": round(random.uniform(0.6, 0.99), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    client.publish(topic, payload, qos=1)
    print(f"[SIM] {topic} -> {payload}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"[SIM] Đã kết nối broker: {reason_code}")
    publish_status(True)
    print("===================")
client.on_connect = on_connect

if __name__ == "__main__":
    client.connect(BROKER_HOST, BROKER_PORT)
    client.loop_start()
    time.sleep(1)  # chờ broker trả CONNACK trước khi publish
    loop_count = 0
    try:
        while True:
            publish_fill_levels()
            loop_count += 1
            if loop_count % CLASSIFY_EVERY_N_LOOPS == 0:
                # publish_classification()
                pass
            time.sleep(PUBLISH_INTERVAL_SEC)
    except KeyboardInterrupt:
        print("[SIM] Dừng giả lập")
    finally:
        publish_status(False)
        time.sleep(0.5)
        client.disconnect()
        client.loop_stop()