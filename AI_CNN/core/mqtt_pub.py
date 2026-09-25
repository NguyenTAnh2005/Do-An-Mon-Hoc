"""
mqtt_pub.py — Cầu nối MQTT (EMQX Cloud Serverless).

Nhiệm vụ:
    - Bọc paho-mqtt, cung cấp API đơn giản cho detector gọi.
    - Kết nối EMQX Cloud qua TLS (port 8883) + username/password.
    - Setup LWT để báo "offline" khi script chết đột ngột.

Input:  log_id, loai_rac, confidence, timestamp
Output: Message đẩy lên EMQX Cloud

Ai dùng:
    - detector.py gọi publish_classification() / publish_unsure().
    - worker.py gọi publish_offline() + disconnect() khi Ctrl+C.

Topic sử dụng:
    - truong/khu{n}/phanloai           → kết quả phân loại thành công
    - truong/khu{n}/khongchac          → tín hiệu "không tự tin"
    - truong/khu{n}/trangthai/ai       → LWT online/offline (retain=True)

⚠️  ĐIỂM CHẾT NGƯỜI:
    1. KHÔNG retain topic phanloai → nếu retain, ESP32 reboot sẽ
       nhận lại message cũ → servo mở vô cớ.
    2. client_id PHẢI unique (ai-khu{n}-{uuid_hex}) → 2 client cùng ID
       sẽ kick nhau khỏi broker.
    3. TLS bắt buộc (EMQX Cloud không cho port 1883).

Test riêng:
    - mosquitto_sub -h xxx.emqx.io -p 8883 --cafile ca.crt
      -u USER -P PASS -t "truong/#" -v
"""