# Tóm tắt các quyết định đã chốt

> **Mục đích file này:** bản tóm lược ngắn gọn tất cả quyết định kiến trúc đã thống nhất, không đi sâu chi tiết kỹ thuật — chi tiết đầy đủ nằm ở các file được link tới. Dùng file này để cập nhật nhanh khi lâu ngày không xem lại dự án.

## Tổng quan đề tài

Hệ thống quản lý & phân loại rác thải thông minh tại trường học: camera nhận diện loại rác qua Deep Learning → tự động mở đúng ngăn thùng; cảm biến khoảng cách giám sát mức đầy realtime; website trung tâm hiển thị dashboard, lịch sử, thống kê. Demo trên **2 khu vực × 3 thùng/khu vực** (tái chế / hữu cơ / vô cơ) do giới hạn chi phí.

Phân công: **Vũ** — AI/CNN, **Tường** — IoT, **Anh** — Web (kiêm PM, người duyệt PR).

## Phần cứng đã chốt

- Chip IoT: **ESP32** (1 con/khu vực, điều khiển cả 3 thùng)
- Cảm biến mức đầy: **HC-SR04** (1/thùng)
- Servo mở nắp: 1/thùng — **tự động mở đúng ngăn** dựa vào `loai_rac` nhận qua MQTT, không phụ thuộc LED nào cả
- **LED phản hồi: chỉ báo "detect được hay không", không gắn theo thùng cụ thể — cả 2 đều là tín hiệu cấp zone**
  - LED xanh: 1/zone (2 cái tổng, **không phải 1/thùng**) — bật khi AI phân loại thành công (bất kể loại rác gì)
  - LED đỏ: 1/zone (2 cái tổng), **độc lập, không dùng chung chân/module với LED xanh** — bật khi AI không đủ tự tin để phân loại
  - → Mỗi ESP32 quản lý: 3 servo (theo thùng, tự động) + 2 LED (1 xanh + 1 đỏ, theo zone)
- Camera: smartphone chạy IP Webcam/DroidCam, 1 cái/khu vực

Chi tiết đầy đủ: [Danh sách thành phần](../01-kien-truc-tong-the/danh-sach-thanh-phan.md), [Thiết kế IoT](../03-iot/thiet-ke-iot.md)

## Logic nhận diện đã chốt

- YOLOv8n fine-tune từ Roboflow, 3 lớp, mục tiêu 80–85% accuracy
- Có lớp lọc **frame differencing** chặn trước, tránh nhận nhầm khay trống
- State machine `IDLE → DETECTING → COOLDOWN`, chốt kết quả theo **vote tần suất class** (không phải confidence cao nhất đơn lẻ)
- Khi không class nào đạt ngưỡng tối thiểu → **AI publish tín hiệu "không tự tin"**, ESP32 bật **LED đỏ riêng của zone**, yêu cầu người dùng tự phân loại tay
  - **Case này KHÔNG insert gì vào DB `lich_su_phan_loai`** — vì không có kết quả phân loại thật, lưu lại không có giá trị thống kê
  - **Case miss_count** (không thấy vật gì, chỉ là thoáng qua) → huỷ phiên, về IDLE, không publish gì, không có LED nào bật cả — đây là hành vi bình thường

Chi tiết đầy đủ: [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md)

## MQTT đã chốt

- Broker: Mosquitto, chạy trên máy 1 người khi tích hợp thật, cả nhóm dùng chung 1 địa chỉ IP (cùng mạng WiFi)
- Cấu trúc topic: `truong/khu{n}/mucday/{loai_rac}`, `truong/khu{n}/phanloai`, `truong/khu{n}/trangthai/iot`, `truong/khu{n}/trangthai/ai`
- QoS: mức đầy = 0, phân loại/trạng thái = 1
- Trạng thái online/offline dùng cơ chế **LWT**, tách riêng 2 cờ `iot_online` / `ai_online`

Chi tiết đầy đủ: [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md)

## Web đã chốt

- Stack: React + FastAPI (sync) + PostgreSQL (ORM + Alembic) + Cloudinary + JWT
- Backend chạy song song 2 vai trò trong 1 process: MQTT subscriber + WebSocket server
- Ảnh và kết quả phân loại là 2 luồng độc lập (MQTT tới trước, ảnh tới sau), ghép bằng `log_id` (uuid do AI tự sinh)
- Ảnh lỗi mạng: **không tự động retry**, AI lưu cục bộ theo `log_id`, quản lý upload lại thủ công qua giao diện
- Mỗi `khu_vuc`/`thung_rac` tự lưu **full topic MQTT** của chính nó trong DB, không dùng prefix nối chuỗi

Chi tiết đầy đủ: [Kiến trúc Backend realtime](../05-web/kien-truc-backend-realtime.md), [Thiết kế Database](../05-web/thiet-ke-database.md)

## Còn chưa chốt (cần bàn tiếp)

- [ ] **Format chính xác của tín hiệu "không tự tin"** trên MQTT: publish qua topic `phanloai` với field riêng, hay tách hẳn 1 topic phụ? Cần Vũ (AI) và Tường (IoT) thống nhất field/topic cụ thể trước khi code. Xem đề xuất tạm trong [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md#tín-hiệu-không-tự-tin-đề-xuất---cần-chốt).
- [ ] Kiểm tra băng thông WiFi khi 2 luồng camera stream cùng lúc tại đúng địa điểm demo (thuộc phần AI/IoT xử lý, Web không cần can thiệp).

## Đã xác nhận ổn, không cần lo lại

- [x] 2 điện thoại + laptop cùng mạng WiFi/hotspot khi demo — vẫn nên test lại đúng địa điểm trước ngày báo cáo vì WiFi trường có thể chặn giao tiếp thiết bị với nhau.
