# IoT

- Chọn và xác nhận thư viện MQTT cho ESP32 (ví dụ PubSubClient hoặc tương đương)
- Viết firmware đọc cảm biến HC-SR04: đo khoảng cách liên tục cho cả 3 thùng trong 1 khu vực
- Viết logic publish khoảng cách thô (`distance_cm`) lên đúng topic `mucday/{loai_rac}` riêng từng thùng, theo chu kỳ đã thống nhất (~10 giây/lần)
- Viết firmware subscribe topic `phanloai` của khu vực — nhận kết quả phân loại, xác định đúng thùng tương ứng
- Viết logic điều khiển servo: mở đúng ngăn thùng theo nhãn `loai_rac` nhận được, đóng lại sau 1 khoảng thời gian cố định
- Setup MQTT client trên ESP32: kết nối broker, cấu hình LWT cho topic `trangthai/iot` (publish "online" khi kết nối, broker tự gửi "offline" khi rớt kết nối)
- Test riêng từng cảm biến (đo đúng khoảng cách, không nhiễu quá nhiều) trước khi ghép chung cả 3 thùng
- Test riêng servo (mở đúng góc, đóng lại đúng) trước khi ghép với MQTT
- Đo và chốt giá trị `H` (khoảng cách khi thùng rỗng) cho từng thùng thực tế — giá trị này Web cần để tính %, nên đo xong phải báo lại để Web cập nhật vào DB
- Test độc lập: publish thử khoảng cách giả lên broker local, subscribe thử topic phanloai giả (dùng công cụ MQTT Explorer để publish tay), không cần đợi AI/Web hoàn thiện hết
