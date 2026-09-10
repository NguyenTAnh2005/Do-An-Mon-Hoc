# AI

- Tổng hợp dataset trên Roboflow Universe (fork dataset phù hợp 3 lớp: tái chế / hữu cơ / vô cơ)
- Train model YOLOv8n, fine-tune từ dataset đã tổng hợp
- Đánh giá độ chính xác model, mục tiêu 80–85%
- Test nhận diện với cv2, đọc luồng camera qua IP Webcam/DroidCam
- Nghiên cứu cơ chế chọn frame: khi stream, chỉ lấy 1 frame có độ tin cậy cao nhất trong 1 khoảng thời gian, chuyển thành ảnh, lưu tạm bằng Python
- Viết logic publish MQTT: gửi `loai_rac`, `do_chac_chan`, `timestamp`, `log_id` (tự sinh uuid) lên đúng topic `phanloai` của khu vực
- Viết logic gửi ảnh: encode frame (`cv2.imencode`), gọi HTTP POST `multipart/form-data` tới endpoint `/api/anh-phan-loai` của Web, kèm `log_id`
- Setup MQTT client (paho-mqtt) trong script AI: kết nối broker, cấu hình LWT cho topic `trangthai/ai` (tự publish "online" khi kết nối, để broker tự gửi "offline" khi rớt kết nối đột ngột)
- Viết threading để đọc song song 2 luồng camera (2 khu vực) trong cùng 1 script, chạy trên 1 máy
- Test độc lập: publish thử lên broker local + gửi ảnh thử tới 1 endpoint giả (hoặc endpoint thật của Web nếu đã có), không cần đợi Web hoàn thiện hết
