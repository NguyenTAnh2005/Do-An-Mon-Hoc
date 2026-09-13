# MQTT — Danh sách topic & format JSON

> **Mục đích file này:** hợp đồng giao tiếp chính giữa 3 mảng AI/IoT/Web. Đây là file cả 3 người đều phải đọc và thống nhất trước khi bắt đầu code phần liên quan MQTT — mọi thay đổi format ở đây cần báo lại cho cả nhóm.

Liên quan: [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) · [Thiết kế IoT](../03-iot/thiet-ke-iot.md) · [Kiến trúc Backend realtime](../05-web/kien-truc-backend-realtime.md)

---

## Cấu trúc topic

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

## Format JSON từng loại

### Mức đầy — `truong/khu{n}/mucday/{loai_rac}`

- Chiều: ESP32 → Broker → Backend
- QoS: 0

```json
{
  "distance_cm": 12.5,
  "timestamp": "2026-09-10T14:32:05Z"
}
```

### Kết quả phân loại thành công — `truong/khu{n}/phanloai`

- Chiều: AI script → Broker → ESP32 (subscribe) + Backend (subscribe)
- QoS: 1

```json
{
  "loai_rac": "huu_co",
  "do_chac_chan": 0.87,
  "timestamp": "2026-09-10T14:32:07Z",
  "log_id": "uuid-tu-sinh"
}
```

### Trạng thái online/offline — `truong/khu{n}/trangthai/iot` và `.../ai`

- Chiều: ESP32 hoặc AI script → Broker → Backend (subscribe), dùng cơ chế **LWT**
- QoS: 1, `retain=true`

```json
{ "status": "online" }
```

```json
{ "status": "offline" }
```

## Tín hiệu "không tự tin" (đề xuất - cần chốt)

Khi AI không đủ tự tin phân loại (không class nào đạt ngưỡng xuất hiện tối thiểu trong cửa sổ `DETECTING`), cần 1 tín hiệu MQTT riêng để ESP32 bật **LED đỏ của zone**. Đã chốt về hành vi (xem [luồng nhận diện, mục 4](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md#4-trường-hợp-đặc-biệt--model-không-đủ-tự-tin)):

- Không kèm `loai_rac` (vì không xác định được)
- Không kèm `log_id` (vì Backend không lưu gì cho case này, không cần ghép nối)
- Backend không cần xử lý gì với tín hiệu này — chỉ ESP32 cần subscribe

**Còn chưa chốt — 2 phương án, cần Vũ và Tường thống nhất trước khi code:**

**Phương án A — Field riêng trong cùng topic `phanloai`:**

```json
{
  "trang_thai": "khong_chac",
  "timestamp": "2026-09-10T14:32:07Z"
}
```

- Ưu điểm: chỉ cần 1 topic, ESP32 và Backend đều subscribe sẵn `phanloai`, chỉ cần thêm điều kiện kiểm tra field `trang_thai` khi parse
- Nhược điểm: Backend cũng nhận được message này (dù không dùng) — cần nhớ bỏ qua đúng cách, tránh insert nhầm

**Phương án B — Topic phụ riêng, ví dụ `truong/khu{n}/khongchac`:**

```json
{
  "timestamp": "2026-09-10T14:32:07Z"
}
```

- Ưu điểm: tách bạch rõ ràng, Backend không cần quan tâm/subscribe topic này chút nào (chỉ ESP32 subscribe)
- Nhược điểm: thêm 1 topic mới cần cập nhật vào danh sách này và vào cấu hình broker/firmware

→ **Khuyến nghị:** phương án B rõ ràng hơn về mặt phân tách trách nhiệm (Backend hoàn toàn không cần biết tới tín hiệu này). Nhưng quyết định cuối cùng cần Vũ (người publish) và Tường (người subscribe) thống nhất trực tiếp.

## Quy ước chung

- `timestamp`: chuẩn ISO 8601, giờ UTC
- `loai_rac`: cố định 3 giá trị `tai_che`, `huu_co`, `vo_co` — viết liền không dấu, khớp enum DB
- QoS: mức đầy dùng QoS 0 (mất vài gói không sao), `phanloai` và `trangthai` dùng QoS 1 (đảm bảo tới nơi)

## LWT (Last Will and Testament)

Cơ chế để broker tự phát hiện khi 1 client (ESP32 hoặc script AI) rớt kết nối đột ngột (mất điện, đứt wifi, crash — không kịp báo offline bình thường):

1. Khi client kết nối tới broker, đăng ký sẵn "di chúc": nếu rớt kết nối đột ngột, broker tự publish `{"status": "offline"}` lên topic trạng thái thay cho client
2. Khi client kết nối lại bình thường → tự publish `{"status": "online"}` như message thường

**Lưu ý:** ESP32 và script AI là **2 client MQTT riêng biệt**, nên có LWT riêng — 2 trạng thái khác nhau (`trangthai/iot` và `trangthai/ai`) vì "phần cứng thùng rác mất kết nối" khác với "hệ thống nhận diện không chạy nữa".
