## 🧠 AI/CNN (Vũ)

**Dataset & model**

- [ ] Tổng hợp dataset trên Roboflow Universe (3 lớp: tái chế/hữu cơ/vô cơ)
- [ ] Train YOLOv8n từ dataset (setup PyTorch + CUDA nếu cần)
- [ ] Đánh giá độ chính xác, mục tiêu 80–85%
- [ ] Test nhận diện với cv2, đọc luồng camera qua IP Webcam/DroidCam
- [ ] Viết threading đọc song song 2 luồng camera (2 khu vực) trên 1 máy

**Lớp lọc trước — frame differencing (PA3)**

- [ ] Chụp ảnh nền khay trống làm mốc so sánh
- [ ] So sánh mỗi frame với ảnh nền, chỉ cho qua YOLO khi vượt ngưỡng khác biệt

**State machine IDLE → DETECTING → COOLDOWN**

- [ ] `IDLE`: chạy YOLO mỗi frame đã lọc, ngưỡng confidence tối thiểu để chuyển `DETECTING`
- [ ] `DETECTING`: cửa sổ ~1.5s, đếm tần suất class (Counter), giữ frame confidence cao nhất theo từng class
- [ ] `miss_count`: vượt ngưỡng → huỷ phiên về `IDLE`, không publish gì
- [ ] Chốt kết quả: class thắng = tần suất nhiều nhất; ảnh lưu = confidence cao nhất **trong nhóm class thắng**
- [ ] Case không class nào đạt ngưỡng → publish tín hiệu "không tự tin" (không kèm `log_id`/`loai_rac`) — format chốt cùng Tường
- [ ] `COOLDOWN`: nghỉ cố định vài giây rồi về `IDLE`

**Publish & gửi ảnh (case thành công)**

- [ ] Publish `phanloai`: `log_id` (UUID tự sinh), `loai_rac`, `confidence`, `timestamp`
- [ ] POST ảnh multipart tới Web kèm `log_id`, chạy async không chặn camera loop
- [ ] Lỗi mạng khi POST → lưu ảnh + metadata cục bộ theo `log_id`

**MQTT client**

- [ ] Setup paho-mqtt, LWT cho `trangthai/ai`

**Test**

- [ ] Test độc lập publish + gửi ảnh tới endpoint giả/thật
- [ ] Test riêng tín hiệu "không tự tin" bằng MQTTX trước khi ghép ESP32 thật

---
