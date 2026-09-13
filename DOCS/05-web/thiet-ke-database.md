# Thiết kế Database

> **Mục đích file này:** schema PostgreSQL đầy đủ cho hệ thống, kèm giải thích lý do đằng sau các quyết định thiết kế (vì sao dùng `log_id` UUID, vì sao lưu full topic MQTT, vì sao không lưu lịch sử mức đầy...).

Liên quan: [Kiến trúc Backend realtime](./kien-truc-backend-realtime.md) · [Luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) · [MQTT topic & JSON format](../06-mqtt/mqtt-topic-va-json-format.md)

---

## Schema

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

> **Lưu ý quan trọng:** bảng `lich_su_phan_loai` chỉ nhận dòng mới khi AI phân loại **thành công** (có `loai_rac` cụ thể). Trường hợp AI publish tín hiệu "không tự tin" (xem [luồng nhận diện](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md#41-điều-kiện-xảy-ra)) **không tạo dòng nào** trong bảng này — vì không có kết quả phân loại thật để lưu.

## Nguyên tắc quan trọng

- `thung_rac` chỉ có đúng 6 dòng cố định (3 thùng × 2 khu vực), **không bao giờ tăng thêm** — mức đầy được **UPDATE ghi đè**, không insert dòng mới mỗi lần MQTT gửi.
- Chỉ `lich_su_phan_loai` tăng dòng theo thời gian, và chỉ khi có 1 lần phân loại thành công thật sự xảy ra (không phải mỗi lần đo mức đầy, và không phải khi AI báo "không tự tin").
- `iot_online` / `ai_online` tách riêng 2 cột, vì ESP32 và script AI là 2 MQTT client độc lập, có LWT riêng — "phần cứng mất kết nối" khác với "hệ thống nhận diện không chạy".

**Về cách lưu topic:** thay vì lưu 1 `prefix` chung rồi để BE tự nối chuỗi ra topic con, mỗi đối tượng (`khu_vuc`, `thung_rac`) tự lưu sẵn **full topic đầy đủ** của chính nó. BE khi cần subscribe/publish chỉ đọc thẳng cột tương ứng ra dùng, không cần logic nối chuỗi. Đánh đổi: nếu sau này đổi quy tắc đặt tên topic hàng loạt thì phải sửa từng dòng trong DB — nhưng với quy mô 6 thùng + 2 khu vực, không đáng lo.

## Luồng ảnh (cv2 → Backend → Cloudinary)

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
