# MQTT — Danh sách topic & format JSON

> **Mục đích file này:** hợp đồng giao tiếp chính giữa 3 mảng AI/IoT/Web. Đây là file cả 3 người đều phải đọc và thống nhất trước khi bắt đầu code phần liên quan MQTT — mọi thay đổi format ở đây cần báo lại cho cả nhóm.

Liên quan: [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) · [Thiết kế IoT](../03-iot/thiet-ke-iot.md) · [Kiến trúc Backend realtime](../05-web/kien-truc-backend-realtime.md)

---

## Quy ước đặt tên

- Toàn bộ topic, tên trường và giá trị đều dùng **tiếng Anh**, viết thường. Topic ngăn cách bằng `/`, tên trường và giá trị ngăn cách bằng `_`.
- Mỗi khái niệm chỉ có **một tên duy nhất** đi xuyên suốt AI → MQTT → Backend/Database → API → Frontend. Ví dụ loại rác tái chế luôn là `recyclable` ở mọi nơi, không có dạng khác để phải ánh xạ.
- Việc hiển thị tiếng Việt (ví dụ `recyclable` → "Tái chế") do **Frontend** lo, thông qua một bảng map ở phía hiển thị.

## Cấu trúc topic

```
school/area{n}/fill_level/{waste_type}
school/area{n}/classification
school/area{n}/status/iot
school/area{n}/status/ai
school/area{n}/uncertain
```

Ví dụ khu vực 1:

```
school/area1/fill_level/recyclable
school/area1/fill_level/organic
school/area1/fill_level/inorganic
school/area1/classification
school/area1/status/iot
school/area1/status/ai
school/area1/uncertain
```

Dùng `waste_type` (không phải số bin_id) làm định danh topic vì trùng sẵn với enum `WasteType` trong database, dễ đọc log khi debug.

Mỗi `area` và `trash_bin` trong database lưu **nguyên chuỗi topic** của mình (các cột `mqtt_topic_*`). Backend dựa vào đó để biết một message thuộc khu vực hoặc thùng nào, nên chuỗi topic ở đây và chuỗi trong database phải khớp từng ký tự.

## Format JSON từng loại

### Mức đầy — `school/area{n}/fill_level/{waste_type}`

- Chiều: ESP32 → Broker → Backend
- QoS: 0

```json
{
  "distance_cm": 12.5,
  "timestamp": "2026-09-10T14:32:05+07:00"
}
```

### Kết quả phân loại thành công — `school/area{n}/classification`

- Chiều: AI script → Broker → ESP32 (subscribe) + Backend (subscribe)
- QoS: 1

```json
{
  "waste_type": "organic",
  "confidence": 0.87,
  "timestamp": "2026-09-10T14:32:07Z",
  "log_id": "uuid-tu-sinh"
}
```

### Trạng thái online/offline — `school/area{n}/status/iot` và `.../status/ai`

- Chiều: ESP32 hoặc AI script → Broker → Backend (subscribe), dùng cơ chế **LWT**
- QoS: 1, `retain=true`

```json
{ "status": "online" }
```

```json
{ "status": "offline" }
```

## Tín hiệu "không tự tin" — `school/area{n}/uncertain` (đã chốt phương án B)

Khi AI không đủ tự tin phân loại (không class nào đạt ngưỡng xuất hiện tối thiểu trong cửa sổ `DETECTING`), AI publish một tín hiệu riêng để ESP32 bật **LED đỏ của khu vực**. Hành vi đã chốt (xem [luồng nhận diện, mục 4](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md#4-trường-hợp-đặc-biệt--model-không-đủ-tự-tin)):

- Không kèm `waste_type` (vì không xác định được)
- Không kèm `log_id` (vì Backend không lưu gì cho trường hợp này, không cần ghép nối)
- **Backend không subscribe topic này**, chỉ ESP32 subscribe

```json
{
  "timestamp": "2026-09-10T14:32:07Z"
}
```

- **QoS:** chưa chốt. Đề xuất QoS 1 để ESP32 chắc chắn nhận được lệnh bật đèn đỏ; cần Vũ và Tường thống nhất.
- **Vì sao chọn phương án B (topic phụ):** tách bạch trách nhiệm, Backend hoàn toàn không phải biết tới tín hiệu này. Phương án A (thêm một field trạng thái vào topic `classification`) đã bị bỏ vì Backend cũng nhận message đó và phải nhớ bỏ qua đúng cách, nếu quên sẽ insert nhầm.
- Chi phí của phương án B: thêm một topic mới cần cập nhật vào danh sách này và vào cấu hình broker/firmware.

## Quy ước chung

- `timestamp`: chuẩn ISO 8601, giờ UTC
- `waste_type`: cố định 3 giá trị `recyclable`, `organic`, `inorganic` — dùng giống hệt nhau ở payload, đuôi topic `fill_level`, database và API
- `confidence`: số thực từ 0 đến 1
- QoS: mức đầy dùng QoS 0 (mất vài gói không sao), `classification` và `status` dùng QoS 1 (đảm bảo tới nơi)
- Bên publish (script AI) nên kiểm tra `waste_type` thuộc đúng 3 giá trị trên trước khi gửi; Backend bỏ qua và ghi log nếu nhận giá trị lạ

## LWT (Last Will and Testament)

Cơ chế để broker tự phát hiện khi 1 client (ESP32 hoặc script AI) rớt kết nối đột ngột (mất điện, đứt wifi, crash — không kịp báo offline bình thường):

1. Khi client kết nối tới broker, đăng ký sẵn "di chúc": nếu rớt kết nối đột ngột, broker tự publish `{"status": "offline"}` lên topic trạng thái thay cho client
2. Khi client kết nối lại bình thường → tự publish `{"status": "online"}` như message thường

**Lưu ý:** ESP32 và script AI là **2 client MQTT riêng biệt**, nên có LWT riêng — 2 trạng thái khác nhau (`status/iot` và `status/ai`) vì "phần cứng thùng rác mất kết nối" khác với "hệ thống nhận diện không chạy nữa".

## Thay đổi so với bản trước (21/10/2026)

Bảng này để cả nhóm sửa code theo. Sửa xong có thể xoá mục này.

| Bản cũ                                     | Bản mới                                              |
| ------------------------------------------ | ---------------------------------------------------- |
| `truong/khu{n}/...`                        | `school/area{n}/...`                                 |
| `.../mucday/{taiche\|huuco\|voco}`         | `.../fill_level/{recyclable\|organic\|inorganic}`    |
| `.../phanloai`                             | `.../classification`                                 |
| `.../trangthai/iot`, `.../trangthai/ai`    | `.../status/iot`, `.../status/ai`                    |
| `.../khongchac`                            | `.../uncertain`                                      |
| `loai_rac`: `tai_che` / `huu_co` / `vo_co` | `waste_type`: `recyclable` / `organic` / `inorganic` |
| `do_chac_chan` / `do_tin_cay`              | `confidence`                                         |

Ai cần sửa gì:

- **AI (Vũ):** topic publish, tên trường trong payload, và tên class của model khi train lại (xem file tổng quan, mục 4).
- **IoT (Tường):** topic publish `fill_level` và `status/iot`, topic subscribe `classification` và `uncertain`, cách đọc `waste_type` để chọn servo.
- **Web (Tuấn Anh):** seed data, các pattern subscribe ở Backend, và bảng map hiển thị tiếng Việt ở Frontend.
