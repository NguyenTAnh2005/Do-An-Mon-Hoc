# Note tự nghiên cứu — WebSocket + EMQX + MQTTX cho Dashboard Realtime

> Mục đích: bạn tự triển khai trước, test bằng MQTTX (giả lập ESP32 publish), để dashboard chạy được realtime trước khi 2 bạn kia xong IoT/AI.
> Format: mỗi mục có **Cần gì → Vai trò → Lưu ý**. Bạn đọc, tự ghi chú lại, rồi đối chiếu.

---

## 1. Tổng thể hệ thống cần gì (nhìn 1 lần)

```
┌─────────────┐     MQTT      ┌──────────┐    MQTT     ┌──────────────────┐    WebSocket    ┌──────────────┐
│  ESP32      │ ────────────► │  EMQX    │ ──────────► │  FastAPI Backend │ ──────────────► │  React FE    │
│  (hoặc      │   publish     │  Broker  │  subscribe  │  + MQTT client   │   broadcast     │  Dashboard   │
│  MQTTX giả) │               │          │             │  + WS Manager    │                 │              │
└─────────────┘               └──────────┘             └──────────────────┘                 └──────────────┘
```

**5 thành phần bạn cần dựng:**

1. **EMQX broker** — chạy ở đâu đó (Docker/local/cloud), là trạm trung chuyển MQTT
2. **MQTTX** — tool publish message giả, đóng vai ESP32
3. **Backend MQTT client** — paho-mqtt kết nối EMQX, subscribe topic
4. **Backend WebSocket server** — endpoint + Connection Manager
5. **Frontend WebSocket client** — mở kết nối, nhận delta, update state

---

## 2. EMQX Broker

**Cần gì:**

- Chạy được EMQX (Docker là nhanh nhất: `docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 18083:18083 emqx/emqx:latest`)
- Biết địa chỉ broker (host + port)

**Vai trò:**

- Nhận message từ ESP32 (hoặc MQTTX giả) → giữ → đẩy cho ai subscribe đúng topic
- **Không làm gì liên quan đến WebSocket** — nó chỉ là "bưu điện" của MQTT

**Port cần nhớ:**

| Port      | Dùng cho                             | Có cần không                   |
| --------- | ------------------------------------ | ------------------------------ |
| **1883**  | MQTT thuần (TCP) — paho-mqtt kết nối | ✅ Cần                         |
| **8083**  | MQTT over WebSocket                  | ❌ Chưa cần (trừ khi bạn muốn) |
| **18083** | **Dashboard web của EMQX**           | ✅ Rất nên mở để debug         |

**Lưu ý:**

- Port 18083 là **cực kỳ hữu ích** — mở `http://localhost:18083`, login `admin/public` (lần đầu), xem được:
  - Client nào đang kết nối (backend, MQTTX, ESP32)
  - Topic nào đang có message
  - **Publish message thủ công từ dashboard** (test nhanh không cần MQTTX)
- Nếu chạy Docker: nhớ `-p` đủ 3 port trên, không thì dashboard không mở được
- Nếu là bản cloud (EMQX Cloud): dùng host + port do nó cấp, thường có TLS nên port khác (8883 thay 1883)

**Tự hỏi để kiểm tra hiểu:**

- EMQX có nằm giữa backend và frontend không? → **Không**. Nó chỉ nằm giữa ESP32 và backend.
- Đổi EMQX sang Mosquitto có phải sửa code backend không? → **Gần như không**, chỉ đổi host/port kết nối.

---

## 3. MQTTX — Giả lập ESP32

**Cần gì:**

- Cài MQTTX (app desktop hoặc web `mqttx.app`)
- Tạo 1 connection tới EMQX (host + port 1883)
- Biết **topic** và **format message** mà backend sẽ subscribe

**Vai trò:**

- Đóng vai ESP32: publish message MQTT giả lên EMQX
- Cho phép bạn **test toàn bộ luồng** (EMQX → backend → WS → FE) mà không cần phần cứng

**Lưu ý:**

- **Phải thống nhất topic với backend trước khi publish.** Ví dụ:
  - `school/bins/1/water_level` → thùng 1 báo mực
  - `school/bins/+/water_level` (backend subscribe, dấu `+` là wildcard 1 cấp)
- **Phải thống nhất format payload.** Ví dụ:
  ```json
  { "bin_id": 1, "water_level": 45, "status": "online" }
  ```
- MQTTX publish nhiều message liên tục để test realtime (có chức năng "Auto publish" theo interval)
- Có thể tạo nhiều connection trong MQTTX để giả nhiều ESP32 cùng lúc

**Tự hỏi:**

- Topic backend subscribe là gì? (chốt với 2 bạn kia luôn)
- Payload format là gì? (JSON hay string thuần — nên dùng JSON)
- QoS mấy? (thường 0 hoặc 1 là đủ cho demo)

---

## 4. Backend — MQTT Client (paho-mqtt)

**Cần gì:**

- Thư viện `paho-mqtt`
- 1 instance MQTT client, kết nối EMQX lúc FastAPI startup
- Hàm callback `on_message` xử lý khi có message
- Subscribe topic đã chốt
- **Lưu event loop** của FastAPI lúc startup để dùng sau

**Vai trò:**

- Nghe message từ EMQX
- Khi có message → đóng gói → gửi sang event loop để broadcast

**Cấu trúc tối thiểu:**

```
services/mqtt_client.py
  ├── khởi tạo client (client_id, clean_session)
  ├── client.connect(host, 1883)
  ├── client.subscribe("school/bins/+/water_level")
  ├── def on_message(...)  → run_coroutine_threadsafe(...)
  └── client.loop_start()  ← tạo thread riêng
```

**Lưu ý quan trọng:**

- `client.loop_start()` **tạo thread riêng** — đây là gốc rễ của mọi vấn đề thread.
- `on_message` chạy ở thread đó → **không được** gọi thẳng hàm async.
- Phải **lưu loop** ở startup (dùng `@app.on_event("startup")` hoặc `lifespan`) và truyền tham chiếu cho MQTT client. Nếu gọi `asyncio.get_event_loop()` ở thread khác → lấy sai loop → bug.
- Nên có **`client_id` riêng** cho backend (ví dụ `fastapi-backend-01`) để dễ nhìn trong dashboard EMQX.
- `on_connect` nên `subscribe` lại — vì khi reconnect, subscription có thể mất tùy config.
- Nếu dùng QoS 1: có thể nhận **message trùng** → FE cần xử lý idempotent (update cùng giá trị 2 lần không sao).

**Tự hỏi:**

- Loop được lưu ở đâu? (`app.state.loop` hay global variable?)
- Nếu MQTT mất kết nối → có tự reconnect không? (`client.loop_start()` có tự reconnect mặc định, nhưng nên kiểm tra)
- Message format trước khi broadcast: giữ nguyên payload hay transform?

---

## 5. Backend — WebSocket Endpoint + Connection Manager

**Cần gì:**

- 1 class `ConnectionManager` với `connect / disconnect / broadcast`
- 1 WebSocket route `@router.websocket("/ws/dashboard")`
- Xử lý JWT (verify token từ query string)
- Chỗ lưu instance manager (global hoặc `app.state`)

**Vai trò:**

- Manager: giữ danh sách WS đang mở, gửi message cho tất cả
- Route WS: nhận kết nối mới, verify token, thêm vào manager, giữ connection sống
- Khi client ngắt → xóa khỏi manager

**Cấu trúc tối thiểu:**

```
services/ws_manager.py
  └── class ConnectionManager
        ├── active: set[WebSocket]
        ├── connect(ws)
        ├── disconnect(ws)
        └── broadcast(data)

routers/ws.py
  └── @router.websocket("/ws/dashboard")
        ├── đọc token từ query string
        ├── verify JWT (dùng lại hàm verify hiện có)
        ├── nếu sai → close() ngay
        ├── nếu đúng → manager.connect(ws)
        └── while True: await ws.receive_text()  ← giữ connection sống
```

**Lưu ý:**

- **Phải `await ws.accept()`** trước khi làm gì khác (sau khi verify token nếu verify trước accept).
- `while True: await ws.receive_text()` là cách giữ connection sống. Nếu không có vòng lặp này, hàm route return → connection đóng ngay.
- **Bắt `WebSocketDisconnect`** trong vòng lặp → gọi `manager.disconnect(ws)`.
- Dùng `set` thay vì `list` để tránh trùng connection.
- Trong `broadcast`, dùng `list(self.active)` khi duyệt để tránh lỗi nếu có ai disconnect giữa lúc đang duyệt.
- Nếu 1 connection bị lỗi khi `send_json` → bắt exception, xóa nó khỏi set (đừng để nó làm chết cả vòng broadcast).

**Tự hỏi:**

- Manager instance lưu ở đâu để cả route WS và MQTT callback đều truy cập được? (thường là `app.state.manager`)
- Khi verify JWT sai → close với code gì? (`1008` là "policy violation", hợp lý)
- Format message broadcast: giữ nguyên payload từ MQTT hay bọc thêm `{type, data}`?

---

## 6. Frontend — WebSocket Client

**Cần gì:**

- Chỗ lưu `accessToken` (bạn đã có trong state/hook)
- Hàm tạo `new WebSocket("ws://.../ws/dashboard?token=...")`
- `onopen / onmessage / onclose / onerror`
- State chứa danh sách thùng (snapshot từ REST + delta từ WS)
- Cleanup đóng WS khi unmount
- (Nâng cao) Reconnect logic

**Vai trò:**

- Mở kết nối WS tới backend
- Nhận delta → cập nhật state → UI re-render

**Pattern trong `useEffect`:**

```
useEffect(() => {
  1. axios.get("/api/bins")  → setBins(snapshot)
  2. const ws = new WebSocket(`ws://...?token=${accessToken}`)
  3. ws.onmessage = (e) => { parse + update state }
  4. return () => ws.close()
}, [])
```

**Lưu ý:**

- **`ws.close()` trong cleanup là BẮT BUỘC** — không làm → rò rỉ connection, backend giữ mãi.
- Update state phải **tạo object mới**, không sửa thẳng:
  ```js
  setBins((prev) =>
    prev.map((b) => (b.bin_id === msg.bin_id ? { ...b, ...msg.data } : b)),
  );
  ```
- Không dùng WS để load snapshot ban đầu — dùng REST. WS chỉ cho delta.
- `onmessage` chạy **nhiều lần** (mỗi lần backend broadcast), không phải 1 lần như axios.
- **`accessToken` trong `useEffect` dependency**: nếu token đổi (refresh), có cần mở lại WS không? → Cân nhắc. Có thể để `[]` và tự reconnect khi cần.
- Reconnect: trong `onclose`, `setTimeout` tạo lại `new WebSocket(...)`. Cần **cờ "shouldReconnect"** để tránh loop vô tận khi component unmount hoặc khi token sai.
- **Đóng WS khi logout** — nếu không, connection vẫn mở dù user đã logout.

**Tự hỏi:**

- Khi token hết hạn giữa lúc WS đang mở → có cách nào backend thông báo cho FE không? (có — backend có thể gửi message `{type: "auth_expired"}` rồi close)
- Nếu nhiều tab cùng mở → mỗi tab 1 connection → manager phải chịu được nhiều connection (đã lo trong `set`).

---

## 7. Luồng end-to-end (vẽ ra để tự đối chiếu)

```
[1] MQTTX publish: topic "school/bins/3/water_level", payload {"bin_id":3,"water_level":45}
        ↓
[2] EMQX nhận, đẩy cho ai subscribe topic khớp
        ↓
[3] paho-mqtt (thread B) on_message chạy
        ↓
[4] run_coroutine_threadsafe(manager.broadcast(...), loop)
        ↓
[5] Event loop (thread A) nhận task, chạy broadcast
        ↓
[6] manager gửi JSON tới mọi WS đang mở
        ↓
[7] FE onmessage nhận → map array → chỉ update bin_id=3
        ↓
[8] React re-render chỉ thùng 3
```

**Khi tự test, bạn debug từng bước:**

- Bước 1-2: mở dashboard EMQX port 18083 → xem message có tới broker không? Topic có đúng không?
- Bước 3-4: log trong `on_message` → xem có chạy không? Payload parse được không?
- Bước 5-6: log trong `broadcast` → xem có client nào trong `manager.active` không?
- Bước 7-8: mở DevTools Network tab → filter "WS" → xem có message bay xuống không? Console.log trong `onmessage`.

---

## 8. Những "bẫy" nên tự note lại

| Bẫy                                      | Hậu quả                           | Cách tránh                                      |
| ---------------------------------------- | --------------------------------- | ----------------------------------------------- |
| Quên `ws.accept()`                       | Connection treo, FE không nhận gì | Luôn accept sau khi verify token                |
| Route WS không có `while True`           | Hàm return → connection đóng ngay | Dùng `while True: await ws.receive_text()`      |
| FE quên `ws.close()` trong cleanup       | Rò rỉ connection, backend giữ mãi | `return () => ws.close()` trong useEffect       |
| Sửa thẳng state thay vì tạo object mới   | React không re-render             | Dùng spread `{...b, ...msg.data}`               |
| Gọi `broadcast()` thẳng từ MQTT callback | Lỗi thread, crash                 | Dùng `run_coroutine_threadsafe`                 |
| Lưu sai event loop                       | Coroutine không chạy              | Lưu loop lúc startup                            |
| Token trong query string bị log          | Lộ token                          | Chấp nhận với đồ án; production thì dùng cách 2 |
| Broadcast tới connection đã chết         | Crash giữa vòng lặp               | Bọc `try/except` từng `send_json`               |
| Không có reconnect                       | Dashboard đứng hình khi mất mạng  | Thêm `setTimeout` trong `onclose`               |
| Reconnect loop vô tận khi token sai      | Spam backend                      | Cờ `shouldReconnect` + giới hạn lần thử         |

---

## 9. Checklist để tự đối chiếu khi làm xong

**Setup:**

- [x] EMQX chạy, dashboard port 18083 mở được
- [x] MQTTX kết nối EMQX thành công, publish thử 1 message
- [ ] Backend kết nối EMQX thành công (thấy trong dashboard EMQX)
- [ ] Backend subscribe đúng topic (thấy trong dashboard EMQX)

**Backend:**

- [ ] `on_message` chạy khi MQTTX publish (log ra được)
- [ ] `broadcast` chạy đúng thread (log ra được)
- [ ] WS endpoint accept connection (test bằng browser/Postman)
- [ ] `manager.active` có connection khi FE mở

**Frontend:**

- [ ] WS mở được (DevTools Network → WS → Status 101)
- [ ] `onmessage` nhận được data
- [ ] State update đúng phần tử
- [ ] UI re-render đúng
- [ ] Cleanup đóng WS khi đổi trang
- [ ] (Optional) Reconnect hoạt động khi kill backend rồi bật lại

**End-to-end:**

- [ ] MQTTX publish → FE thấy thay đổi **trong < 1 giây**
- [ ] Publish cho 2 thùng khác nhau → cả 2 update đúng
- [ ] Mở 2 tab → cả 2 update đồng thời

---

## 10. Thứ tự tự nghiên cứu gợi ý

1. **Chạy EMQX + MQTTX trước** — publish message thủ công, xem dashboard EMQX, hiểu broker trước.
2. **Backend MQTT client đơn giản** — chỉ log `on_message` ra console, chưa cần WS. Chắc chắn nhận được message.
3. **Thêm WebSocket endpoint + manager** — test bằng browser console: `new WebSocket("ws://...")`, xem có accept không.
4. **Nối MQTT → WS** — dùng `run_coroutine_threadsafe`, log trong `broadcast`.
5. **Frontend đơn giản** — chỉ `onmessage` → `console.log`, chưa setState. Chắc chắn nhận được.
6. **Frontend đầy đủ** — setState + render.
7. **Reconnect + cleanup** — thêm sau cùng.

→ Mỗi bước phải chạy được mới qua bước sau. Đừng làm hết 1 lượt rồi debug — sẽ không biết lỗi ở đâu.

---

Bạn cứ note lại rồi tự làm theo thứ tự. Khi vướng ở bước nào, quay lại đây đối chiếu. Cần mình đào sâu phần nào (ví dụ: code mẫu tối giản cho từng bước, hoặc giải thích sâu hơn về một "bẫy" cụ thể) thì nói mình biết.
