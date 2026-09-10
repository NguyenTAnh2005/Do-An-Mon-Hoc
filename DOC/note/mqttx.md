## MQTTX (hoặc MQTT Explorer, tương tự nhau) hoạt động thế nào và dùng để debug ra sao.

MQTTX là 1 ứng dụng đóng vai trò **"người giả"** — nó tự kết nối vào broker như 1 client bình thường (giống ESP32 hay script AI cũng chỉ là 1 client), nhưng thay vì code tự động, bạn **tự tay** publish hoặc subscribe bằng giao diện, gõ tay nội dung muốn gửi.

## Dùng để làm gì trong dự án của bạn

**1. Kiểm tra chiều publish → subscribe (dễ nhất, dùng nhiều nhất)**

Ví dụ bạn IoT muốn test firmware ESP32 subscribe topic `truong/khu1/phanloai` có nhận đúng và mở đúng servo không — nhưng script AI thật chưa code xong. Thay vì ngồi chờ:

- Mở MQTTX, kết nối vào broker
- Vào ô "Publish", gõ topic: `truong/khu1/phanloai`
- Gõ payload: `{"loai_rac": "huu_co", "do_chac_chan": 0.9, "timestamp": "...", "log_id": "test123"}`
- Bấm gửi → ESP32 (nếu đang chạy, đã subscribe đúng topic) sẽ nhận được y hệt như nhận từ script AI thật, mở servo thùng hữu cơ

→ Đây chính là cách bạn IoT test được firmware của mình **mà không cần chờ AI xong**.

**2. Kiểm tra chiều subscribe (xem ai đó có publish đúng không)**

Ngược lại, nếu bạn AI vừa viết xong đoạn code publish, muốn biết code mình gửi đúng chưa (đúng topic, đúng format JSON) mà chưa cần ESP32/Web chạy để nhận:

- Mở MQTTX, vào ô "Subscribe", gõ topic: `truong/khu1/phanloai` (hoặc dùng `truong/khu1/#` để nghe **tất cả** topic con của khu 1 cùng lúc — dấu `#` là wildcard)
- Chạy script AI thật (hoặc đoạn code publish đang test)
- MQTTX sẽ hiện ra ngay nội dung vừa nhận được, kèm thời gian — nhìn bằng mắt xem JSON có đúng cấu trúc không, có gõ nhầm tên field không (ví dụ `"loai_rac"` mà lỡ gõ `"loairac"`)

## Vì sao hữu ích cho việc bạn (quản lý dự án) theo dõi tiến độ

Bạn có thể tự mở MQTTX, subscribe `truong/#` (nghe hết mọi thứ mọi khu vực), rồi **tự mắt kiểm tra** cả 3 mảng có đang publish đúng format đã thống nhất trong note hay không — mà không cần đọc code của từng người, không cần hỏi "cậu code xong chưa" — chỉ cần nhìn message thực tế chạy qua có khớp văn bản đã chốt hay không.

Đây cũng chính là cách thực hiện **Module 5 (tích hợp thật)** đã bàn trước đó — khi ghép từng luồng, bạn dùng MQTTX để đối chiếu message thật nhận được với format đã thống nhất, phát hiện lệch sớm trước khi ảnh hưởng tới Web hay servo.
