## 🌐 Web (Anh) — Module 0 → 6

**Module 0 — Nền tảng**

- [x] Khởi tạo repo, cấu trúc thư mục `web/`
- [ ] Setup FastAPI + React project
- [x] Setup PostgreSQL, PgAdmin, Alembic
- [x] Setup Cloudinary (API key)
- [x] Viết model/migration tạo bảng DB (Alembic)
- [x] Seed dữ liệu mẫu (2 khu vực, 6 thùng, `mqtt_topic_*`, `chieu_cao_H_cm`) + 1 tài khoản admin

**Module 1 — Error handling + Auth**

- [ ] BE: Error/Success response config, JWT access + refresh token, schemas/crud/service auth
- [ ] FE: Axios config, Auth Context, Protected routes, trang đăng nhập

**Module 2 — Dashboard realtime**

- [ ] BE: `GET /api/khu-vuc`, `GET /api/thung-rac`
- [ ] BE: MQTT client subscribe `mucday`, `trangthai/iot`, `trangthai/ai` → tính % đầy, update DB
- [ ] BE: Xử lý reconnect khi mất kết nối broker
- [ ] BE: Endpoint `/ws/thung-rac` + connection manager
- [ ] BE: Script giả lập publish MQTT để test độc lập
- [ ] FE: Layout, trang dashboard (2 khu vực × 3 thùng), load REST + WebSocket update

**Module 3 — Lịch sử phân loại**

- [ ] BE: Subscribe `phanloai` → tạo dòng `lich_su_phan_loai` (chỉ case thành công)
- [ ] BE: `POST /api/anh-phan-loai` (upload Cloudinary, update dòng)
- [ ] BE: `GET /api/lich-su-phan-loai` (filter, phân trang)
- [ ] BE: `PATCH /api/lich-su-phan-loai/{id}` (xác nhận đúng/sai)
- [ ] BE: `POST .../batch-delete`
- [ ] FE: Bảng log, bộ lọc (ngày/khu vực/loại rác/ảnh null), nút xác nhận, checkbox + xoá hàng loạt, giao diện upload ảnh thủ công theo `log_id`

**Module 4 — Thống kê**

- [ ] BE: `GET /api/thong-ke` (theo ngày/tuần/loại rác/khu vực, tỉ lệ đúng/sai)
- [ ] FE: Biểu đồ số lượng rác, biểu đồ độ chính xác model theo ngày

**Module 5 — Tích hợp thật**

- [ ] Test API bằng Postman/Swagger (làm sớm)
- [ ] Xác nhận 3 người dùng chung 1 broker
- [ ] Ghép từng luồng: mức đầy → phân loại (không ảnh) → ảnh → tín hiệu không tự tin
- [ ] Đối chiếu message thật với format đã chốt (qua MQTTX)
- [ ] Test tại đúng địa điểm demo

**Module 6 — Bàn giao**

- [ ] README hướng dẫn chạy web
- [ ] Tài liệu API/MQTT contract cho AI/IoT
- [ ] Ghi chú phần Web cho báo cáo

---
