# 🗓️ Tổng quan logic triển khai

```
Tuần 1: Chốt nền tảng (MQTT contract, DB schema) — bắt buộc trước khi 3 người tách ra
Tuần 2-4: Mỗi người làm phần riêng song song (có thể test độc lập bằng MQTTX/mock)
Tuần 5: Hoàn thiện + polish từng phần riêng, chuẩn bị ghép
Tuần 6-7: Tích hợp thật (ghép từng luồng một, không ghép hết 1 lần)
Tuần 8: Tích hợp hoàn chỉnh + báo cáo + buffer xử lý lỗi phát sinh
```

---

## 📅 Chi tiết theo tuần

### **Tuần 1 — Nền tảng chung (bắt buộc xong trước khi tách việc)**

| Chung (Anh - PM)                                                                              | IoT (Tường)                                                | AI (Vũ)                                                           | Web (Anh)                                     |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------- | --------------------------------------------- |
| Khởi tạo repo, cấu trúc thư mục, `.gitignore`                                                 | Mua/kiểm tra đủ phần cứng (ESP32, HC-SR04, servo, LED)     | Bắt đầu tổng hợp dataset Roboflow (song song, không phụ thuộc gì) | Setup FastAPI + React skeleton                |
| **Chốt văn bản MQTT topic + JSON format** cho cả 3 loại                                       | Cài Arduino IDE/PlatformIO, test nạp code cơ bản lên ESP32 | Setup môi trường PyTorch + CUDA                                   | Setup PostgreSQL + Alembic, viết migration DB |
| **Chốt luôn tín hiệu "không tự tin"** (khuyến nghị Phương án B — topic riêng) giữa Vũ & Tường |                                                            |                                                                   | Setup Cloudinary                              |
| Cài Mosquitto local + MQTTX cho cả nhóm                                                       |                                                            |                                                                   | Seed dữ liệu mẫu (2 khu vực, 6 thùng)         |

> ⚠️ Đây là tuần **quan trọng nhất về mặt phối hợp** — nếu MQTT contract chưa chốt xong thì tuần 2 cả 3 người dễ code lệch nhau.

---

### **Tuần 2 — Bắt đầu phần lõi kỹ thuật riêng**

| IoT                                                                            | AI                                                                                                | Web                                                        |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Firmware đọc HC-SR04 (test riêng từng cảm biến, đo `H` thực tế cho từng thùng) | Train model YOLOv8n lần đầu (bản v1, chưa cần tối ưu) — **việc tốn thời gian nhất, cần chạy sớm** | Module 1: JWT auth (BE) + trang đăng nhập (FE)             |
| Test riêng servo (mở đúng góc, đóng đúng)                                      | Test đọc luồng camera qua IP Webcam/DroidCam bằng cv2                                             | Bắt đầu Module 2: API `GET /api/khu-vuc`, `/api/thung-rac` |
| Publish thử `d` giả lên MQTT bằng code thật (chưa cần Backend nhận)            |                                                                                                   |                                                            |

---

### **Tuần 3 — Logic xử lý chính**

| IoT                                                   | AI                                                             | Web                                                                   |
| ----------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------- |
| Subscribe `phanloai`, mở đúng servo theo `loai_rac`   | Frame differencing (PA3) — chống nhận nhầm khay trống          | Module 2: MQTT subscriber (mucday, trangthai) → tính % đầy, update DB |
| LED xanh/đỏ cấp zone, timer non-blocking đóng servo   | State machine IDLE → DETECTING → COOLDOWN (vote theo tần suất) | WebSocket server + connection manager                                 |
| Setup LED đỏ riêng, subscribe tín hiệu "không tự tin" | Đánh giá độ chính xác model, retrain nếu cần đạt 80-85%        | FE Dashboard: hiển thị 6 thùng, % đầy, online/offline                 |

---

### **Tuần 4 — Hoàn thiện luồng dữ liệu + ảnh**

| IoT                                                                                                           | AI                                                                             | Web                                                                                                     |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| Test toàn diện: publish `phanloai` giả + tín hiệu "không tự tin" giả bằng MQTTX, kiểm tra ESP32 phản ứng đúng | Case "không tự tin": publish đúng tín hiệu đã chốt tuần 1                      | Module 3: subscribe `phanloai` → tạo `lich_su_phan_loai`; `POST /api/anh-phan-loai` (upload Cloudinary) |
| Chốt LWT cho `trangthai/iot`                                                                                  | Publish `phanloai` thành công: `log_id`, `loai_rac`, `confidence`, `timestamp` | `GET /api/lich-su-phan-loai` (filter, phân trang), `PATCH` xác nhận đúng/sai                            |
|                                                                                                               | POST ảnh async kèm `log_id`, xử lý lỗi mạng (lưu cục bộ)                       | FE: bảng lịch sử, bộ lọc, nút xác nhận                                                                  |
|                                                                                                               | Threading đọc song song 2 camera                                               |                                                                                                         |

---

### **Tuần 5 — Hoàn thiện + chuẩn bị tích hợp**

| IoT                                                                  | AI                                                                    | Web                                                                  |
| -------------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Hoàn thiện toàn bộ firmware, dọn code, test lại end-to-end với MQTTX | Fine-tune model nếu cần, đảm bảo chạy ổn định 2 luồng camera cùng lúc | Module 3 hoàn thiện: batch-delete, upload ảnh thủ công theo `log_id` |
| Chuẩn bị mang thiết bị đi test thật                                  | Test độc lập toàn bộ pipeline (camera → publish → ảnh) trên máy AI    | Module 4: thống kê (`GET /api/thong-ke`), biểu đồ FE                 |
|                                                                      |                                                                       | Test API bằng Postman/Swagger cho toàn bộ endpoint                   |

> Cuối tuần 5 nên có buổi **demo nội bộ riêng từng người** để chắc mỗi phần chạy độc lập ổn trước khi ghép.

---

### **Tuần 6 — Tích hợp thật, giai đoạn 1**

- Setup broker chung (1 máy chạy Mosquitto, mở IP cho cả 3 kết nối — xem file setup-broker-mang-noi-bo)
- Cả 3 người **cùng phòng, cùng WiFi**
- **Ghép luồng mức đầy trước** (đơn giản nhất, dễ debug): ESP32 thật → broker → Backend thật → Dashboard FE thật
- Ghép luồng trạng thái online/offline (LWT)
- Đối chiếu từng message qua MQTTX với format đã chốt, sửa lệch ngay

### **Tuần 7 — Tích hợp thật, giai đoạn 2**

- Ghép luồng phân loại (MQTT trước, chưa kèm ảnh) — AI thật → ESP32 thật (mở servo/LED) → Backend thật (tạo row DB) → FE hiển thị lịch sử
- Ghép tiếp luồng gửi ảnh HTTP (phức tạp nhất, để cuối)
- Ghép luồng tín hiệu "không tự tin" → LED đỏ
- Test toàn bộ pipeline nhận diện thật với rác thật, ghi nhận lỗi phát sinh

### **Tuần 8 — Hoàn thiện & bàn giao**

- Test tại đúng địa điểm demo (mạng, ánh sáng, vị trí đặt thùng thật)
- Fix bug phát sinh từ môi trường thật (khác với test ở nhà)
- Module 6: README, tài liệu API/MQTT contract, ghi chú báo cáo
- Viết báo cáo đồ án, chuẩn bị slide/kịch bản demo
- Buffer dự phòng — luôn có rủi ro phát sinh ở bước tích hợp phần cứng thật

---

## 🎯 Vài lưu ý về thứ tự ưu tiên

1. **Tuần 1 là điểm nghẽn** — nếu MQTT contract + tín hiệu "không tự tin" chưa chốt, mọi thứ sau đó có nguy cơ code sai format, phải sửa lại tốn thời gian gấp đôi.
2. **AI nên bắt đầu train model từ tuần 2**, vì đây là việc mất nhiều thời gian nhất và có độ bất định cao (có thể phải train lại nhiều lần để đạt 80-85%).
3. **Web có thể chạy song song với IoT/AI** nhờ dùng script giả lập publish MQTT (Module 2 có ghi rõ việc này) — không cần đợi 2 bạn kia xong mới bắt đầu.
4. **Đừng dồn tích hợp thật vào 1 tuần cuối** — tài liệu đã nhấn mạnh "ghép từng luồng riêng lẻ, không ghép hết 1 lần", nên cần ít nhất 2 tuần (6-7) cho việc này, tuần 8 chỉ nên là buffer + polish.
