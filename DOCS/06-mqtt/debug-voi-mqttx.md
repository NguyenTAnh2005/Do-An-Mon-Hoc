# Debug MQTT bằng MQTTX

> **Mục đích file này:** hướng dẫn dùng MQTTX (hoặc MQTT Explorer, tương tự) để test/debug từng luồng MQTT độc lập mà không cần chờ các mảng khác code xong.

Liên quan: [Setup broker mạng nội bộ](./setup-broker-mang-noi-bo.md) · [MQTT topic & JSON format](./mqtt-topic-va-json-format.md)

---

## Nguyên lý hoạt động

MQTTX là 1 ứng dụng đóng vai trò **"người giả"** — nó tự kết nối vào broker như 1 client bình thường (giống ESP32 hay script AI cũng chỉ là 1 client), nhưng thay vì code tự động, bạn **tự tay** publish hoặc subscribe bằng giao diện, gõ tay nội dung muốn gửi.

## Dùng để làm gì trong dự án

**1. Kiểm tra chiều publish → subscribe (dễ nhất, dùng nhiều nhất)**

Ví dụ Tường (IoT) muốn test firmware ESP32 subscribe topic `truong/khu1/phanloai` có nhận đúng và mở đúng servo không — nhưng script AI thật chưa code xong. Thay vì ngồi chờ:

- Mở MQTTX, kết nối vào broker
- Vào ô "Publish", gõ topic: `truong/khu1/phanloai`
- Gõ payload: `{"loai_rac": "huu_co", "do_chac_chan": 0.9, "timestamp": "...", "log_id": "test123"}`
- Bấm gửi → ESP32 (nếu đang chạy, đã subscribe đúng topic) sẽ nhận được y hệt như nhận từ script AI thật, mở servo thùng hữu cơ

→ Đây chính là cách Tường test được firmware của mình **mà không cần chờ AI xong**. Tương tự có thể giả lập tín hiệu "không tự tin" để test LED đỏ trước khi AI code xong phần đó.

**2. Kiểm tra chiều subscribe (xem ai đó có publish đúng không)**

Ngược lại, nếu Vũ (AI) vừa viết xong đoạn code publish, muốn biết code mình gửi đúng chưa (đúng topic, đúng format JSON) mà chưa cần ESP32/Web chạy để nhận:

- Mở MQTTX, vào ô "Subscribe", gõ topic: `truong/khu1/phanloai` (hoặc dùng `truong/khu1/#` để nghe **tất cả** topic con của khu 1 cùng lúc — dấu `#` là wildcard)
- Chạy script AI thật (hoặc đoạn code publish đang test)
- MQTTX sẽ hiện ra ngay nội dung vừa nhận được, kèm thời gian — nhìn bằng mắt xem JSON có đúng cấu trúc không, có gõ nhầm tên field không (ví dụ `"loai_rac"` mà lỡ gõ `"loairac"`)

## Vì sao hữu ích cho việc theo dõi tiến độ (PM)

Có thể tự mở MQTTX, subscribe `truong/#` (nghe hết mọi thứ mọi khu vực), rồi **tự mắt kiểm tra** cả 3 mảng có đang publish đúng format đã thống nhất hay không — mà không cần đọc code của từng người, không cần hỏi "cậu code xong chưa" — chỉ cần nhìn message thực tế chạy qua có khớp văn bản đã chốt hay không.

Đây cũng chính là cách thực hiện bước **tích hợp thật** ([Module 5 của Web](../05-web/phase-cong-viec-web.md#module-5--kiểm-thử--tích-hợp-thật-xuyên-suốt-không-tách-befe)) — khi ghép từng luồng, dùng MQTTX để đối chiếu message thật nhận được với format đã thống nhất, phát hiện lệch sớm trước khi ảnh hưởng tới Web hay servo.
