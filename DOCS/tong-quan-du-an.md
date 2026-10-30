# Tổng quan dự án: Hệ thống phân loại rác thông minh trường học

Bản đọc nhanh để nắm toàn bộ dự án (AI, IoT, Web), cập nhật 21/10/2026.

## 1. Dự án làm gì

Khi có người bỏ rác vào khay của một khu vực, camera ghi hình, AI (YOLOv8n) nhận ra rác thuộc một trong ba loại: tái chế, hữu cơ, vô cơ. Kết quả được gửi qua MQTT để ESP32 mở đúng nắp thùng và bật đèn xanh. Nếu AI không đủ tự tin, ESP32 bật đèn đỏ để người dùng tự phân loại. Song song, cảm biến siêu âm đo mức đầy từng thùng. Web Dashboard cho người quản lý xem trạng thái thời gian thực, xem lịch sử phân loại có ảnh, xác nhận đúng/sai và xem thống kê.

- Quy mô demo: 2 khu vực × 3 thùng = 6 thùng.
- Thời gian: 9 tuần (08/09 đến 10/11/2026).
- Giảng viên hướng dẫn: thầy Nguyễn Hồ Hải.

## 2. Nhóm và phân vai

| Thành viên       | Vai trò  | Phụ trách                                                        |
| ---------------- | -------- | ---------------------------------------------------------------- |
| Tuấn Anh         | PM + Web | Backend FastAPI, Frontend React, database, tích hợp              |
| Lý Lâm Vũ        | AI       | Huấn luyện YOLOv8n, script AI đọc camera, publish MQTT, POST ảnh |
| Nguyễn Đức Tường | IoT      | Firmware ESP32: HC-SR04, servo, LED, MQTT                        |

Ba mảng gần như độc lập, chỉ nối với nhau qua hai thứ: file hợp đồng MQTT (`DOCS/06-mqtt`) và API nhận ảnh của Backend. Vì vậy mọi thay đổi format message đều phải báo cả nhóm.

## 3. Kiến trúc tổng thể

| Khối                          | Chạy ở đâu            | Việc chính                                                                              |
| ----------------------------- | --------------------- | --------------------------------------------------------------------------------------- |
| Script AI (Python)            | Máy tính chạy script  | Đọc camera bằng OpenCV, chạy YOLO, chốt kết quả, publish MQTT, POST ảnh                 |
| ESP32                         | Phần cứng tại khu vực | Đọc 3 cảm biến HC-SR04, publish khoảng cách; nhận lệnh phân loại, mở servo, bật LED     |
| MQTT broker (EMQX serverless) | Đám mây               | Trung gian: AI, IoT, Web không gọi trực tiếp nhau                                       |
| Backend FastAPI               | Server                | Subscribe MQTT, ghi PostgreSQL, nhận ảnh, upload Cloudinary, cung cấp REST và WebSocket |
| Frontend React (VTA-trash)    | Trình duyệt           | Đăng nhập, Dashboard, Lịch sử, Thống kê                                                 |
| PostgreSQL, Cloudinary        | Dịch vụ               | Lưu dữ liệu và lưu ảnh                                                                  |

Có hai kênh dữ liệu tách biệt: **MQTT** cho tin nhắn nhẹ cần realtime, và **HTTP** cho ảnh (nặng). Camera là điện thoại (IP Webcam hoặc DroidCam). Video không đi qua database hay MQTT.

### Một lượt bỏ rác đi qua hệ thống như thế nào

1. Người dùng đặt rác vào khay. Bước lọc frame differencing so khung hình hiện tại với ảnh nền khay trống; chỉ khi khay thay đổi đáng kể thì mới chạy YOLO.
2. AI vào trạng thái DETECTING. Trong cửa sổ khoảng 1,5 giây, AI đếm số lần mỗi class xuất hiện qua các frame.
3. Hết cửa sổ, class xuất hiện nhiều nhất thắng (nếu đạt ngưỡng xuất hiện tối thiểu). AI sinh `log_id` (UUID) và chọn frame có confidence cao nhất của class thắng làm ảnh lưu.
4. AI publish lên `school/area{n}/classification` (QoS 1) gồm `log_id`, `waste_type`, `confidence`, `timestamp`; đồng thời POST ảnh kèm `log_id` về Backend.
5. ESP32 nhận message: mở servo của thùng tương ứng, bật LED xanh, nắp tự đóng bằng timer nội bộ.
6. Backend nhận cùng message: insert một dòng `classification_log` với `image_url = NULL`.
7. Ảnh đến sau: Backend upload lên Cloudinary rồi cập nhật `image_url` theo `log_id`.
8. Dashboard và trang Lịch sử đọc dữ liệu từ Backend.

**Trường hợp không đủ tự tin:** AI publish một tín hiệu riêng lên `school/area{n}/uncertain`, ESP32 bật LED đỏ, Backend không subscribe topic này và không lưu gì.

## 4. Phần AI (Vũ)

- **Mô hình:** YOLOv8n fine-tune từ dataset Roboflow Universe, ba class: tái chế, hữu cơ, vô cơ.
- **Tên class:** phải trùng với giá trị `waste_type` dùng trong MQTT: `recyclable`, `organic`, `inorganic`. Hiện `data.yaml` đang ghi `inorganic-waste`, `organic-waste`, `recyclable-waste`; khi train lại thì đổi `names` thành `['inorganic', 'organic', 'recyclable']` (cùng thứ tự alphabet nên file label không phải sửa). Script AI nên kiểm tra tên class thuộc đúng ba giá trị này trước khi publish.
- **Frame differencing:** bước lọc đặt trước YOLO. Nếu khay không đổi so với ảnh nền thì bỏ qua, tiết kiệm tài nguyên và gần như loại bỏ phát hiện nhầm khi khay trống.
- **State machine:** IDLE → DETECTING → COOLDOWN. COOLDOWN là quãng nghỉ sau khi chốt để không nhận diện lại cùng một món rác.
- **Bỏ phiếu theo tần suất:** không lấy frame có confidence cao nhất, mà đếm class nào xuất hiện nhiều frame nhất. Cách này bền hơn trong môi trường nhiễu (một frame nhầm không làm hỏng kết quả).
- **`miss_count`:** đếm số frame liên tiếp không phát hiện được gì. Vượt ngưỡng thì huỷ phiên và về IDLE, không publish gì và không bật đèn. Đây là hành vi bình thường, ví dụ khi người dùng rút tay ra.
- **Không đủ tự tin:** hết cửa sổ mà không class nào đạt ngưỡng xuất hiện tối thiểu → publish lên topic `uncertain` để bật LED đỏ, không lưu log.
- **Sau khi chốt:** publish MQTT và POST ảnh bất đồng bộ để không chặn việc phân loại. Nếu POST lỗi mạng, ảnh và file metadata được lưu cục bộ theo `log_id`.

## 5. Phần IoT (Tường)

- Mỗi khu vực có 1 ESP32 điều khiển 3 thùng; mỗi thùng có 1 cảm biến HC-SR04 và 1 servo.
- 2 LED cho cả khu vực (không gắn theo thùng): **xanh** = AI phân loại thành công, **đỏ** = AI không đủ tự tin. Đã bỏ buzzer/loa.
- ESP32 publish liên tục khoảng cách d thô lên topic `fill_level`. Backend mới là nơi tính phần trăm đầy:

**% đầy = (H − d) / H × 100**, trong đó H là chiều cao thùng (`height_cm`), d là khoảng cách từ cảm biến đến mặt rác; kết quả giới hạn trong khoảng 0–100.

- Mỗi message trên `classification` được ESP32 coi là lệnh mở servo theo `waste_type`. Nắp tự đóng bằng timer cố định, không có lệnh đóng qua MQTT.
- ESP32 subscribe thêm `uncertain` để bật LED đỏ.
- ESP32 và script AI là hai client MQTT riêng nên có LWT riêng.

## 6. MQTT: hợp đồng giữa ba mảng

| Topic                                             | Chiều                 | QoS                   | Nội dung                                          |
| ------------------------------------------------- | --------------------- | --------------------- | ------------------------------------------------- |
| `school/area{n}/fill_level/{waste_type}`          | ESP32 → Backend       | 0                     | `distance_cm`, `timestamp`                        |
| `school/area{n}/classification`                   | AI → ESP32 và Backend | 1                     | `waste_type`, `confidence`, `timestamp`, `log_id` |
| `school/area{n}/status/iot`                       | ESP32 → Backend       | 1, retain             | `{"status": "online"}` hoặc offline               |
| `school/area{n}/status/ai`                        | Script AI → Backend   | 1, retain             | như trên                                          |
| `school/area{n}/uncertain` (phương án B, đã chốt) | AI → ESP32            | chưa chốt (đề xuất 1) | `timestamp`; Backend không subscribe              |

Quy ước đặt tên:

- Toàn bộ topic, tên trường và giá trị dùng tiếng Anh. Mỗi khái niệm chỉ có một tên đi suốt từ AI → MQTT → database → API → Frontend, nên Backend không phải ánh xạ gì.
- `waste_type` luôn là một trong ba giá trị `recyclable`, `organic`, `inorganic`, kể cả ở đuôi topic `fill_level`.
- Việc hiển thị tiếng Việt do Frontend lo bằng một bảng map (ví dụ `recyclable` → "Tái chế").
- Tên trường độ tin cậy là `confidence` ở mọi nơi, khớp với cột trong database.
- Mỗi `area` và `trash_bin` lưu **toàn bộ chuỗi topic** của mình trong database, không ghép từ tiền tố.

**Các khái niệm MQTT cần nắm:**

- **QoS 0**: gửi một lần, có thể mất (dùng cho mức đầy vì mất vài gói không sao). **QoS 1**: đảm bảo tới nơi ít nhất một lần, có thể bị giao trùng (dùng cho phân loại và trạng thái).
- **Retain**: broker giữ lại message cuối cùng của topic, client mới subscribe sẽ nhận ngay trạng thái hiện tại.
- **LWT (Last Will and Testament)**: khi kết nối, client nhờ broker giữ sẵn một «di chúc». Nếu client rớt đột ngột (mất điện, đứt wifi), broker tự publish offline thay nó. Khi kết nối lại client tự publish online.
- Trạng thái IoT và AI tách riêng vì «phần cứng thùng rác mất kết nối» khác với «hệ thống nhận diện không chạy nữa».

## 7. Luồng ảnh (đã chốt, không đổi)

- MQTT `classification` chỉ mang metadata nhẹ, nên ESP32 mở nắp ngay lập tức.
- Ảnh đi bằng HTTP POST multipart riêng, kèm `log_id`, xác thực bằng header `X-API-Key` (khoá tĩnh lưu trong `.env` của AI và Backend). Khoá tĩnh phù hợp hơn JWT cho máy gọi máy chạy liên tục 24/7.
- Backend upload Cloudinary, lưu `image_url` và `cloudinary_public_id`, cập nhật dòng theo `log_id`.
- Thiết kế chấp nhận MQTT thường tới trước, ảnh tới sau.
- **Vì sao không gộp ảnh vào MQTT:** code multipart phức tạp hơn; nếu gộp thì một lỗi mạng sẽ mất luôn cả dòng dữ liệu, còn khi tách thì chỉ mất ảnh.
- **POST ảnh lỗi:** AI lưu ảnh và file metadata cục bộ; không retry tự động; người quản lý tự tải ảnh lên lại thủ công trên giao diện. Backend không có enum trạng thái ảnh, dòng thiếu ảnh được nhận biết bằng `image_url IS NULL`.

## 8. Cơ sở dữ liệu (PostgreSQL, SQLAlchemy ORM, Alembic)

| Bảng                 | Cột chính                                                                                                                                                                  | Ghi chú                                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `account`            | `id`, `username`, `email`, `password_hash`                                                                                                                                 | `username` và `email` duy nhất; chỉ có một loại tài khoản quản lý                               |
| `area`               | `id`, `location_description`, `mqtt_topic_classification`, `mqtt_topic_status_iot`, `mqtt_topic_status_ai`, `iot_online`, `ai_online`, `iot_last_online`, `ai_last_online` | Mỗi topic duy nhất; trạng thái online của IoT và AI tách riêng, cập nhật qua LWT                |
| `trash_bin`          | `id`, `area_id`, `waste_type`, `mqtt_topic_fill_level`, `height_cm`, `current_fill_percent`, `updated_at`                                                                  | Mức đầy **ghi đè tại chỗ**, không lưu lịch sử theo thời gian                                    |
| `classification_log` | `id`, `log_id`, `area_id`, `detected_waste_type`, `confidence`, `image_url`, `cloudinary_public_id`, `confirmation_result`, `created_at`                                   | `id` tự tăng là khoá chính; `log_id` (chuỗi 36 ký tự) do AI sinh, chỉ dùng để ghép MQTT với ảnh |
| `refresh_token`      | `id`, `account_id`, `token_hash`, `expires_at`, `created_at`, `revoked`                                                                                                    | Chỉ lưu bản băm của refresh token; xoá theo khi xoá account                                     |

**Vai trò các cột topic:** đây là bảng tra từ topic ra đối tượng. Message MQTT không mang `area_id`, Backend chỉ biết topic mà message đi qua. Khi có message đến, Backend tìm dòng có cột topic khớp chuỗi đó rồi lấy id:

- `classification` → tìm `area` theo `mqtt_topic_classification` → lấy `area_id` để insert `classification_log`.
- `status/iot`, `status/ai` → tìm `area` theo `mqtt_topic_status_iot` hoặc `mqtt_topic_status_ai` → cập nhật trạng thái online của khu vực đó.
- `fill_level/{waste_type}` → tìm `trash_bin` theo `mqtt_topic_fill_level` → ghi đè `current_fill_percent`.

Nguyên tắc: tin nhắn thuộc cấp nào thì cột topic nằm ở bảng cấp đó. Phân loại và trạng thái theo khu vực (camera nhìn cả khay), mức đầy theo thùng (mỗi thùng một cảm biến). Vì vậy các cột topic đều `unique`. Topic `uncertain` không có cột nào vì Backend không subscribe.

Các enum trong code:

- `WasteType`: `recyclable`, `organic`, `inorganic`. Giá trị này **trùng hoàn toàn** với `waste_type` trong MQTT nên Backend dùng thẳng, không cần ánh xạ.
- `ConfirmationResult`: `unconfirmed` (mặc định), `correct`, `incorrect`.

Quan hệ: một `area` có nhiều `trash_bin` và nhiều `classification_log`; một `account` có nhiều `refresh_token`.

## 9. Backend FastAPI

Backend đóng bốn vai trò cùng lúc:

1. **MQTT subscriber** (thư viện paho-mqtt chạy ở thread riêng): subscribe theo ba pattern `school/+/fill_level/+`, `school/+/classification`, `school/+/status/+`.
   - `fill_level`: tính % đầy rồi ghi đè `current_fill_percent` và `updated_at`.
   - `classification`: insert `classification_log` với `image_url = NULL`.
   - `status`: cập nhật `iot_online` hoặc `ai_online` và `*_last_online`.
   - Message có `waste_type` ngoài ba giá trị hợp lệ thì bỏ qua và ghi log.
2. **Cổng nhận ảnh** cho script AI, xác thực bằng `X-API-Key` (một dependency riêng, độc lập với JWT).
3. **REST API** cho Frontend: dashboard lần đầu, lịch sử có phân trang và bộ lọc, xác nhận đúng/sai, xoá hàng loạt dòng thiếu ảnh, tải ảnh lên lại, thống kê. Bảo vệ bằng JWT.
4. **WebSocket server** `/ws/dashboard`: đẩy thay đổi realtime xuống Frontend.

**Xác thực:** access token (sống ngắn) lưu trong bộ nhớ ở hook React; refresh token lưu ở cookie và có bản băm trong bảng `refresh_token`.

**Cầu nối MQTT → WebSocket:**

- Callback của paho chạy ở thread khác với event loop của FastAPI, nên không gọi thẳng hàm async `broadcast()` được.
- Dùng `asyncio.run_coroutine_threadsafe(coro, loop)`: đóng gói coroutine từ thread MQTT rồi đẩy an toàn vào event loop chính.
- `ConnectionManager` giữ danh sách WebSocket đang mở, có `connect`, `disconnect`, `broadcast`.
- Message gửi xuống Frontend bọc dạng `{type, ...}` thay vì giữ nguyên payload MQTT.
- Route WebSocket khác route HTTP: hàm không return mà sống trong vòng lặp suốt vòng đời kết nối.
- JWT gắn vào query string lúc kết nối (xem phần hạn chế).

## 10. Frontend React (VTA-trash)

- **Trang:** Đăng nhập, Dashboard (6 thùng: % đầy, trạng thái online/offline của IoT và AI tách riêng), Lịch sử phân loại (ảnh, bộ lọc, xác nhận đúng/sai, chọn nhiều để xoá dòng thiếu ảnh, tải ảnh lên lại), Thống kê (theo loại, khu vực, thời gian, độ chính xác model theo ngày).
- **Hiển thị tiếng Việt:** dữ liệu từ Backend luôn là giá trị tiếng Anh (`recyclable`, `unconfirmed`...). Frontend giữ một bảng map để đổi sang tiếng Việt khi hiển thị, ví dụ `recyclable` → "Tái chế".
- **Pattern dữ liệu:** REST để tải lần đầu, truy vấn lịch sử và các hành động ghi; WebSocket chỉ gửi phần thay đổi (delta) sau đó.
- **WebSocket phía trình duyệt:** dùng API gốc `new WebSocket(url)` (không dùng axios). Không có response, chỉ có sự kiện `onopen`, `onmessage` (chạy mỗi lần Backend broadcast), `onclose`, `onerror`. Mở kết nối trong `useEffect` và bắt buộc `ws.close()` ở cleanup. Cần tự làm reconnect vì WebSocket có khái niệm mất kết nối giữa chừng.
- Backend chạy HTTPS local (mkcert), nên Frontend kết nối bằng `wss://`.

## 11. Khái niệm AI giải thích đơn giản

- **CNN:** mạng nơ-ron học các đặc trưng của ảnh (cạnh, màu, hình dạng) qua nhiều lớp tích chập.
- **YOLO (You Only Look Once):** mô hình phát hiện đối tượng, nhìn ảnh một lần và đưa ra các hộp bao kèm class và confidence. Bản n (nano) nhỏ và nhanh, phù hợp chạy realtime.
- **Phát hiện đối tượng khác phân loại ảnh:** phân loại chỉ trả lời «ảnh này là gì», phát hiện trả lời thêm «ở đâu trong ảnh».
- **IoU:** độ chồng lấn giữa hộp dự đoán và hộp thật (diện tích giao / diện tích hợp).
- **Precision:** trong số những lần mô hình báo «đúng», bao nhiêu lần thật sự đúng. **Recall:** trong số vật thật có mặt, mô hình bắt được bao nhiêu.
- **mAP@0,5:** điểm trung bình trên các class, tính một dự đoán là đúng khi IoU từ 0,5 trở lên. Đây là chỉ số chính để đánh giá mô hình phát hiện đối tượng; **accuracy** thường không dùng cho loại bài toán này.
- **Hàm mất mát trong biểu đồ Ultralytics:** `box_loss` (sai lệch vị trí hộp), `cls_loss` (sai class), `dfl_loss` (độ chính xác biên hộp). Mất mát giảm dần qua các epoch là dấu hiệu huấn luyện tốt.
- **Epoch:** một lượt học qua toàn bộ tập huấn luyện. Dừng sớm (early stopping) là dừng khi mô hình không cải thiện thêm.

## 12. Các quyết định đã chốt và lý do

| Quyết định                                                                                       | Lý do                                                            |
| ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| Tách MQTT (tin nhẹ) và HTTP (ảnh)                                                                | Servo phản hồi ngay; lỗi mạng không làm mất cả dòng dữ liệu      |
| `log_id` do AI tự sinh                                                                           | Không phải chờ Backend trả ID về, không bị chặn lúc phân loại    |
| Bỏ phiếu theo tần suất thay vì confidence đơn khung                                              | Bền hơn khi nhiễu                                                |
| Frame differencing trước YOLO                                                                    | Tiết kiệm tài nguyên, bớt phát hiện nhầm khi khay trống          |
| Chỉ một loại tài khoản quản lý, không RBAC                                                       | Giữ phạm vi khả thi                                              |
| Mức đầy ghi đè, không lưu chuỗi thời gian                                                        | Đơn giản; đồ án không cần lịch sử mức đầy                        |
| Không retry tự động khi POST ảnh lỗi, không có enum trạng thái ảnh                               | Đơn giản hoá có chủ đích                                         |
| Bỏ buzzer/loa, đèn LED gắn theo khu vực                                                          | Giảm phần cứng                                                   |
| API key tĩnh cho AI → Backend                                                                    | Máy gọi máy, chạy liên tục                                       |
| Tín hiệu không tự tin: phương án B (topic phụ `uncertain`)                                       | Backend hoàn toàn không phải biết tới tín hiệu này               |
| Models gộp một file `app/models/models.py`                                                       | Tránh import vòng giữa các bảng quan hệ hai chiều                |
| Một bộ tên tiếng Anh duy nhất cho MQTT, database, API; Frontend map sang tiếng Việt khi hiển thị | Bỏ các bước ánh xạ giữa các tầng, giảm lỗi lệch tên giữa ba mảng |

## 13. Hạn chế đã biết và câu hỏi có thể bị hỏi

- **Ảnh đến trước MQTT thì sao?** Thiết kế mới chỉ giả định MQTT tới trước. Trường hợp ngược lại (chưa có dòng để cập nhật) chưa được xử lý; nên thừa nhận đây là hạn chế đã biết.
- **QoS 1 có thể giao trùng:** `log_id` là duy nhất nên insert trùng sẽ lỗi; Backend cần bắt lỗi này và bỏ qua.
- **JWT qua query string:** token có thể lọt vào log và URL. Chấp nhận cho đồ án; cách tốt hơn là gửi token ở message đầu tiên sau khi mở kết nối hoặc dùng ticket ngắn hạn.
- **Mất mạng khi gửi ảnh:** ảnh được giữ cục bộ, không retry tự động; quản lý tải lên lại thủ công.
- **Model phân loại sai:** người quản lý đánh dấu đúng/sai ở trang Lịch sử; số liệu đó dùng cho thống kê độ chính xác theo ngày.
- **Vật lạ hoặc bị che khuất:** nếu YOLO không phát hiện gì thì hệ thống im lặng và về IDLE; đèn đỏ chỉ bật khi có phát hiện nhưng không class nào đủ ngưỡng.
- **Hai trạng thái online tách riêng:** để biết lỗi nằm ở phần cứng hay ở hệ thống nhận diện.
