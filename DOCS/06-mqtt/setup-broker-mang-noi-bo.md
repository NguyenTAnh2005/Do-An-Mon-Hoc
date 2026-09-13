# Setup MQTT broker dùng chung khi tích hợp thật

> **Mục đích file này:** hướng dẫn cấu hình Mosquitto để 3 máy (Web, AI, IoT/ESP32) kết nối chung 1 broker qua mạng nội bộ, thay vì mỗi người tự chạy `localhost` riêng khi test.

Liên quan: [Danh sách công việc chung](../07-quy-trinh-nhom/phase-cong-viec-chung.md) · [Debug MQTT bằng MQTTX](./debug-voi-mqttx.md)

---

## Bản chất

Nếu bạn là người chạy Mosquitto (ví dụ chạy ngay trên laptop bạn), thì:

- 2 bạn kia chỉ cần biết **địa chỉ IP máy bạn** + **port 1883** (port mặc định của MQTT)
- Trong code của họ (ESP32 dùng PubSubClient, script AI dùng paho-mqtt), chỗ cấu hình kết nối broker sẽ trỏ tới `địa_chỉ_ip_của_bạn:1883` thay vì `localhost:1883` như lúc tự test riêng

## Điều kiện cần thêm để kết nối được thật

**1. Tất cả phải cùng 1 mạng (cùng WiFi/hotspot)**

MQTT ở đây chạy trên mạng nội bộ (local network), không phải public internet. Máy bạn, laptop AI, ESP32 (qua wifi) đều phải nằm chung 1 mạng. Nếu 3 người ở 3 chỗ khác nhau dùng mạng nhà riêng, sẽ **không kết nối được** trừ khi có thêm bước public broker ra internet (phức tạp hơn, không cần thiết cho đồ án).

→ **Việc "tích hợp thật" gần như bắt buộc phải làm khi cả nhóm ngồi cùng chỗ** (cùng phòng, cùng wifi).

**2. Mosquitto mặc định có thể chỉ lắng nghe `localhost`, cần cấu hình mở ra mạng ngoài**

Nếu cài Mosquitto mà không chỉnh gì, có thể nó chỉ nhận kết nối từ chính máy nó (`127.0.0.1`), từ chối kết nối từ máy khác trong mạng. Cần sửa file cấu hình (`mosquitto.conf`), thêm:

```
listener 1883 0.0.0.0
allow_anonymous true
```

(`allow_anonymous true` — vì đồ án không cần thiết lập user/password cho broker, cho phép ai cũng kết nối được trong phạm vi mạng nội bộ đó)

**3. Firewall của máy bạn có thể chặn kết nối tới port 1883**

Windows/macOS đôi khi chặn kết nối từ máy lạ vào port ứng dụng mới cài — cần mở port 1883 trong firewall, hoặc set về "cho phép trong mạng riêng tư" khi hệ điều hành hỏi lúc mở Mosquitto lần đầu.

**4. Địa chỉ IP máy bạn có thể đổi**

Địa chỉ IP nội bộ (dạng `192.168.x.x`) thường **được cấp lại mỗi lần kết nối WiFi mới**, không cố định. Nếu hôm nay test ở nhà rồi cho 2 bạn IP đó, tới ngày demo đổi sang WiFi khác (ở trường), IP sẽ đổi — cần kiểm tra lại và báo IP mới đúng ngày demo.

## Tóm gọn quy trình

```
1. Cài Mosquitto, sửa config cho phép nghe từ mạng ngoài (0.0.0.0)
2. Mở firewall port 1883
3. Kiểm tra IP máy bạn (ipconfig trên Windows, ifconfig trên máy khác) — dạng 192.168.x.x
4. Đảm bảo cả 3 người + ESP32 cùng kết nối 1 mạng WiFi/hotspot
5. Gửi IP đó cho 2 bạn, họ sửa code trỏ broker về đúng IP:port đó
6. Test thử: 1 trong 3 publish thử 1 message, người còn lại subscribe xem có nhận được không
```
