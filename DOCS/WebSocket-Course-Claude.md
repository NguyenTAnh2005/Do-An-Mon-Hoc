# WebSocket + MQTT cho Backend: hiểu hệ thống trước, code sau

Dự án Phân loại Rác · Tuần 7 · Nguyễn Tuấn Anh · 21/10/2026

## 1. Bài toán cần giải

Dashboard của quản lý phải thấy **không cần bấm refresh**: % đầy của 6 thùng, và IoT/AI của mỗi khu vực đang online hay offline.

Dữ liệu đó sinh ra ở ESP32 và AI script. Hai bên này nói MQTT. Trình duyệt thì nói HTTP và WebSocket. Backend đứng giữa và làm ba việc:

1. **Nghe** MQTT từ thiết bị
2. **Xử lý**: kiểm tra payload, tính toán, ghi DB
3. **Đẩy** kết quả xuống mọi trình duyệt đang mở dashboard

```
ESP32 / AI ──MQTT──► EMQX ──MQTT──► Backend (FastAPI) ──WebSocket──► React Dashboard
 (publish)         (broker)       (subscribe + xử lý)     (broadcast)
```

| Khối              | Vai trò trong một câu                                   |
| ----------------- | ------------------------------------------------------- |
| ESP32 / AI script | Nguồn dữ liệu, chỉ biết publish lên topic               |
| EMQX              | Bưu điện: nhận tin, chuyển cho ai subscribe đúng topic  |
| Backend           | Bộ não: nghe, xử lý, ghi DB, quyết định đẩy gì cho FE   |
| WebSocket         | Đường dây hai chiều luôn mở giữa Backend và trình duyệt |
| React             | Hiển thị, giữ state, nhận phần thay đổi (delta)         |

**Vì sao không cho trình duyệt nối thẳng EMQX?** EMQX có hỗ trợ MQTT qua WebSocket (cổng 8083) nên về kỹ thuật làm được. Nhưng khi đó FE phải cầm thông tin kết nối broker, JWT của bạn không còn bảo vệ dữ liệu, FE nhận giá trị thô `d` của cảm biến và phải tự tính %, và dữ liệu không đi qua DB. Cho Backend làm trạm trung gian thì mọi logic nằm ở một chỗ.

**Tự hỏi:** EMQX nằm giữa những bên nào? (Chỉ giữa thiết bị và Backend, không liên quan tới WebSocket của bạn. Đổi sang broker khác thì gần như chỉ đổi host/port.)

## 2. MQTT: phía nói chuyện với thiết bị

### 2.1 Vì sao thiết bị IoT dùng MQTT chứ không dùng HTTP

HTTP là hỏi-đáp: bên nào muốn dữ liệu phải chủ động gọi, và bên gửi phải biết địa chỉ bên nhận. Nếu một tin của ESP32 cần tới cả Backend lẫn thiết bị khác thì phải gọi từng nơi.

MQTT là **publish/subscribe qua một broker**: bên gửi chỉ ném tin vào một topic, ai quan tâm thì subscribe topic đó. Nó nhẹ, giữ kết nối lâu, và có cơ chế báo khi thiết bị rớt mạng. Với dự án của bạn còn một lý do nữa: ba bên (AI, IoT, Web) chỉ cần thống nhất **tên topic và định dạng payload**, không cần biết địa chỉ nhau, nên mỗi người làm phần mình độc lập được.

### 2.2 Từ vựng cốt lõi

| Khái niệm       | Ý nghĩa                                                                                       |
| --------------- | --------------------------------------------------------------------------------------------- |
| Broker          | Máy chủ trung chuyển (ở đây là EMQX)                                                          |
| Client          | Bất kỳ ai kết nối broker: ESP32, AI script, Backend, MQTTX                                    |
| Topic           | “Địa chỉ” phân cấp của tin, ví dụ `school/area1/fill_level/organic`                           |
| Wildcard        | `+` thay đúng một cấp, `#` thay mọi cấp phía sau. Chỉ dùng khi **subscribe**                  |
| Payload         | Nội dung tin (dự án dùng JSON)                                                                |
| QoS 0           | Gửi tối đa một lần, có thể mất. Hợp dữ liệu liên tục                                          |
| QoS 1           | Gửi ít nhất một lần, có thể trùng. Hợp sự kiện quan trọng                                     |
| LWT (Last Will) | “Di chúc” đăng ký lúc kết nối: nếu client rớt đột ngột, broker tự publish tin offline thay nó |
| client_id       | Tên định danh client. **Hai client trùng id sẽ đá nhau liên tục**                             |

### 2.3 EMQX

EMQX chỉ là bưu điện. Dự án dùng EMQX serverless nên host, port và TLS do dịch vụ cấp (thường là cổng TLS khác 1883, xem trang thông tin kết nối). Phần hữu ích nhất để học là dashboard của EMQX: xem client nào đang online, topic nào có tin, và publish thử một tin thủ công mà không cần MQTTX. Nếu sau này chạy EMQX bằng Docker local thì nhớ mở cổng 1883 (MQTT) và 18083 (dashboard).

### 2.4 Các topic của dự án

| Topic                                    | Ai publish  | Ai subscribe     | QoS | Backend làm gì                                                                       |
| ---------------------------------------- | ----------- | ---------------- | --- | ------------------------------------------------------------------------------------ |
| `school/area{n}/fill_level/{waste_type}` | ESP32       | Backend          | 0   | Nhận `d` thô, tính % đầy = (H − d)/H × 100, ghi đè `current_fill_percent`, broadcast |
| `school/area{n}/classification`          | AI          | Backend và ESP32 | 1   | ESP32 mở servo; Backend insert `classification_log` (chưa có ảnh)                    |
| `school/area{n}/status/iot`              | ESP32 (LWT) | Backend          | 1   | Cập nhật `iot_online`, broadcast                                                     |
| `school/area{n}/status/ai`               | AI (LWT)    | Backend          | 1   | Cập nhật `ai_online`, broadcast                                                      |
| `school/area{n}/uncertain`               | AI          | Chỉ ESP32        | 1   | **Backend không subscribe**                                                          |

Backend chỉ cần 3 pattern: `school/+/fill_level/+`, `school/+/classification`, `school/+/status/+`. Vì schema lưu **full topic** cho từng area và thùng, backend tìm đúng thùng bằng cách tra bảng theo topic nhận được, không nối chuỗi.

### 2.5 Hai loại tin: state và event

Đây là phân biệt quyết định cách xử lý:

- **State** (`fill_level`, `status`): mô tả tình trạng hiện tại, tin mới thay tin cũ. Mất một tin không sao vì sẽ có tin kế tiếp. Xử lý: ghi đè + broadcast.
- **Event** (`classification`): một sự kiện xảy ra đúng một lần. Mất là mất. Xử lý: insert một dòng mới, không ghi đè.

**Câu hỏi mở nên chốt với Vũ và Tường vào thứ 2:** khi Backend khởi động lại, nó không biết IoT/AI đang online hay offline cho tới khi có tin status kế tiếp. Cách thường dùng là publish status với cờ **retained** để broker giữ tin cuối và gửi ngay cho subscriber mới. Cần hai bạn kia đồng ý vì họ là bên publish.

**Tự hỏi:** vì sao `classification` dùng QoS 1 còn `fill_level` dùng QoS 0? Nếu `classification` nhận trùng hai lần thì Backend tránh insert hai dòng bằng cách nào? (Gợi ý: `log_id` là UUID duy nhất.)

## 3. WebSocket: phía nói chuyện với trình duyệt

### 3.1 Vì sao dashboard cần WebSocket

HTTP chỉ cho phép trình duyệt hỏi, server không tự gửi được. Muốn thấy dữ liệu mới bằng HTTP phải hỏi lặp lại (polling), vừa tốn vừa trễ. WebSocket bắt đầu bằng một request HTTP xin “nâng cấp” (trả về status 101), sau đó thành **một đường dây hai chiều mở liên tục**: Backend có tin mới là đẩy xuống ngay.

### 3.2 Vòng đời một kết nối

1. FE mở kết nối, kèm access token
2. Backend kiểm tra JWT. Sai thì đóng ngay (mã `1008`)
3. Đúng thì `accept()`
4. Backend cho kết nối vào danh sách chung (manager)
5. Backend **giữ hàm sống** bằng vòng lặp chờ nhận tin. Hàm kết thúc là kết nối đóng
6. Kết nối đứt (đóng tab, mất mạng, hết hạn token)
7. Backend bắt `WebSocketDisconnect` và gỡ khỏi danh sách

Đây là điểm khác route HTTP: route HTTP return là xong, route WebSocket phải sống suốt vòng đời kết nối.

### 3.3 Backend: vì sao cần ConnectionManager

Mỗi route WebSocket chỉ biết **một** kết nối của nó. Nhưng khi MQTT có tin mới, Backend cần gửi cho **tất cả** trình duyệt đang mở. Cần một “sổ chung” để làm việc đó:

| Thành phần                | Việc                                                                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Tập các WebSocket đang mở | Dùng `set` để không trùng                                                                                                                 |
| `connect`                 | Thêm vào tập sau khi accept                                                                                                               |
| `disconnect`              | Gỡ khỏi tập                                                                                                                               |
| `broadcast`               | Duyệt tập, gửi cho từng kết nối. Duyệt trên bản sao `list(...)`; bọc `try/except` từng lần gửi để một kết nối chết không làm hỏng cả vòng |

Manager phải truy cập được từ **cả route WebSocket lẫn callback MQTT**, nên đặt ở một chỗ dùng chung (ví dụ `app.state`) thay vì tạo mới trong từng nơi.

### 3.4 Frontend: khác axios ở đâu

- `new WebSocket(url)` tạo ra một **đối tượng kết nối sống**, không phải một lệnh gọi trả response
- Không có response, chỉ có sự kiện: `onopen`, `onmessage` (chạy lặp lại mỗi lần Backend đẩy), `onclose`, `onerror`
- Không còn “loading” theo nghĩa cũ, chỉ có “đã kết nối chưa” và dữ liệu đến dần
- Mở trong `useEffect` lúc mount và **bắt buộc `ws.close()` trong cleanup**, nếu không rò rỉ kết nối
- Cập nhật state bằng object mới (spread), không sửa trực tiếp
- Mất kết nối giữa chừng là chuyện bình thường nên cần tự reconnect bằng `setTimeout`, có cờ để không lặp vô tận

### 3.5 JWT trên WebSocket

Trình duyệt không gắn custom header cho WebSocket được như interceptor của axios, và access token của bạn nằm trong memory nên cũng không tự đính kèm như cookie. Đã chốt: gửi token qua **query string** lúc kết nối. Hạn chế cần ghi vào báo cáo: URL có thể bị log nên lộ token; chấp nhận cho đồ án, bản production nên gửi token bằng message đầu tiên sau khi mở kết nối.

Backend đang chạy HTTPS local (mkcert) nên FE phải dùng `wss://`, không phải `ws://`.

**Tự hỏi:** nếu không có vòng lặp giữ sống trong route WebSocket thì chuyện gì xảy ra? Vì sao cleanup `ws.close()` là bắt buộc?

## 4. Cầu nối: nơi hai thế giới gặp nhau

Đây là phần dễ gây mất phương hướng nhất, nên hiểu kỹ.

- FastAPI chạy trong thế giới **asyncio**: có một người điều phối (event loop) và mọi hàm `async` do người này chạy.
- `paho-mqtt` với `loop_start()` mở **một thread riêng** để nghe broker. Callback `on_message` chạy trong thread đó, **ngoài** thế giới asyncio.

Callback `on_message` không thể gọi thẳng `await manager.broadcast(...)`: nó không có event loop để chạy hàm async. Hình dung: thread MQTT là nhân viên giao hàng, không được tự vào bàn làm việc của văn phòng, chỉ được bỏ giấy vào khay nhận việc. `asyncio.run_coroutine_threadsafe(coro, loop)` chính là cái khay đó: nó đóng gói coroutine và đẩy an toàn vào hàng đợi của event loop chính.

Hệ quả cần nhớ:

1. Phải **lưu event loop lúc FastAPI startup** và đưa cho phía MQTT. Gọi `get_event_loop()` ngay trong thread MQTT sẽ lấy sai loop.
2. Callback chạy ngoài request nên **không có `Depends(get_db)`**. Muốn ghi DB thì tự mở session và đóng trong `finally`.
3. Callback phải bền: payload sai JSON hay thiếu field không được làm callback chết, vì lỗi ném ra có thể làm thread MQTT ngừng xử lý.
4. Chạy **một worker** uvicorn. Nhiều worker nghĩa là nhiều manager và nhiều MQTT client, FE chỉ nhận được tin của worker mình nối vào.

Luồng xử lý một tin MQTT trong Backend:

```
on_message (thread MQTT)
  → tách topic: loại tin nào, khu vực nào, loại rác nào
  → parse JSON (try/except)
  → xử lý theo loại: tính % / cập nhật status / insert log  (ghi DB bằng session riêng)
  → dựng message {type, ...}
  → run_coroutine_threadsafe(manager.broadcast(msg), loop)
        ↓
  event loop chính chạy broadcast → mọi WebSocket đang mở nhận tin
```

**Tự hỏi:** nếu bỏ `run_coroutine_threadsafe` và gọi thẳng hàm broadcast thì lỗi gì xảy ra, và vì sao?

## 5. REST hay WebSocket?

Nguyên tắc: **WebSocket cho dữ liệu tự thay đổi khi người dùng đang nhìn màn hình. REST cho mọi thứ người dùng chủ động hỏi hoặc thao tác.**

| Dữ liệu                                         | Kênh      | Lý do                                             |
| ----------------------------------------------- | --------- | ------------------------------------------------- |
| Load dashboard lần đầu (6 thùng, trạng thái)    | REST      | Lấy ảnh chụp hiện tại (snapshot) lúc mount        |
| % đầy từng thùng                                | WebSocket | ESP publish liên tục, chỉ ghi đè giá trị hiện tại |
| Online/offline IoT và AI                        | WebSocket | Cần thấy ngay khi đổi                             |
| Lịch sử phân loại (filter, phân trang, ảnh)     | REST      | Có truy vấn và phân trang                         |
| Xác nhận đúng/sai, batch delete, upload lại ảnh | REST      | Là hành động ghi                                  |
| Thống kê                                        | REST      | Tính theo khoảng thời gian                        |
| Đăng nhập, refresh token                        | REST      | Hiển nhiên                                        |

**Mẫu snapshot + delta:** REST lấy trạng thái đầy đủ lúc mount, WebSocket chỉ gửi phần thay đổi sau đó. Có một khe hở nhỏ giữa lúc lấy snapshot và lúc nhận tin đầu tiên, nhưng `fill_level` được publish liên tục nên tự sửa ở lần kế tiếp. Chấp nhận được cho đồ án.

**`classification_log` (đề xuất, chưa chốt):** cho trang lịch sử đi **hoàn toàn bằng REST**. Lý do: ảnh tới sau metadata nên một dòng log mới đẩy qua WebSocket sẽ chưa có ảnh; đẩy log vào bảng đang lọc và phân trang buộc FE phải ghép dữ liệu, kiểm tra filter và dedupe theo `log_id`; WebSocket không phát lại tin nên sau khi reconnect vẫn phải refetch bằng REST. Nếu còn thời gian, thêm một tin báo nhẹ `classification_created` để FE hiện badge “có log mới” hoặc refetch, còn dữ liệu đầy đủ vẫn đi qua REST.

## 6. Hợp đồng thông điệp xuống FE (đề xuất)

Bạn đã chốt mọi tin gửi xuống FE được bọc dạng `{type, ...}` thay vì giữ nguyên payload MQTT. Lý do nên làm vậy: FE chỉ cần `switch (type)`, và thêm loại tin mới không làm hỏng những loại cũ. Các tên dưới đây là đề xuất để bạn chốt:

| `type`                              | Nội dung                                                     | Khi nào gửi                                     |
| ----------------------------------- | ------------------------------------------------------------ | ----------------------------------------------- |
| `fill_level`                        | `area_id`, `waste_type`, `percent`, `timestamp`              | Sau khi tính % từ tin fill_level                |
| `status`                            | `area_id`, `source` (`iot` hoặc `ai`), `online`              | Khi nhận tin status hoặc LWT                    |
| `classification_created` (tùy chọn) | `log_id`, `area_id`, `waste_type`, `confidence`, `timestamp` | Sau khi insert log                              |
| `auth_expired` (tùy chọn)           | không có                                                     | Trước khi Backend đóng kết nối vì token hết hạn |

Tên enum như `waste_type` giữ nguyên tiếng Anh xuyên suốt MQTT, DB, API; FE tự map sang tiếng Việt khi hiển thị.

## 7. Kế hoạch triển khai theo từng bài

Mỗi bài phải chạy được và tự giải thích được rồi mới sang bài sau; đừng làm cả lượt rồi mới debug. Bài 1 đến 4 theo ghi chú đã làm và test xong, nên bạn chỉ cần **ôn phần hiểu**: tự vẽ lại sơ đồ mục 1 và mục 4 không nhìn tài liệu.

### Bài 1: EMQX + MQTTX (đã làm)

- **Mục tiêu:** hiểu broker và topic bằng tay, chưa cần code.
- **Việc làm:** kết nối MQTTX vào EMQX, publish và subscribe thử, xem client và topic trong dashboard EMQX.
- **Xong khi:** giải thích được vì sao subscribe `school/+/fill_level/+` nhận được tin publish ở `school/area1/fill_level/organic`.

### Bài 2: Backend nghe MQTT (đã làm)

- **Mục tiêu:** Backend là một MQTT client.
- **Việc làm:** paho-mqtt kết nối lúc startup, subscribe 3 pattern, `on_message` chỉ log topic và payload; `client_id` riêng.
- **Xong khi:** publish từ MQTTX thì thấy log; thấy client Backend trong dashboard EMQX.
- **Hiểu được:** `loop_start()` mở thread riêng.

### Bài 3: WebSocket endpoint + manager (đã làm)

- **Việc làm:** ConnectionManager, route `/ws/dashboard`, verify JWT từ query string, vòng lặp giữ sống, bắt `WebSocketDisconnect`.
- **Xong khi:** mở hai tab thì manager có 2 kết nối, đóng một tab thì còn 1.

### Bài 4: Cầu nối MQTT → WebSocket (đã làm)

- **Việc làm:** lưu event loop lúc startup, `run_coroutine_threadsafe` đẩy broadcast.
- **Xong khi:** publish từ MQTTX thì cả hai tab nhận được tin thô.

### Bài 5: Xử lý thật ở Backend (bước tiếp theo)

- **Mục tiêu:** biến payload thô thành dữ liệu có nghĩa.
- **Việc làm:** trong `on_message`, theo luồng ở mục 4: tách topic và tra thùng/khu vực theo full topic; parse JSON có `try/except`; rẽ nhánh theo loại: fill_level (tính %, ghi đè `current_fill_percent`), status (cập nhật `iot_online` / `ai_online`), classification (insert `classification_log`, `image_url` để trống); dựng message `{type, ...}` rồi broadcast.
- **Xong khi:** publish từ MQTTX thì DB đổi đúng; payload sai không làm chết callback; tin trùng không tạo hai dòng log.
- **Hiểu được:** state khác event ở chỗ nào.

### Bài 6: REST snapshot cho dashboard

- **Việc làm:** một endpoint trả 6 thùng cùng trạng thái online/offline của từng khu vực, dùng JWT dependency như các route admin khác.
- **Xong khi:** gọi endpoint ra đúng dữ liệu mà Bài 5 vừa ghi vào DB.

### Bài 7: Script giả lập MQTT

- **Mục tiêu:** có nguồn dữ liệu để test và demo khi Vũ và Tường chưa xong.
- **Việc làm:** script Python publish định kỳ cho 6 thùng (giá trị `d` thay đổi dần), publish status, thỉnh thoảng publish một `classification`. Để thử LWT, tắt đột ngột tiến trình giả lập IoT thay vì thoát êm.
- **Xong khi:** chạy script thì DB và broadcast thay đổi liên tục không cần chạm tay.

### Bài 8: Frontend hook kết nối WebSocket

- **Việc làm:** một hook riêng mở `wss://...?token=...`, `onmessage` chỉ `console.log` trước rồi mới `switch (type)`; cleanup đóng kết nối.
- **Xong khi:** DevTools tab Network, lọc WS, thấy status 101 và tin bay xuống.

### Bài 9: Giao diện dashboard

- **Việc làm:** REST load snapshot vào state, WebSocket cập nhật đúng phần tử bằng spread; hiển thị trạng thái đã kết nối chưa.
- **Xong khi:** chạy script giả lập thì thùng nào đổi chỉ thùng đó re-render; mở hai tab đều cập nhật; từ lúc publish đến lúc thấy chưa tới 1 giây.

### Bài 10: Độ bền

- **Việc làm:** reconnect bằng `setTimeout` với cờ và giới hạn số lần thử; đóng WebSocket khi logout; xử lý token hết hạn (Backend gửi `auth_expired` rồi đóng); sau reconnect gọi lại REST snapshot.
- **Xong khi:** tắt rồi bật lại Backend thì dashboard tự nối lại và dữ liệu đúng.

### Bài 11 (tùy chọn): Tin báo classification

- Chỉ làm khi đã xong tất cả bài trên. Thêm một dòng broadcast `classification_created` ở Backend và một nhánh `switch` ở FE; không đụng gì phần đã làm.

## 8. Bẫy thường gặp

| Bẫy                                                                | Hậu quả                               | Cách tránh                                                   |
| ------------------------------------------------------------------ | ------------------------------------- | ------------------------------------------------------------ |
| Quên `accept()` hoặc route WebSocket không có vòng lặp             | Kết nối treo hoặc đóng ngay           | Accept sau khi verify; `while True: await ws.receive_text()` |
| Gọi `broadcast` thẳng từ callback MQTT                             | Lỗi thread, tin không gửi             | `run_coroutine_threadsafe`                                   |
| Lưu sai event loop                                                 | Coroutine không bao giờ chạy          | Lưu loop lúc startup                                         |
| Callback MQTT ném lỗi vì payload sai                               | Thread MQTT ngừng xử lý               | `try/except` bao toàn bộ callback                            |
| Hai client trùng `client_id` (ví dụ reload hai tiến trình)         | Hai bên đá nhau, mất kết nối liên tục | Mỗi tiến trình một id riêng                                  |
| Chạy nhiều worker uvicorn                                          | Mỗi worker một manager, FE thiếu tin  | Chạy một worker                                              |
| Trang HTTPS nhưng dùng `ws://`, hoặc chứng chỉ mkcert chưa tin cậy | Trình duyệt chặn kết nối              | Dùng `wss://`, cài CA của mkcert                             |
| FE quên `ws.close()` khi unmount hoặc logout                       | Rò rỉ kết nối                         | Cleanup trong `useEffect`                                    |
| Sửa trực tiếp state thay vì tạo object mới                         | React không re-render                 | Dùng spread                                                  |
| Reconnect lặp vô tận khi token sai                                 | Spam Backend                          | Cờ `shouldReconnect` và giới hạn số lần thử                  |
| Broadcast tới kết nối đã chết                                      | Crash giữa vòng lặp                   | `try/except` từng lần gửi                                    |

## 9. Gỡ lỗi theo tầng

Khi dashboard không cập nhật, đi từ nguồn xuống, kiểm tra từng tầng và dừng ở tầng đầu tiên hỏng:

| Tầng            | Câu hỏi                                         | Kiểm tra bằng                                       |
| --------------- | ----------------------------------------------- | --------------------------------------------------- |
| 1. Broker       | Tin có tới EMQX không, topic có đúng không?     | Dashboard EMQX hoặc MQTTX subscribe `school/#`      |
| 2. Subscribe    | Backend có subscribe đúng pattern không?        | Dashboard EMQX, mục subscription của client Backend |
| 3. Callback     | `on_message` có chạy, payload parse được không? | Log trong `on_message`                              |
| 4. Xử lý        | DB có đổi đúng không?                           | Xem trực tiếp bảng trong Postgres                   |
| 5. Broadcast    | Manager có kết nối nào không?                   | Log số kết nối trong `broadcast`                    |
| 6. Đường truyền | Tin có bay xuống trình duyệt không?             | DevTools, tab Network, lọc WS, xem Messages         |
| 7. State FE     | Tin có vào state, UI có render không?           | `console.log` trong `onmessage`, React DevTools     |

## 10. Đối chiếu tên topic cũ và mới

Code đang chạy có thể vẫn dùng tên cũ cho tới khi đổi sang tên mới (triển khai cho cả nhóm vào thứ 2, 26/10).

| Tên cũ                            | Tên mới                                  |
| --------------------------------- | ---------------------------------------- |
| `truong/khu{n}/mucday/{loai_rac}` | `school/area{n}/fill_level/{waste_type}` |
| `truong/khu{n}/phanloai`          | `school/area{n}/classification`          |
| `truong/khu{n}/trangthai/iot`     | `school/area{n}/status/iot`              |
| `truong/khu{n}/trangthai/ai`      | `school/area{n}/status/ai`               |
| `truong/khu{n}/khongchac`         | `school/area{n}/uncertain`               |

`waste_type` nhận ba giá trị `recyclable`, `organic`, `inorganic`; trường độ tin cậy là `confidence`.

## 11. Tự kiểm tra hiểu

Trả lời không nhìn tài liệu. Nếu vướng câu nào, quay lại mục tương ứng.

1. Vì sao Backend là chỗ tính % đầy chứ không phải ESP32 hay FE? (Mục 1 và 2.4: ESP gửi `d` thô, tính ở Backend để có một nơi giữ logic và ghi DB.)
2. EMQX có liên quan gì tới WebSocket của bạn? (Không. Nó chỉ nằm giữa thiết bị và Backend.)
3. Khác biệt giữa state và event trong MQTT, và mỗi loại xử lý ra sao? (Mục 2.5.)
4. `loop_start()` tạo ra điều gì và vì sao nó gây ra vấn đề thread? (Mục 4.)
5. Vì sao cần ConnectionManager? (Mục 3.3: MQTT cần gửi cho tất cả kết nối, route chỉ biết một.)
6. Vì sao dashboard dùng cả REST lẫn WebSocket? (Mục 5: snapshot lúc mount, delta về sau.)
7. Vì sao `classification_log` đề xuất đi bằng REST? (Mục 5: ảnh tới sau, filter và phân trang, không replay.)
8. Khi tắt đột ngột script giả lập IoT, dashboard biết nó offline bằng cơ chế nào? (LWT: broker tự publish tin offline, Backend nhận và broadcast `status`.)
