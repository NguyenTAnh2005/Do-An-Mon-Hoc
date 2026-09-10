# Chung:

- Khởi tạo dự án git, cấu trúc thư mục chung
- Cấu hình .gitignore, env example
- Cài Eclipse Mosquitto — hỗ trợ chạy local MQTT broker
- Thống nhất & chốt văn bản: cấu trúc topic MQTT + format JSON từng loại (mucday, phanloai, trangthai) — gửi cho cả 3 người trước khi ai bắt đầu code phần liên quan MQTT
- Cài công cụ debug MQTTX — dùng chung để cả 3 người tự kiểm tra message mình gửi/nhận đúng chưa, không cần chờ người khác. [_`--> GHI CHÚ`_](../note/mqttx.md)
- Quyết định broker dùng khi tích hợp thật: chạy trên máy ai, địa chỉ IP là gì (khác với lúc mỗi người tự test local). [_`--> GHI CHÚ`_](../note/broker-mqtt.md)
- Test mạng: xác nhận phương án dùng dữ liệu di động cho 2 camera, laptop có đọc được stream ổn định không (Ổn).
