# WEB

## Module 0 — Nền tảng

- Khởi tạo repo, cấu trúc thư mục `web/`
- `.gitignore`, `.env.example`
- Setup FastAPI project, setup React project
- Phía React tạo trang rỗng, Config file style JS
- Setup PostgreSQL, kết nối qua PgAdmin, cài thư viện cần thiết, cấu hình alembic
- Setup Cloudinary, lấy API key
- Setup Mosquitto broker để test
- Viết model/migration tạo bảng cho DB (alembic)
- Seed dữ liệu mẫu (2 khu vực, 6 thùng, `mqtt_topic_*`, `chieu_cao_H_cm`) + 1 tài khoản admin (script python và alembic)

## Module 1 — Error handling + Auth

_Note_: Web chỉ hỗ trợ đăng nhập mới vào xem quản lý, chưa hỗ trợ nhiều phân quyền.

**BE**: Hệ thống đăng nhập jwt-access token + refresh token

- Error Handling, Success Response config
- jwt, refresh token service
- Các schemas, crud, service API liên quan đến a  uth

**FE**

- Axios Config
- Auth axios service
- Auth Context, Auth Protected,
- Xử lý các routes web
- Trang đăng nhập

## Module 2 — Dashboard realtime (mức đầy + trạng thái online)

**BE**

- `GET /api/khu-vuc`, `GET /api/thung-rac`
- MQTT client: kết nối broker, subscribe `mucday`, `trangthai/iot`, `trangthai/ai`
- Xử lý message: tính % đầy, UPDATE `thung_rac`; UPDATE `iot_online`/`ai_online`
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

- MQTT: subscribe `phanloai`, tạo dòng mới `lich_su_phan_loai` (ảnh null)
- `POST /api/anh-phan-loai` — nhận ảnh multipart + `log_id`, upload Cloudinary, UPDATE dòng tương ứng
- `GET /api/lich-su-phan-loai` — filter theo ngày/khu vực/loại rác, phân trang
- `PATCH /api/lich-su-phan-loai/{id}` — xác nhận đúng/sai
- Test ghép `log_id`: giả lập MQTT tới trước, ảnh tới sau, kiểm tra ghép đúng dòng

**FE**

- Bảng/danh sách log: thời gian, loại rác, độ chắc chắn, ảnh, trạng thái xác nhận
- Bộ lọc theo ngày/khu vực/loại rác
- Nút xác nhận đúng/sai
- Phân trang

## Module 4 — Thống kê

**BE**

- `GET /api/thong-ke` — tổng hợp theo ngày/tuần/loại rác/khu vực, kèm tỉ lệ đúng/sai theo ngày

**FE**

- Biểu đồ số lượng rác theo loại, theo khu vực, theo thời gian
- Biểu đồ độ chính xác model theo ngày

## Module 5 — Kiểm thử & tích hợp thật (xuyên suốt, không tách BE/FE)

- Test từng API bằng Postman/Swagger (làm sớm, không đợi cuối)
- Trước khi ghép thật: xác nhận cả 3 người dùng chung 1 broker (cùng địa chỉ, không phải mỗi người chạy localhost riêng)
- Ghép từng luồng riêng lẻ, KHÔNG ghép hết 1 lần:
  1. Ghép luồng mức đầy trước (đơn giản, dễ debug nếu lỗi)
  2. Rồi ghép luồng phân loại (không kèm ảnh trước — test riêng phần MQTT)
  3. Cuối cùng mới ghép thêm luồng gửi ảnh HTTP (phức tạp nhất, nhiều bước nhất)
- Ở mỗi bước ghép, đối chiếu message thật nhận được (in ra log) với format đã thống nhất — phát hiện lệch sớm
- Tích hợp thật với script AI + ESP32 khi 2 bạn có bản chạy được
- Test tại đúng địa điểm demo (mạng, thiết bị)

## Module 6 — Tài liệu & bàn giao

- README hướng dẫn chạy web
- Tài liệu API/MQTT contract cho 2 bạn AI/IoT
- Ghi chú phần Web cho báo cáo
