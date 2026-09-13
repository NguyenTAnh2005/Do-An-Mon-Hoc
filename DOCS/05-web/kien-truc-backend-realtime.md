# Kiến trúc Backend: MQTT Subscriber + WebSocket Server & Frontend: REST + WebSocket

> **Mục đích file này:** giải thích cơ chế realtime của hệ thống — vì sao Backend cần vừa là MQTT subscriber vừa là WebSocket server, và vì sao Frontend cần dùng cả REST lẫn WebSocket. Dùng làm tài liệu tham chiếu khi Anh code phần Backend/Frontend.

Liên quan: [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) · [Thiết kế Database](./thiet-ke-database.md) · [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md)

---

## 1. Vì sao Backend phải vừa là MQTT subscriber, vừa là WebSocket server

Ba module AI, IoT, Web không giao tiếp trực tiếp với nhau — tất cả đi qua MQTT broker (Mosquitto). Nhưng trình duyệt (React) **không nói được MQTT**, nó chỉ nói HTTP/WebSocket. Vì vậy Backend đóng vai trò cầu nối bắt buộc:

```
ESP32 ──┐
        ├─► MQTT Broker ──► Backend (subscriber) ──► WebSocket ──► React (browser)
AI/cv2 ─┘                         │
                                  └─► ghi/update PostgreSQL
```

Backend chạy **đồng thời hai vai trò**, không phải hai server tách biệt:

- Là **MQTT client (subscriber)**: lắng nghe các topic đã chốt (`mucday`, `phanloai`, `trangthai/iot`, `trangthai/ai`)
- Là **WebSocket server**: giữ kết nối mở với các trình duyệt đang mở dashboard, đẩy dữ liệu mới xuống ngay khi có

> Lưu ý: tín hiệu "không tự tin" (LED đỏ) từ AI **không đi qua Backend** — đó là luồng AI → ESP32 trực tiếp qua MQTT. Backend chỉ xử lý `phanloai` khi có kết quả phân loại thật sự (xem [luồng nhận diện](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md#41-điều-kiện-xảy-ra)).

## 2. Luồng xử lý khi nhận được một message MQTT

Với mỗi topic, Backend làm 3 việc theo thứ tự: **parse → lưu DB → broadcast**.

| Topic                             | Backend làm gì                                                                                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `truong/khu{n}/mucday/{loai_rac}` | Nhận `d` thô → tính `%đầy = (H-d)/H×100` → update `phan_tram_day_hien_tai` trong `thung_rac` (ghi đè, không lưu lịch sử) → broadcast qua WS                 |
| `truong/khu{n}/phanloai`          | Nhận `log_id, loai_rac, confidence, timestamp` → tạo dòng mới trong `lich_su_phan_loai` (chưa có ảnh) → broadcast qua WS để dashboard/lịch sử cập nhật ngay |
| `truong/khu{n}/trangthai/iot`     | LWT — cập nhật `iot_online` của `khu_vuc` → broadcast                                                                                                       |
| `truong/khu{n}/trangthai/ai`      | Tương tự, cập nhật `ai_online` → broadcast                                                                                                                  |

Điểm quan trọng: **MQTT chỉ để nhận dữ liệu vào**, còn **WebSocket chỉ để đẩy dữ liệu ra** cho FE. Backend là nơi duy nhất "dịch" giữa hai giao thức.

## 3. Vì sao FastAPI cần chạy MQTT client dạng background task

FastAPI (sync) vốn xử lý theo model request/response, nhưng MQTT client phải **chạy nền, luôn lắng nghe**, không đợi request nào cả. Cách làm chuẩn:

- Dùng thư viện `paho-mqtt`, chạy MQTT client trong **một thread/background task riêng**, khởi động cùng lúc với app FastAPI (qua `lifespan`/`startup` event)
- Callback `on_message` của MQTT sẽ gọi hàm xử lý (parse → lưu DB → gọi hàm broadcast WebSocket)
- WebSocket connections được quản lý trong một **connection manager** (list các socket đang mở), để khi có event mới thì loop qua và gửi cho tất cả client đang kết nối

```python
# Ý tưởng cấu trúc, không phải code đầy đủ
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

def on_mqtt_message(client, userdata, msg):
    # 1. parse topic + payload
    # 2. tính toán / lưu DB (sync, trong thread MQTT)
    # 3. đẩy sang WebSocket — cần cầu nối giữa thread sync và event loop async
    #    (ví dụ dùng asyncio.run_coroutine_threadsafe)
    ...
```

**Lưu ý kỹ thuật cần nhớ khi code thật:** MQTT callback (`paho-mqtt`) chạy trên thread riêng, còn FastAPI WebSocket chạy trong event loop async. Không thể `await` trực tiếp từ thread MQTT — phải dùng `asyncio.run_coroutine_threadsafe()` để đẩy việc broadcast vào event loop chính. Đây là điểm dễ vướng nhất khi code phần này.

## 4. Vì sao Frontend cần cả REST lẫn WebSocket, không dùng WebSocket cho tất cả

WebSocket rất hợp để **đẩy update tức thời**, nhưng có nhược điểm: **khi client vừa mở kết nối, nó không có "trạng thái quá khứ"** — nó chỉ nhận được các message phát ra _sau_ thời điểm kết nối. Nếu chỉ dùng WebSocket, người dùng mở dashboard lên sẽ thấy màn hình trống cho tới khi có sự kiện mới.

Vì vậy chia rõ 2 việc:

| Nhu cầu                                                                             | Dùng gì                             | Lý do                                                                                   |
| -------------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------- |
| Tải dữ liệu ban đầu khi mở trang (6 thùng đang đầy bao nhiêu %, online/offline)         | **REST GET**                          | Cần "snapshot" trạng thái hiện tại ngay lúc load, REST trả về đúng 1 lần là đủ                |
| Cập nhật % đầy, trạng thái online, kết quả phân loại mới... trong lúc đang mở trang     | **WebSocket**                         | Cần đẩy realtime, không muốn FE phải polling liên tục                                        |
| Xem lịch sử phân loại, lọc, thống kê                                                    | **REST** (GET có filter/pagination)   | Dữ liệu tra cứu, không cần realtime, REST phù hợp hơn cho query có điều kiện                  |
| Xác nhận đúng/sai, batch delete                                                         | **REST** (POST/PATCH/DELETE)          | Đây là hành động ghi dữ liệu — WebSocket không phù hợp cho request/response có xác nhận       |

### Luồng thực tế trên Frontend

```
1. Component Dashboard mount
   → gọi REST GET /api/khu-vuc  (lấy toàn bộ trạng thái hiện tại: 6 thùng, iot_online, ai_online)
   → render lần đầu

2. Sau đó mở kết nối WebSocket
   → mỗi khi nhận message (fill % mới / trạng thái đổi / phân loại mới)
   → cập nhật state cục bộ (ví dụ dùng useState/useReducer), KHÔNG gọi lại REST

3. Khi rời trang / component unmount
   → đóng WebSocket
```

```jsx
useEffect(() => {
  const ws = new WebSocket("ws://localhost:8000/ws/thung-rac");
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    setThungRac((prev) =>
      prev.map((t) => (t.id === data.id ? { ...t, ...data } : t)),
    );
  };
  return () => ws.close();
}, []);
```

Việc tách bạch này giúp:

- Trang luôn có dữ liệu ngay khi load (không phải đợi sự kiện MQTT tiếp theo mới có gì để hiển thị)
- WebSocket chỉ cần gửi **dữ liệu thay đổi (delta)**, không cần gửi lại toàn bộ state mỗi lần

**Vì sao cần lưu `iot_online`/`ai_online` + `lan_cuoi_online` vào DB:** LWT chỉ bắn 1 lần duy nhất tại đúng thời điểm rớt mạng. Người mở trang sau (hoặc F5) sẽ bỏ lỡ sự kiện đó nếu không có DB để tra lại trạng thái mới nhất.

## 5. Tóm tắt để brief lại

- **Backend = 1 process, 2 vai trò chạy song song**: MQTT subscriber (nhận từ AI/IoT) + WebSocket server (đẩy cho FE), nối với nhau qua DB và connection manager.
- **FE không nói MQTT** — mọi dữ liệu tới FE đều qua Backend, dưới dạng REST (lúc load) hoặc WebSocket (lúc đang mở trang).
- **REST dùng cho**: load ban đầu, lịch sử/thống kê (có filter), và mọi hành động ghi (xác nhận, xoá).
- **WebSocket dùng cho**: đẩy thay đổi realtime duy nhất — fill %, trạng thái online/offline, kết quả phân loại mới.
- Điểm kỹ thuật khó nhất khi code thật: cầu nối giữa MQTT callback (thread sync) và WebSocket broadcast (async event loop) — cần `asyncio.run_coroutine_threadsafe`.
