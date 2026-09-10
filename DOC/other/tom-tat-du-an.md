# Note tổng hợp — Hệ thống quản lý & phân loại rác thải thông minh trường học

> File này tổng hợp toàn bộ quyết định đã thống nhất tính đến hiện tại (bao gồm cả phần đã chốt trước đó và phần vừa đào sâu về Web). Một số mục vẫn còn "chưa chốt" — đã đánh dấu rõ để nhóm bàn tiếp.

---

## 1. Tổng quan đề tài

Xây dựng hệ thống quản lý và phân loại rác thải thông minh tại trường học, ứng dụng nhận diện hình ảnh (Deep Learning) để phân loại rác qua camera, tự động mở đúng ngăn thùng tương ứng. Cảm biến khoảng cách giám sát mức độ đầy của từng thùng theo thời gian thực. Website trung tâm thu thập dữ liệu qua MQTT, hiển thị dashboard trạng thái, lịch sử phân loại và thống kê. Do giới hạn chi phí, demo triển khai trên **2 khu vực**, mỗi khu vực **3 thùng** (tái chế / hữu cơ / vô cơ).

**Phân công nhóm:** 1 bạn AI/CNN, 1 bạn IoT, 1 bạn Web (bạn).

---

## 2. Phần cứng — sơ đồ 1 khu vực

Mỗi khu vực gồm:

- **1 camera điện thoại** chạy app IP Webcam/DroidCam → phát luồng video qua địa chỉ dạng `http://ip:port/video`
- **1 ESP32** điều khiển chung 3 thùng trong khu vực đó
- Mỗi thùng (3 thùng/khu vực) có:
  - 1 cảm biến khoảng cách **HC-SR04** → đo mức đầy
  - 1 **servo** → mở nắp tự động

→ Tổng 2 khu vực = 2 camera + 2 ESP32 + 6 thùng + 6 cảm biến + 6 servo.

---

## 3. Cấu trúc thư mục dự án

```
project-root/
├── web/            (FE + BE, do bạn Web phụ trách)
├── ai-vision/       (script cv2 + model detect, do bạn AI phụ trách)
│   ├── khu1.py      (hoặc 1 script nhận tham số --zone=1)
│   └── khu2.py
└── iot-firmware/    (code Arduino/ESP32, do bạn IoT phụ trách)
```

**Mô hình chạy khi demo:**

- 4 process độc lập, mỗi cái 1 terminal: **MQTT broker (Mosquitto)**, **Web BE**, **Web FE**, **Script AI**
- Threading chỉ xuất hiện **bên trong** script AI, dùng để đọc song song 2 luồng camera (2 khu vực) trong cùng 1 script, không cần multiprocessing

---

## 4. AI / CNN

- Model: YOLOv8n, fine-tune từ dataset fork trên Roboflow Universe
- Input: camera điện thoại → stream qua IP Webcam/DroidCam → đọc bằng OpenCV (`cv2.VideoCapture`)
- Phân loại 3 lớp: **tái chế / hữu cơ / vô cơ**
- Độ chính xác mục tiêu: 80–85%
- Retrain: không bắt buộc làm thật, chỉ nêu ở phần "hướng phát triển"
- Máy xử lý AI: Laptop Asus TUF A15 FA507NU (Ryzen 5 7035HS, RTX 4050) — 1 máy xử lý cả 2 khu vực cùng lúc, chạy CUDA, dùng threading đọc 2 camera song song

### Luồng xử lý khi detect xong 1 frame (chạy tuần tự, không cần song song thật sự)

```python
# Sau khi detect xong: label, confidence, frame

# Bước 1: publish kết quả phân loại lên MQTT (nhanh, vài chục byte)
mqtt_client.publish("truong/khu1/phanloai", json.dumps({
    "loai_rac": label,
    "do_chac_chan": confidence,
    "timestamp": now_iso,
    "log_id": log_id
}))

# Bước 2: encode + gửi ảnh qua HTTP (chậm hơn chút vì ảnh nặng hơn)
_, buffer = cv2.imencode('.jpg', frame)
requests.post(
    "http://backend-url/api/anh-phan-loai",
    files={"anh": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
    data={"log_id": log_id}
)
```

- 2 việc này chạy nối tiếp trong code, không phải song song thật — nhưng đủ nhanh nên không đáng lo về độ trễ
- `log_id` do script AI tự sinh (uuid), gắn vào cả MQTT và request ảnh, dùng để backend ghép 2 luồng dữ liệu độc lập (MQTT + HTTP) lại thành 1 bản ghi duy nhất

### Video stream — không đi qua DB/MQTT

Luồng camera chỉ được script AI đọc trực tiếp và xử lý nội bộ. Web **không biết và không cần biết** gì về luồng video này — trách nhiệm của Web chỉ bắt đầu từ lúc script AI gửi **kết quả** (MQTT) và **ảnh 1 frame** (HTTP).

---

## 5. IoT (phần cứng mỗi khu vực)

- ESP32: subscribe kết quả phân loại từ MQTT → điều khiển servo mở đúng ngăn
- HC-SR04: đo khoảng cách liên tục → publish khoảng cách thô lên MQTT
- Servo: mở ngăn thùng tương ứng theo lệnh nhận được

### Cơ chế tính % đầy (logic nằm ở Web/BE, không phải ESP32)

- `H` = khoảng cách từ cảm biến đến đáy thùng khi rỗng (đo 1 lần, lưu cố định trong DB — cột `chieu_cao_H_cm` của từng thùng, vì 3 thùng có thể cao khác nhau)
- `d` = khoảng cách đo được tại thời điểm hiện tại (ESP32 publish thô, không tự tính %)
- **% đầy = (H − d) / H × 100**

→ Quyết định: ESP32 chỉ publish `d` thô, **Web tính %** — để dễ sửa công thức (lọc nhiễu, làm mượt số liệu...) sau này mà không cần flash lại firmware.

### Tần suất publish mức đầy

**10 giây/lần** — hợp lý vì:

- Mức đầy thay đổi chậm, không cần cập nhật dày
- Tiết kiệm tài nguyên phần cứng (pin, wifi) nếu sau này chạy không cắm điện
- Dễ debug/theo dõi log khi demo

Riêng **kết quả phân loại** thì gửi ngay khi có (event-based), không theo lịch cố định, vì cần phản hồi tức thời để mở đúng ngăn.

---

## 6. Giao tiếp hệ thống — MQTT

MQTT broker (Mosquitto) làm trung gian, tách rời hoàn toàn AI / IoT / Web — mỗi thành phần chỉ cần thống nhất tên topic và format JSON, không phụ thuộc code lẫn nhau.

### Cấu trúc topic

```
truong/khu{n}/mucday/{loai_rac}
truong/khu{n}/phanloai
truong/khu{n}/trangthai/iot
truong/khu{n}/trangthai/ai
```

Ví dụ khu vực 1:

```
truong/khu1/mucday/taiche
truong/khu1/mucday/huuco
truong/khu1/mucday/voco
truong/khu1/phanloai
truong/khu1/trangthai/iot
truong/khu1/trangthai/ai
```

Dùng `loai_rac` (không phải số bin_id) làm định danh topic vì khớp sẵn với enum trong DB, dễ đọc log khi debug.

### Format JSON từng loại

**Mức đầy** — `truong/khu{n}/mucday/{loai_rac}`

```json
{
  "distance_cm": 12.5,
  "timestamp": "2026-09-10T14:32:05Z"
}
```

**Kết quả phân loại** — `truong/khu{n}/phanloai`

```json
{
  "loai_rac": "huu_co",
  "do_chac_chan": 0.87,
  "timestamp": "2026-09-10T14:32:07Z",
  "log_id": "uuid-tu-sinh"
}
```

**Trạng thái online/offline** — `truong/khu{n}/trangthai/iot` và `.../ai`

```json
{ "status": "online" }
```

```json
{ "status": "offline" }
```

### Quy ước chung

- `timestamp`: chuẩn ISO 8601, giờ UTC
- `loai_rac`: cố định 3 giá trị `tai_che`, `huu_co`, `vo_co` — viết liền không dấu, khớp enum DB
- QoS: mức đầy dùng QoS 0 (mất vài gói không sao), `phanloai` và `trangthai` dùng QoS 1 (đảm bảo tới nơi)

### LWT (Last Will and Testament)

Cơ chế để broker tự phát hiện khi 1 client (ESP32 hoặc script AI) rớt kết nối đột ngột (mất điện, đứt wifi, crash — không kịp báo offline bình thường):

1. Khi client kết nối tới broker, đăng ký sẵn "di chúc": nếu rớt kết nối đột ngột, broker tự publish `{"status": "offline"}` lên topic trạng thái thay cho client
2. Khi client kết nối lại bình thường → tự publish `{"status": "online"}` như message thường

**Lưu ý:** ESP32 và script AI là **2 client MQTT riêng biệt**, nên có LWT riêng — 2 trạng thái khác nhau (`trangthai/iot` và `trangthai/ai`) vì "phần cứng thùng rác mất kết nối" khác với "hệ thống nhận diện không chạy nữa".

⚠️ **Chưa chốt:** có cần tách 2 cột `iot_online` / `ai_online` riêng trong DB hay gộp chung 1 cột trạng thái cho đơn giản — tuỳ mức độ chi tiết muốn hiển thị trên dashboard.

---

## 7. Web — Tech stack

- **Frontend:** React JS
- **Backend:** FastAPI (sync)
- **Database:** PostgreSQL (dùng ORM, không viết SQL thuần)
- **Auth:** JWT — access token lưu ở `useState`, refresh token lưu cookie nếu cần (cân nhắc bỏ nếu chỉ demo ngắn)
- **Lưu ảnh:** Cloudinary

## 8. Web — Phạm vi chức năng đã chốt (bản rút gọn, bỏ vai trò nhân viên)

### Người quản lý (giao diện chính)

- Xem tổng quan 6 thùng theo 2 khu vực: % đầy, vừa phân loại rác gì
- Xem lịch sử phân loại (kèm ảnh)
- Xem thống kê theo lịch sử phân loại (ngày/tuần, theo loại rác, theo khu vực)
- Xác nhận thủ công đúng/sai cho từng log phân loại (xem đề xuất bên dưới)

### Hệ thống (chạy nền, không phải giao diện)

- BE subscribe MQTT liên tục, cập nhật trạng thái (ghi đè, không lưu lịch sử mức đầy)
- BE đẩy dữ liệu realtime qua WebSocket cho FE (mức đầy + online/offline)

### Đề xuất: đánh giá đúng/sai từng log phân loại

- Vì thùng mở hoàn toàn dựa vào kết quả model (không có cơ chế kiểm chứng độc lập), nên bổ sung 1 cột `ket_qua_xac_nhan` (chưa xác nhận / đúng / sai) — người quản lý xem ảnh, xác nhận thủ công bằng nút bấm đơn giản
- Giá trị: cho phép vẽ biểu đồ "độ chính xác model theo ngày" — chi phí thêm rất thấp, giá trị demo cao

---

## 9. Web — Thiết kế Database

```
tai_khoan (id, ten_dang_nhap, mat_khau_hash)

khu_vuc (
  id,
  mo_ta_vi_tri,
  mqtt_topic_phanloai,        -- full topic, vd: truong/khu1/phanloai
  mqtt_topic_trangthai_iot,   -- full topic, vd: truong/khu1/trangthai/iot
  mqtt_topic_trangthai_ai,    -- full topic, vd: truong/khu1/trangthai/ai
  iot_online          BOOLEAN,
  ai_online           BOOLEAN,
  iot_lan_cuoi_online TIMESTAMP,
  ai_lan_cuoi_online  TIMESTAMP
)

enum loai_rac (tai_che, huu_co, vo_co)

thung_rac (
  id,
  khu_vuc_id,
  loai_rac,
  mqtt_topic_mucday,            -- full topic riêng của từng thùng, vd: truong/khu1/mucday/huuco
  chieu_cao_H_cm,                -- dùng để tính % đầy
  phan_tram_day_hien_tai,        -- ghi đè, KHÔNG lưu lịch sử theo thời gian
  cap_nhat_luc
)

lich_su_phan_loai (
  id            SERIAL PRIMARY KEY,   -- dùng join/hiển thị/phân trang bình thường
  log_id        VARCHAR UNIQUE,        -- chỉ để ghép nối MQTT + ảnh (script AI tự sinh uuid)
  khu_vuc_id,
  loai_rac_nhan_dien,
  do_chac_chan,
  url_anh                          NULL,   -- null tạm tới khi ảnh HTTP về
  cloudinary_public_id             NULL,
  ket_qua_xac_nhan  enum (chua_xac_nhan / dung / sai),
  thoi_gian
)
```

**Nguyên tắc quan trọng:**

- `thung_rac` chỉ có đúng 6 dòng cố định (3 thùng × 2 khu vực), **không bao giờ tăng thêm** — mức đầy được **UPDATE ghi đè**, không insert dòng mới mỗi lần MQTT gửi
- Chỉ `lich_su_phan_loai` tăng dòng theo thời gian, và chỉ khi có 1 lần phân loại thật sự xảy ra (không phải mỗi lần đo mức đầy)
- `iot_online` / `ai_online` tách riêng 2 cột, vì ESP32 và script AI là 2 MQTT client độc lập, có LWT riêng — "phần cứng mất kết nối" khác với "hệ thống nhận diện không chạy"

**Về cách lưu topic (đã chốt):** thay vì lưu 1 `prefix` chung rồi để BE tự nối chuỗi ra topic con, mỗi đối tượng (`khu_vuc`, `thung_rac`) tự lưu sẵn **full topic đầy đủ** của chính nó. BE khi cần subscribe/publish chỉ đọc thẳng cột tương ứng ra dùng, không cần logic nối chuỗi. Đánh đổi: nếu sau này đổi quy tắc đặt tên topic hàng loạt thì phải sửa từng dòng trong DB — nhưng với quy mô 6 thùng + 2 khu vực, không đáng lo.

---

## 10. Web — Luồng ảnh (cv2 → Backend → Cloudinary)

**Bên AI:** encode frame (`cv2.imencode`) → POST `multipart/form-data` kèm `log_id` lên endpoint backend.

**Bên Backend (FastAPI):**

1. Nhận `UploadFile` qua endpoint riêng (vd `/api/anh-phan-loai`)
2. Upload thẳng bytes lên Cloudinary (không lưu file tạm ra ổ đĩa)
3. Nhận `secure_url` từ Cloudinary
4. `UPDATE lich_su_phan_loai SET url_anh=..., cloudinary_public_id=... WHERE log_id=...`

**Ghép nối 2 luồng độc lập (MQTT tới trước, ảnh tới sau):**

1. MQTT (topic `phanloai`) tới trước → BE **tạo dòng mới** trong `lich_su_phan_loai`, cột ảnh để `NULL` tạm
2. HTTP ảnh tới sau → BE tìm đúng dòng theo `log_id`, **UPDATE** thêm `url_anh`

→ Nếu ảnh bị lỗi/mất giữa chừng, dòng lịch sử vẫn tồn tại đầy đủ nhãn phân loại, chỉ thiếu ảnh — chấp nhận được vì nhãn là dữ liệu quan trọng nhất cho thống kê.

**Vì sao dùng `log_id` (uuid) thay vì đợi `id` auto-increment:** script AI cần 1 mã định danh **trước khi** bản ghi tồn tại trong DB, để gắn cùng 1 mã vào cả MQTT lẫn ảnh mà không biết trước bên nào tới trước. `id` tự tăng chỉ có sau khi insert nên không dùng được cho việc này. Vẫn giữ `id` SERIAL làm khóa chính bình thường, `log_id` chỉ là cột phụ có index, dùng để ghép nối và debug.

---

## 11. Web — MQTT ↔ WebSocket ↔ FE

### Vì sao không để FE tự subscribe MQTT trực tiếp

Trình duyệt không nói được giao thức MQTT thuần (TCP) — phải qua thêm 1 lớp MQTT-over-WebSocket và public broker ra ngoài, phức tạp không cần thiết cho quy mô đồ án.

### Luồng đúng

```
ESP32/Script AI → publish → MQTT Broker → BE subscribe
    → BE UPDATE DB (ghi đè, không lưu lịch sử mức đầy)
    → BE đẩy qua WebSocket → FE cập nhật UI ngay, không cần F5
```

BE đóng đồng thời 2 vai trò: **MQTT subscriber** và **WebSocket server** cho FE, chạy trong cùng 1 process backend.

### Kết hợp REST + WebSocket trên FE (dùng cả 2, không phải chọn 1)

- **Lúc mới load trang:** gọi REST `GET /api/thung-rac` để lấy toàn bộ trạng thái hiện có (giống code `useEffect` + `fetch` thông thường)
- **Sau khi trang đã load:** mở thêm 1 kết nối WebSocket, chỉ nhận **cập nhật lẻ tẻ** khi có thùng nào đổi số — không cần gửi lại toàn bộ danh sách mỗi lần

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

**Lý do cần lưu `trang_thai_online` + `lan_cuoi_online` vào DB:** LWT chỉ bắn 1 lần duy nhất tại đúng thời điểm rớt mạng. Người mở trang sau (hoặc F5) sẽ bỏ lỡ sự kiện đó nếu không có DB để tra lại trạng thái mới nhất.

---

## 12. Cách tổ chức Git giữa 3 thành viên

- **1 repo chung duy nhất** (không phải 3 repo riêng), khớp với cấu trúc thư mục `web/`, `ai-vision/`, `iot-firmware/` — mỗi người chỉ động vào folder của mình, ít giẫm chân nhau
- **Nhánh:** mỗi người 1 nhánh riêng theo tên mảng (`web`, `ai-vision`, `iot-firmware`), push thường xuyên lên nhánh của mình (không cần đợi xong hết mới push). Khi phần nào chạy ổn, tạo Pull Request merge vào `main`
- **`.gitignore`** cần có ngay từ đầu, bỏ qua đúng loại file rác từng mảng:

  ```
  # Web
  node_modules/
  .env
  __pycache__/
  venv/

  # AI
  *.pt
  runs/

  # IoT
  .pio/
  ```

- **Quan trọng:** file `.env` (chứa mật khẩu DB, API key Cloudinary...) tuyệt đối không push lên GitHub. Tạo `.env.example` (chỉ có tên biến, không có giá trị thật) để đồng đội biết cần khai báo gì
- Vì bạn phụ trách Web 1 mình, rủi ro conflict code gần như không có — điều quan trọng hơn là thống nhất đúng API/MQTT contract (đã có ở mục 6 và 10) để 2 bạn kia biết chính xác cần gửi dữ liệu dạng gì

## 13. Đã chốt (đợt cập nhật gần nhất)

- Chip IoT chính thức: **ESP32**
- Trạng thái online/offline: **tách riêng** `iot_online` và `ai_online`, không gộp chung
- Cách lưu MQTT topic: mỗi `khu_vuc` và `thung_rac` tự lưu **full topic** của chính nó (xem mục 9), không dùng prefix nối chuỗi

## 14. Việc chưa chốt (cần nhóm bàn tiếp)

- [ ] Kiểm tra băng thông WiFi khi 2 luồng camera stream cùng lúc — nên test trực tiếp tại địa điểm demo: mở cả 2 app stream cùng lúc, xem laptop nhận hình có mượt/đứng hình không. Việc này thuộc phần AI/IoT xử lý (giảm độ phân giải stream nếu mạng yếu), Web không cần can thiệp
- [x] 2 điện thoại + laptop cùng mạng WiFi khi demo — đã xác nhận ổn, vẫn nên test lại đúng tại địa điểm demo trước ngày báo cáo vì WiFi trường có thể chặn giao tiếp thiết bị

---

_File này tổng hợp các quyết định tính tới thời điểm hiện tại — nên cập nhật lại khi nhóm chốt thêm các mục còn treo ở trên._
