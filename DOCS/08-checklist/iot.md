## 📡 IoT (Tường)

**Setup & kết nối**

- [ ] Chọn thư viện MQTT cho ESP32 (PubSubClient hoặc tương đương)
- [ ] Kết nối Mosquitto, cấu hình LWT cho `trangthai/iot` (retain=true)

**Đo mức đầy**

- [ ] Viết firmware đọc HC-SR04 cho cả 3 thùng/zone (lấy trung bình vài lần đo để giảm nhiễu)
- [ ] Publish `d` thô lên `mucday/{loai_rac}` mỗi ~10s, QoS 0
- [ ] Đo & chốt giá trị `H` (khoảng cách khi thùng rỗng) cho từng thùng thực tế → báo Web cập nhật DB

**Nhận lệnh & điều khiển servo/LED**

- [ ] Subscribe topic `phanloai` của khu vực mình phụ trách
- [ ] Khi nhận `loai_rac` khớp → mở servo đúng thùng + bật LED xanh của zone
- [ ] Dùng timer non-blocking (`millis()`) để tự đóng servo + tắt LED xanh sau X giây
- [ ] Setup LED đỏ riêng (chân GPIO độc lập) → subscribe tín hiệu "không tự tin", bật khi nhận được
- [ ] Chốt cùng Vũ định dạng chính xác tín hiệu "không tự tin" trước khi code phần subscribe

**Test**

- [ ] Test riêng từng cảm biến (đo đúng khoảng cách, ít nhiễu)
- [ ] Test riêng servo (mở đúng góc, đóng đúng)
- [ ] Test riêng LED đỏ/xanh phản ứng đúng tín hiệu
- [ ] Test độc lập bằng MQTTX/mosquitto_pub (publish `d` giả, `phanloai` giả, tín hiệu "không tự tin" giả) — không cần đợi AI/Web xong
