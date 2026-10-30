# AI_CNN — Nhận diện và phân loại rác

Camera chụp khay rác từ trên xuống. Chương trình so ảnh với khay trống, chạy YOLOv8n khi có vật, bình chọn loại rác qua nhiều frame, rồi gửi kết quả qua MQTT và ảnh qua HTTP.

## Chuẩn bị

1. Cài Python và PyTorch phù hợp máy theo [hướng dẫn GPU](../DOCS/04-ai/cai-dat-pytorch-gpu.md), sau đó chạy `pip install -r requirements.txt`.
2. Đặt model đã train tại `AI_CNN/best.pt`. Model hiện có ba tên lớp: `inorganic-waste`, `organic-waste`, `recyclable waste`; [config.py](config.py) chuyển chúng thành `inorganic`, `organic`, `recyclable` khi gửi đi.
3. Copy `.env.example` thành `.env`, điền MQTT và `BACKEND_URL`. Sửa địa chỉ hai camera trong `CAMERAS` ở `config.py` cho đúng mạng demo.
4. Để **khay trống trong 30 frame đầu** khi khởi động để chương trình ghi ảnh nền. Nếu đổi góc camera hoặc khay, khởi động lại để ghi ảnh nền mới.

## Chạy

Từ thư mục `AI_CNN`:

```powershell
python worker.py 1  # khu vực 1
python worker.py 2  # khu vực 2, ở terminal khác
```

Mỗi worker xử lý một camera. `Ctrl+C` dừng và báo trạng thái AI offline. Nếu gửi ảnh thất bại, ảnh được lưu vào `local_images/<log_id>/frame.jpg` cùng `meta.txt` để upload thủ công.

Chạy test không cần camera hoặc broker thật:

```powershell
python -m unittest discover -s tests -v
```

Hợp đồng topic, JSON, QoS và `retain` nằm ở [tài liệu MQTT](../DOCS/06-mqtt/mqtt-topic-va-json-format.md).

## Giới hạn tích hợp hiện tại

`BACKEND_URL` phải trỏ tới API **POST multipart** nhận `log_id` và file JPEG ở field `file`. Backend hiện chỉ có API PATCH upload thủ công theo `record_id`; endpoint dành cho AI theo `log_id` chưa có. Cho tới khi Web bổ sung endpoint đó, uploader sẽ lưu ảnh cục bộ sau khi HTTP trả lỗi.

MQTT QoS 1 có thể giao trùng `classification`; ESP32 cần bỏ qua `log_id` đã xử lý để tránh mở nắp hai lần. Trạng thái `status/ai` dùng LWT và `retain=true`.
