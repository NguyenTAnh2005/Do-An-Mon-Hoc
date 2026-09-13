# Thiết kế phần cứng & firmware IoT (Người phụ trách: Tường)

> **Mục đích file này:** đặc tả kỹ thuật đầy đủ cho phần IoT — cơ chế đo mức đầy, điều khiển servo, logic LED (LED chỉ báo hiệu detect thành công/thất bại, không gắn theo thùng cụ thể), topic MQTT liên quan. Đây là tài liệu bàn giao chính cho Tường.

Liên quan: [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) · [Luồng mức đầy & trạng thái online](../02-luong-xu-ly/luong-mucday-trangthai-online.md) · [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md) · [Danh sách công việc IoT](./phase-cong-viec-iot.md)

---

## 1. Tổng quan phạm vi

- Toàn hệ thống có **2 khu vực (zone)**, mỗi khu vực có **3 thùng rác**: tái chế / hữu cơ / vô cơ.
- Mỗi khu vực: **1 ESP32** duy nhất điều khiển cả 3 thùng.
- Mỗi thùng gồm:
  - 1 cảm biến siêu âm **HC-SR04** (đo mức đầy)
  - 1 **servo** (mở/đóng nắp thùng — servo tự động mở đúng ngăn dựa theo `loai_rac` nhận được qua MQTT, không cần LED nào báo hiệu theo thùng)
- Mỗi khu vực có thêm **2 LED cấp zone** (không gắn theo thùng cụ thể nào):
  - **LED xanh**: báo hiệu AI **detect/phân loại thành công** (bất kể là loại rác gì — servo đã tự lo việc mở đúng ngăn)
  - **LED đỏ**: báo hiệu AI **không đủ tự tin** để phân loại
  - 2 LED này độc lập hoàn toàn với nhau (không dùng chung chân/module), và đều **không liên quan tới thùng cụ thể nào** — chỉ đơn thuần là tín hiệu "detect được hay không" cho người đứng trước camera biết
- Mỗi khu vực còn có **1 smartphone làm IP camera** (IP Webcam/DroidCam) — thuộc luồng AI, không do ESP32 xử lý, nhưng Tường cần biết để lắp camera đúng góc nhìn thấy cả 3 thùng.

**Nguyên tắc quan trọng: ESP32 KHÔNG tính toán nghiệp vụ.** ESP32 chỉ đọc cảm biến, gửi dữ liệu thô, và thực thi lệnh (mở nắp, bật LED) khi nhận lệnh từ MQTT. Mọi phép tính (% đầy) do Backend đảm nhiệm — giữ firmware đơn giản, dễ debug, dễ maintain.

---

## 2. Đo mức đầy (Fill Level)

### 2.1 Cơ chế

- HC-SR04 đặt ở nắp thùng, đo khoảng cách `d` (cm) từ cảm biến đến mặt rác.
- ESP32 **chỉ gửi giá trị `d` thô** lên MQTT — không tự tính %.
- Backend tính % đầy theo công thức: `%đầy = (H - d) / H × 100`, trong đó `H` = chiều cao thùng (cm), cấu hình sẵn trong DB (`thung_rac.chieu_cao_H_cm`), không do ESP32 gửi.

### 2.2 Tần suất gửi

- Mỗi thùng publish `d` thô định kỳ, khoảng **mỗi 10 giây/lần**.
- QoS = **0** (mất một lần không quan trọng, 10s sau có bản mới).

### 2.3 Việc cần làm (Tường)

- Đọc HC-SR04 theo chu kỳ ổn định (lấy trung bình vài lần đo/lần publish để giảm sai số).
- Publish `d` (cm) lên đúng topic của từng thùng.
- Không cần validate hay tính %, không cần biết `H` — đó là việc của Backend.

---

## 3. Servo — mở nắp thùng

- Servo mở nắp khi ESP32 **nhận lệnh MQTT phân loại (`phanloai`)** khớp với thùng của nó — hoàn toàn tự động dựa vào `loai_rac` trong payload, không phụ thuộc LED.
- Đồng thời với việc mở servo, ESP32 cũng bật **LED xanh của zone** (mục 4) — nhưng đây là 2 hành động chạy song song, không phải LED "quyết định" thùng nào mở; servo tự biết mở đúng ngăn qua field `loai_rac`, còn LED xanh chỉ đơn thuần báo "đã detect thành công".
- Sau một khoảng thời gian hợp lý (Tường tự định nghĩa, vd 3–5s), servo đóng lại về vị trí ban đầu.

---

## 4. LED phản hồi — chỉ báo "detect được hay không", không liên quan thùng cụ thể

**Quyết định đã chốt:** LED xanh và LED đỏ **đều là tín hiệu cấp zone, không gắn theo thùng cụ thể nào**. Chúng chỉ trả lời đúng 1 câu hỏi cho người đứng trước camera: *"hệ thống có detect/phân loại được không?"* — còn việc mở đúng ngăn thùng nào là do **servo tự động xử lý** dựa vào field `loai_rac` trong MQTT, hoàn toàn độc lập với 2 LED này. 2 LED cũng độc lập với nhau, không dùng chung chân GPIO hay module.

| Trạng thái                                      | Khi nào xảy ra                                                                                                                                                                    | LED nào bật                          | Servo                          | Có ghi vào DB không? |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- | --------------------------------- | ----------------------- |
| **Thành công**                                    | ESP32 nhận MQTT `phanloai` có `loai_rac` khớp với thùng của nó                                                                                                                    | **LED xanh của zone** (báo detect OK)   | Tự động mở đúng thùng theo `loai_rac` | Có                    |
| **Không tự tin (cần phân loại thủ công)**         | AI kết thúc cửa sổ nhận diện (DETECTING) mà không có class nào đạt ngưỡng xuất hiện tối thiểu → AI publish tín hiệu "không tự tin" riêng                                          | **LED đỏ của zone** (báo detect fail)   | Không mở gì cả                     | **Không**             |
| **Không phát hiện gì (miss_count vượt ngưỡng)**   | AI huỷ phiên nhận diện, quay về IDLE, **không publish gì cả**                                                                                                                     | **Không LED nào cả** — hành vi bình thường, không phải lỗi | Không mở gì cả | Không                 |

Ý nghĩa với người dùng: LED xanh sáng = yên tâm rác đã được phân loại và đúng ngăn đã tự mở; LED đỏ sáng = hệ thống không chắc chắn, **tự phân loại thủ công**, không có ngăn nào tự mở.

→ Lưu ý cho Tường: ESP32 **không tự quyết định** khi nào bật LED đỏ/xanh hay mở servo nào — toàn bộ đều là phản ứng theo tín hiệu MQTT nhận từ AI. ESP32 đóng vai trò "thi hành lệnh", không phải "ra quyết định". Việc bật LED xanh và việc mở đúng servo là **2 phản ứng độc lập cho cùng 1 message `phanloai`**, không phụ thuộc lẫn nhau.

**Về mạch/dây:** mỗi ESP32 cần quản lý 3 servo (theo thùng) + 2 LED (1 xanh + 1 đỏ, cấp zone, không theo thùng) trên các chân GPIO riêng biệt, cộng với chân đọc HC-SR04 (có thể multiplex qua 1 số chân nếu dùng thư viện đo tuần tự). Tổng số LED giảm đáng kể so với phương án cũ (không cần 6 LED xanh riêng theo từng thùng nữa).

**Định dạng tín hiệu "không tự tin" trên MQTT vẫn cần chốt cụ thể (topic/field nào)** — xem [đề xuất tạm trong MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md#tín-hiệu-không-tự-tin-đề-xuất---cần-chốt), cần Vũ và Tường thống nhất trước khi code phần subscribe LED đỏ.

**Về buzzer/loa (định hướng mở rộng, chưa bắt buộc cho v1):** buzzer đơn giản dùng `tone()` phát nhịp/tần số khác nhau theo loại rác là khả thi ngay trong v1; loa phát giọng nói thật cần thêm module DFPlayer Mini, để dành hướng phát triển tương lai.

---

## 5. Topic MQTT liên quan đến IoT

### 5.1 `truong/khu{n}/mucday/{loai_rac}`

- **Chiều:** ESP32 → Broker (publish)
- **Nội dung:** giá trị `d` thô (cm)
- **QoS:** 0
- **Tần suất:** ~10 giây/lần/thùng
- **Lưu ý:** `{loai_rac}` phải khớp chính xác enum trong DB (`tai_che` / `huu_co` / `vo_co`), viết đúng chính tả không dấu, không viết tắt khác.

### 5.2 `truong/khu{n}/trangthai/iot`

- **Chiều:** ESP32 → Broker (publish, dùng cơ chế **LWT**)
- **Mục đích:** Backend theo dõi ESP32 của khu vực này còn online hay không, độc lập với trạng thái AI (2 cờ riêng: `iot_online`, `ai_online`).
- **QoS:** 1
- **Cách hoạt động LWT:** khi ESP32 connect MQTT, đăng ký "di chúc" — nếu kết nối bị ngắt đột ngột mà không disconnect đúng cách, broker tự publish payload "offline" thay ESP32. Khi hoạt động bình thường, ESP32 publish "online" định kỳ hoặc ngay sau connect.
- **Việc cần làm (Tường):** cấu hình LWT ngay trong bước `client.connect()` của thư viện MQTT (PubSubClient hay tương đương) — tính năng có sẵn của giao thức MQTT, không phải tự viết logic.

### 5.3 `truong/khu{n}/phanloai` (subscribe)

- **Chiều:** Broker → ESP32 (subscribe)
- Xem đầy đủ format tại [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md).

---

## 6. Những gì Tường KHÔNG cần lo (để tránh nhầm phạm vi)

- Không cần tính % đầy — chỉ gửi `d` thô.
- Không cần biết chiều cao `H` của thùng — nằm trong DB, Backend dùng.
- Không cần lưu lịch sử, không cần biết ảnh, không cần gọi API HTTP nào — ESP32 chỉ giao tiếp qua MQTT.
- Không cần xử lý buzzer/âm thanh — đã bị loại khỏi scope v1.
- Không cần logic AI/nhận diện — chỉ nhận kết quả cuối cùng qua MQTT và phản ứng (mở nắp + LED).

---

## 7. Checklist bàn giao cho Tường (tóm tắt kỹ thuật, không phải task tracking)

1. Kết nối ESP32 với Mosquitto broker, cấu hình LWT cho topic `trangthai/iot`.
2. Đọc HC-SR04 cho cả 3 thùng, publish `d` thô lên `mucday/{loai_rac}` mỗi ~10s, QoS 0.
3. Subscribe topic `phanloai` của khu vực mình phụ trách.
4. Khi nhận `phanloai` khớp `loai_rac` của một thùng cụ thể → mở servo đúng thùng đó (tự động theo field `loai_rac`) + bật LED xanh của zone (báo detect thành công), đồng thời — 2 việc độc lập, không phụ thuộc nhau.
5. Setup thêm 1 LED đỏ riêng cho zone (chân GPIO độc lập, không chung với LED xanh) → subscribe tín hiệu "không tự tin" từ Vũ, bật LED đỏ khi nhận được (không mở servo nào cả).
6. Xác nhận với Vũ format cụ thể của tín hiệu "không tự tin" (topic/field nào).
7. Test độc lập: giả lập publish MQTT bằng tay (MQTTX hoặc mosquitto_pub) để kiểm tra ESP32 phản ứng đúng trước khi tích hợp với AI thật.
