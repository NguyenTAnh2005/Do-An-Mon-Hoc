# Danh sách công việc — Web (Anh), Module 0 → 6

> **Mục đích file này:** checklist chi tiết theo module cho phần Web (BE + FE), đã gộp các bổ sung mới nhất (batch delete, upload ảnh thủ công...). Xem thiết kế đầy đủ tại [Kiến trúc Backend realtime](./kien-truc-backend-realtime.md) và [Thiết kế Database](./thiet-ke-database.md).

## Module 0 — Nền tảng

- Khởi tạo repo, cấu trúc thư mục `web/`
- `.gitignore`, `.env.example`
- Setup FastAPI project, setup React project
- Phía React tạo trang rỗng, config file style JS
- Setup PostgreSQL, kết nối qua PgAdmin, cài thư viện cần thiết, cấu hình Alembic
- Setup Cloudinary, lấy API key
- Setup Mosquitto broker để test
- Viết model/migration tạo bảng cho DB (Alembic)
- Seed dữ liệu mẫu (2 khu vực, 6 thùng, `mqtt_topic_*`, `chieu_cao_H_cm`) + 1 tài khoản admin (script python và alembic)

## Module 1 — Error handling + Auth

_Note: Web chỉ hỗ trợ đăng nhập để vào xem quản lý, chưa hỗ trợ nhiều phân quyền._

**BE**

- Error Handling, Success Response config
- JWT access token + refresh token service
- Các schemas, crud, service API liên quan đến auth

**FE**

- Axios config
- Auth axios service
- Auth Context, Auth Protected
- Xử lý các routes web
- Trang đăng nhập

## Module 2 — Dashboard realtime (mức đầy + trạng thái online)

**BE**

- `GET /api/khu-vuc`, `GET /api/thung-rac`
- MQTT client: kết nối broker, subscribe `mucday`, `trangthai/iot`, `trangthai/ai`
- Xử lý message: tính % đầy, UPDATE `thung_rac`; UPDATE `iot_online`/`ai_online`, cập nhật chiều cao thùng rác
- Xử lý reconnect khi mất kết nối broker
- Endpoint `/ws/thung-rac`, quản lý danh sách kết nối, đẩy dữ liệu khi có update
- Script giả lập publish MQTT để test độc lập (chưa cần AI/IoT thật)

**FE**

- Layout tổng (header/navigation)
- Trang dashboard: hiển thị 2 khu vực × 3 thùng (% đầy, online/offline)
- Gọi API lúc load trang, mở WebSocket để cập nhật realtime
- Xử lý trạng thái loading/lỗi khi API/WebSocket chưa sẵn sàng

## Module 3 — Lịch sử phân loại (kèm ảnh)

**BE**

- MQTT: subscribe `phanloai`, tạo dòng mới `lich_su_phan_loai` (ảnh null) — **chỉ khi có kết quả phân loại thành công thật sự**, không xử lý gì với tín hiệu "không tự tin" (xem [luồng nhận diện](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md))
- `POST /api/anh-phan-loai` — nhận ảnh multipart + `log_id`, upload Cloudinary, UPDATE dòng tương ứng
- `GET /api/lich-su-phan-loai` — filter theo ngày/khu vực/loại rác, phân trang
- `PATCH /api/lich-su-phan-loai/{id}` — xác nhận đúng/sai
- `POST /api/lich-su-phan-loai/batch-delete` (hoặc DELETE) — nhận list `id`/`log_id`, xoá theo `WHERE id IN (...)` trong 1 transaction
- Test ghép `log_id`: giả lập MQTT tới trước, ảnh tới sau, kiểm tra ghép đúng dòng

**FE**

- Bảng/danh sách log: thời gian, loại rác, độ chắc chắn, ảnh, trạng thái xác nhận
- Bộ lọc theo ngày/khu vực/loại rác + bộ lọc `url_anh IS NULL` (tìm nhanh dòng thiếu ảnh)
- Nút xác nhận đúng/sai
- Phân trang
- Checkbox chọn nhiều dòng + nút "Xoá các mục đã chọn"
- Giao diện upload ảnh thủ công theo `log_id` (dùng cho case AI lưu ảnh cục bộ do lỗi mạng — xem [luồng nhận diện, mục 7.3](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md#73-ảnh-lỗi-mạng-không-post-được--đơn-giản-hoá-không-tự-động-retry))

## Module 4 — Thống kê

**BE**

- `GET /api/thong-ke` — tổng hợp theo ngày/tuần/loại rác/khu vực, kèm tỉ lệ đúng/sai theo ngày

**FE**

- Biểu đồ số lượng rác theo loại, theo khu vực, theo thời gian
- Biểu đồ độ chính xác model theo ngày

## Module 5 — Kiểm thử & tích hợp thật (xuyên suốt, không tách BE/FE)

- Test từng API bằng Postman/Swagger (làm sớm, không đợi cuối)
- Trước khi ghép thật: xác nhận cả 3 người dùng chung 1 broker (xem [setup broker mạng nội bộ](../06-mqtt/setup-broker-mang-noi-bo.md))
- Ghép từng luồng riêng lẻ, KHÔNG ghép hết 1 lần:
  1. Ghép luồng mức đầy trước (đơn giản, dễ debug nếu lỗi)
  2. Rồi ghép luồng phân loại (không kèm ảnh trước — test riêng phần MQTT)
  3. Cuối cùng mới ghép thêm luồng gửi ảnh HTTP (phức tạp nhất, nhiều bước nhất)
  4. Ghép riêng luồng tín hiệu "không tự tin" → LED đỏ (không liên quan Web, nhưng nên có mặt để quan sát log MQTTX khi test)
- Ở mỗi bước ghép, đối chiếu message thật nhận được (in ra log, hoặc xem qua MQTTX) với format đã thống nhất — phát hiện lệch sớm
- Tích hợp thật với script AI + ESP32 khi 2 bạn có bản chạy được
- Test tại đúng địa điểm demo (mạng, thiết bị)

## Module 6 — Tài liệu & bàn giao

- README hướng dẫn chạy web
- Tài liệu API/MQTT contract cho 2 bạn AI/IoT (link tới [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md))
- Ghi chú phần Web cho báo cáo
