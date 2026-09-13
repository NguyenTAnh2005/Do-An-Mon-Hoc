# Danh sách công việc — AI/CNN (Vũ)

> **Mục đích file này:** checklist các việc cần làm cho phần AI, theo thứ tự triển khai hợp lý. Logic chi tiết (state machine, format publish) xem tại [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md).

**Dataset & model**

- Tổng hợp dataset trên Roboflow Universe (fork dataset phù hợp 3 lớp: tái chế / hữu cơ / vô cơ)
- Train model YOLOv8n từ dataset đã tổng hợp — xem [cài đặt PyTorch GPU](./cai-dat-pytorch-gpu.md) nếu cần setup lại môi trường
- Đánh giá độ chính xác model, mục tiêu 80–85%
- Test nhận diện với cv2, đọc luồng camera qua IP Webcam/DroidCam
- Viết threading để đọc song song 2 luồng camera (2 khu vực) trong cùng 1 script, chạy trên 1 máy

**Lớp lọc trước — frame differencing (PA3)**

- Chụp ảnh nền khay trống làm mốc so sánh
- Mỗi frame: so sánh với ảnh nền, chỉ cho qua YOLO khi độ khác biệt vượt ngưỡng

**State machine `IDLE → DETECTING → COOLDOWN`**

- `IDLE`: chạy YOLO mỗi frame đã qua lớp lọc, ngưỡng confidence tối thiểu để chuyển `DETECTING`
- `DETECTING`: cửa sổ tích lũy ~1.5s, dùng Counter đếm tần suất class qua các frame, giữ frame confidence cao nhất theo từng class
- `miss_count`: đếm frame liên tiếp mất object, vượt ngưỡng → huỷ phiên về `IDLE`, không publish gì
- Chốt kết quả: class thắng = tần suất nhiều nhất; ảnh lưu = frame confidence cao nhất **trong nhóm class thắng**
- Case không class nào đạt ngưỡng tối thiểu → **publish tín hiệu "không tự tin"** (không kèm `log_id`, không kèm `loai_rac`) — format cần chốt cùng Tường, xem [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md)
- `COOLDOWN`: nghỉ cố định vài giây, không detect, rồi về `IDLE`

**Publish & gửi ảnh (case phân loại thành công)**

- Publish `phanloai`: `log_id` (uuid tự sinh), `loai_rac`, `confidence`, `timestamp`
- POST ảnh multipart tới Web kèm `log_id`, chạy async không chặn camera loop
- Lỗi mạng khi POST → lưu ảnh + metadata cục bộ theo `log_id`

**MQTT client**

- Setup paho-mqtt, LWT cho `trangthai/ai`

**Test**

- Test độc lập publish + gửi ảnh tới endpoint giả/thật, không cần đợi Web hoàn thiện
- Test riêng tín hiệu "không tự tin" bằng MQTTX trước khi ghép với ESP32 thật
