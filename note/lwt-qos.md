## LWT (Last Will and Testament)

**Vấn đề nó giải quyết**: Bình thường, nếu ESP8266 mất điện đột ngột, rớt WiFi, hoặc bị hỏng — nó không kịp gửi tín hiệu gì báo cho biết. Từ phía web, bạn chỉ thấy... im lặng. Không biết là thiết bị đang offline, hay đang online nhưng không có sự kiện gì để gửi (2 trạng thái này nhìn giống hệt nhau nếu không có cơ chế báo hiệu).

**Cách LWT hoạt động**: Đây là tính năng có sẵn trong giao thức MQTT (không phải bạn tự code logic phát hiện mất kết nối). Khi ESP8266 **kết nối** tới broker (Mosquitto), nó gửi kèm một "di chúc" — dặn trước broker rằng: _"Nếu sau này tôi rớt kết nối bất ngờ (không phải tôi chủ động disconnect đàng hoàng), hãy tự động publish giúp tôi message này lên topic `status`."_

```
Ví dụ lúc ESP8266 connect tới broker:
  LWT topic: nhom/esp01/status
  LWT message: "offline"
  LWT retain: true
```

Từ đó, broker **theo dõi liên tục** kết nối TCP với ESP8266 (qua cơ chế keep-alive/ping định kỳ). Nếu quá thời gian keep-alive mà không thấy phản hồi từ ESP8266 (tức là rớt mạng, hỏng, mất điện — bất kỳ lý do gì khiến kết nối chết đột ngột mà không kịp "chào tạm biệt"), **broker tự động publish** message "offline" đó lên topic `status` — hộ ESP8266, dù ESP8266 lúc đó đã "chết" không làm gì được nữa.

Web app của bạn chỉ cần **subscribe** vào topic `nhom/esp01/status`, thấy giá trị đổi thành `"offline"` là biết ngay thiết bị có vấn đề — không cần đợi timeout tự đoán, không cần polling liên tục hỏi "còn sống không".

Ngược lại, khi ESP8266 connect thành công, nó publish `"online"` lên chính topic đó (đây là bạn tự code, không phải LWT tự làm) — nên topic `status` luôn phản ánh đúng trạng thái thật.

## QoS (Quality of Service)

Đây là mức độ **đảm bảo message có tới nơi hay không**, mỗi lần publish/subscribe bạn chọn 1 trong 3 mức:

| QoS   | Cơ chế                                        | Đảm bảo                                                       | Chi phí              |
| ----- | --------------------------------------------- | ------------------------------------------------------------- | -------------------- |
| **0** | Gửi 1 lần, không xác nhận ("fire and forget") | Có thể mất message, không báo lỗi                             | Nhẹ nhất, nhanh nhất |
| **1** | Gửi kèm ID, chờ broker ACK (xác nhận đã nhận) | Chắc chắn tới ít nhất 1 lần (có thể trùng lặp nếu ACK bị mất) | Trung bình           |
| **2** | Bắt tay 4 bước (handshake) đảm bảo đúng 1 lần | Chắc chắn tới đúng 1 lần, không trùng                         | Nặng nhất            |

Trong hệ thống của nhóm bạn:

- **QoS 0 cho dữ liệu cảm biến** (khoảng cách đo liên tục, VD gửi mỗi giây): nếu mất 1 gói giữa chừng thì gói tiếp theo (1 giây sau) vẫn tới, không ảnh hưởng gì — data này có tính chất "cập nhật liên tục", mất 1 điểm dữ liệu không sao, đổi lại tốc độ nhanh, ít tốn tài nguyên ESP8266 (con chip yếu, không nên bắt nó xử lý ACK phức tạp cho luồng dữ liệu dồn dập).

- **QoS 1 cho lệnh cảnh báo** (VD "bật còi", "bật đèn đỏ" khi phát hiện nguy hiểm): đây là message **rời rạc, quan trọng** — nếu mất gói này, còi không kêu, mất luôn ý nghĩa cảnh báo (khác với sensor data có gói kế tiếp bù lại ngay). Nên cần broker đảm bảo message chắc chắn được ESP8266 nhận (broker sẽ gửi lại nếu chưa nhận ACK).

QoS 2 thường **không cần dùng** cho đồ án cỡ này — độ nặng xử lý cao trong khi lợi ích "không trùng lặp tuyệt đối" không quá cần thiết ở đây (kể cả còi kêu 2 lần do trùng lặp QoS 1 cũng không gây hại gì nghiêm trọng).

## QoS dùng cho cái gì

QoS là thuộc tính gắn vào **mỗi lần publish hoặc subscribe một message**, không phải cấu hình cố định cho cả kết nối. Mỗi khi ESP8266 gọi hàm publish, nó chọn QoS 0/1/2 cho message đó — nghĩa là bạn có thể vừa publish sensor data QoS 0, vừa publish lệnh cảnh báo QoS 1, trên cùng một kết nối MQTT, chỉ khác tham số truyền vào lúc gọi hàm publish. Ví dụ code Arduino:

```cpp
mqttClient.publish("nhom/esp01/khoangcach", "45", false);  // QoS mặc định 0 trong nhiều thư viện, hoặc set riêng
mqttClient.publish("nhom/esp01/canhbao_coi", "on", true, 1); // QoS 1
```

Nói cách khác: QoS trả lời câu hỏi _"message NÀY quan trọng tới mức nào, cần đảm bảo tới nơi ra sao"_ — chọn theo từng loại dữ liệu, không phải chọn 1 lần cho toàn hệ thống.

## Broker có phải chỉ là nơi lưu trữ biến không

Không hẳn — cần phân biệt 2 vai trò của broker:

1. **Vai trò chính (mặc định)**: broker là trạm trung chuyển **tức thời**, không lưu trữ. Khi A publish message lên topic X, broker chỉ chuyển tiếp message đó cho các client đang subscribe topic X **tại đúng thời điểm đó**. Nếu không có ai subscribe lúc message tới, message bị mất luôn — broker không giữ lại để phát cho người subscribe sau.

2. **Retain flag** (bạn thấy trong LWT ở trên) là ngoại lệ: khi publish kèm `retain: true`, broker **mới** giữ lại giá trị mới nhất của message đó cho riêng topic này. Sau đó, bất kỳ client nào subscribe vào topic đó — dù kết nối muộn cỡ nào — sẽ **lập tức nhận được ngay giá trị retain gần nhất**, không cần đợi có publish mới. Đây chính là lý do LWT cần đi kèm `retain: true`.

## Cơ chế LWT hoạt động chi tiết — vì sao broker biết ESP8266 chết

Bản chất kết nối MQTT chạy trên TCP, và có một cơ chế gọi là **keep-alive**: khi ESP8266 connect, nó khai báo với broker một khoảng thời gian keep-alive (VD 60 giây), nghĩa là _"tôi cam kết, dù không có gì để publish, tối đa 60 giây tôi sẽ gửi 1 gói PINGREQ (ping) để báo tôi vẫn còn sống"_.

Diễn biến cụ thể:

1. ESP8266 connect tới Mosquitto, gửi kèm gói CONNECT có chứa thông tin LWT (topic `status`, message `"offline"`, retain `true`) + keep-alive 60s.
2. Broker lưu lại "di chúc" này trong bộ nhớ, gắn với session của riêng ESP8266 đó.
3. ESP8266 hoạt động bình thường — publish sensor data, hoặc nếu im lặng quá 60s thì tự gửi ping.
4. **Trường hợp mất điện/rớt WiFi đột ngột**: ESP8266 không kịp gửi DISCONNECT đàng hoàng (đó là cách "ngắt kết nối lịch sự" — nếu ESP8266 chủ động gọi disconnect(), LWT sẽ KHÔNG được kích hoạt, vì đây coi là ngắt có chủ đích, không phải sự cố).
5. Broker chờ hết khoảng keep-alive (thường nhân đôi lên ~1.5x làm buffer, tức khoảng 90s với keep-alive 60s) mà không thấy ping/message nào từ ESP8266 → kết luận kết nối đã chết bất thường → **tự động publish** message "offline" (retain=true) lên topic `status`, thay mặt ESP8266.

Vậy "phát hiện" ở đây không phải broker "dò" gì cả — nó chỉ đơn giản là đợi hết thời gian keep-alive không thấy tín hiệu, rồi thực hiện đúng lời dặn đã lưu sẵn từ lúc connect.

## Mục đích cho dự án cụ thể

Web app của bạn chỉ cần làm 1 việc: **subscribe** vào topic `nhom/esp01/status`. Khi giá trị nhận được đổi từ `"online"` → `"offline"`, web hiển thị badge đỏ "Thiết bị mất kết nối" ở phần "Trạng thái thiết bị IoT" (mục 6 trong note của bạn) — mà không cần code thêm bất kỳ cơ chế polling hay timeout riêng nào ở phía web. MQTT/broker tự lo hết phần "phát hiện mất kết nối", web chỉ việc lắng nghe và hiển thị.

Nếu không có LWT, bạn sẽ phải tự chế cơ chế: VD web tự đếm "quá X giây không nhận được message nào từ thiết bị thì coi là offline" — cách này kém chính xác hơn (dễ báo sai nếu đơn giản là không có sự kiện gì để gửi trong thời gian dài, dù thiết bị vẫn sống bình thường).
