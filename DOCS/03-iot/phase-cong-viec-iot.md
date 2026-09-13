# Danh sách công việc — IoT (Tường)

> **Mục đích file này:** checklist các việc cần làm cho phần IoT, theo thứ tự triển khai hợp lý. Đây là task list, không phải tài liệu thiết kế — xem thiết kế đầy đủ tại [Thiết kế IoT](./thiet-ke-iot.md).

**Setup & kết nối**

- Chọn và xác nhận thư viện MQTT cho ESP32 (ví dụ PubSubClient hoặc tương đương)
- Kết nối Mosquitto, cấu hình LWT cho `trangthai/iot` (retain=true)

**Đo mức đầy**

- Viết firmware đọc cảm biến HC-SR04: đo khoảng cách liên tục cho cả 3 thùng trong 1 khu vực (nên lấy trung bình vài lần đo/lần publish để giảm nhiễu)
- Viết logic publish `d` thô lên topic `mucday/{loai_rac}` riêng từng thùng, theo chu kỳ ~10 giây/lần, QoS 0
- Đo và chốt giá trị `H` (khoảng cách khi thùng rỗng) cho từng thùng thực tế — báo lại cho Web cập nhật vào DB

**Nhận lệnh & điều khiển servo/LED**

- Viết firmware subscribe topic `phanloai` của khu vực mình phụ trách
- Khi nhận `loai_rac` khớp thùng → **tự động mở servo đúng thùng đó** theo field `loai_rac`, đồng thời bật **LED xanh của zone** (chỉ báo "detect thành công", không gắn với thùng nào)
- Dùng timer non-blocking (`millis()`, không `delay()`) để tự đóng servo + tắt LED xanh sau X giây
- Setup thêm 1 **LED đỏ riêng của zone** (chân GPIO độc lập, không chung với LED xanh) → subscribe tín hiệu "không tự tin" từ AI, bật LED đỏ khi nhận được (không mở servo nào)
- Chốt cùng Vũ định dạng chính xác của tín hiệu "không tự tin" (topic/field) trước khi code phần subscribe này

**Test**

- Test riêng từng cảm biến (đo đúng khoảng cách, không nhiễu quá nhiều) trước khi ghép chung cả 3 thùng
- Test riêng servo (mở đúng góc, đóng lại đúng) trước khi ghép với MQTT
- Test riêng LED đỏ/xanh phản ứng đúng tín hiệu trước khi ghép với AI thật
- Test độc lập: publish thử `d` giả, publish thử `phanloai` giả và tín hiệu "không tự tin" giả bằng MQTTX/mosquitto_pub, không cần đợi AI/Web hoàn thiện hết
