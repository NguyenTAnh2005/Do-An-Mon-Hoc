"""Publish AI classifications and status to the MQTT broker."""

import json
import math
import uuid
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import (
    MQTT_HOST,
    MQTT_PASS,
    MQTT_PORT,
    MQTT_USER,
    SYSTEM_CLASSES,
    topic_classification,
    topic_status_ai,
    topic_uncertain,
)


class MqttPublisher:
    def __init__(self, khu_vuc: int):
        self.khu_vuc = khu_vuc
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"ai-area{khu_vuc}-{uuid.uuid4().hex[:8]}",
        )
        self.client.username_pw_set(MQTT_USER, MQTT_PASS)
        self.client.tls_set()
        self.client.will_set(
            topic_status_ai(khu_vuc),
            json.dumps({"status": "offline"}),
            qos=1,
            retain=True,
        )
        self.client.on_connect = self._on_connect
        if self.client.connect(MQTT_HOST, MQTT_PORT) != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError("Không kết nối được MQTT broker")
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self._publish(topic_status_ai(self.khu_vuc), {"status": "online"}, retain=True)
        else:
            print(f"[MQTT-area{self.khu_vuc}] Kết nối thất bại: {reason_code}")

    def _publish(self, topic: str, payload: dict, retain: bool = False):
        info = self.client.publish(topic, json.dumps(payload), qos=1, retain=retain)
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"Không gửi được MQTT topic {topic}: {info.rc}")
        return info

    def publish_classification(self, log_id: str, waste_type: str, confidence: float, timestamp: str):
        uuid.UUID(log_id)
        if waste_type not in SYSTEM_CLASSES:
            raise ValueError(f"Loại rác không hợp lệ: {waste_type}")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise ValueError(f"Độ tin cậy không hợp lệ: {confidence}")
        return self._publish(
            topic_classification(self.khu_vuc),
            {"log_id": log_id, "waste_type": waste_type, "confidence": confidence, "timestamp": timestamp},
        )

    def publish_unsure(self):
        return self._publish(
            topic_uncertain(self.khu_vuc),
            {"timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")},
        )

    def publish_offline(self):
        self._publish(topic_status_ai(self.khu_vuc), {"status": "offline"}, retain=True).wait_for_publish(timeout=3)

    def disconnect(self):
        self.client.disconnect()
        self.client.loop_stop()
