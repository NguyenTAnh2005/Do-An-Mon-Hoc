"""
uploader.py — Gửi ảnh bất đồng bộ (không block AI loop).

Nhiệm vụ:
    - Nhận ảnh → đẩy vào queue → worker thread upload lên backend.
    - Nếu lỗi mạng → lưu local theo log_id để upload thủ công sau.

Input:  log_id (str), image_bytes (bytes)
Output: HTTP POST tới backend, hoặc lưu local_images/{log_id}/

Ai dùng:
    - detector.py gọi uploader.submit() sau khi publish MQTT.

Tại sao cần queue + thread:
    - POST ảnh mất 1-3s (upload Cloudinary) → nếu POST trong AI loop
      sẽ block → frame tiếp theo bị bỏ lỡ.
    - Queue + worker thread → AI loop không bị ảnh hưởng.

⚠️  LƯU Ý:
    - KHÔNG retry tự động (theo doc nhóm đã chốt).
    - Lỗi mạng → lưu local_images/{log_id}/frame.jpg + meta.txt.
    - Quản lý sẽ upload thủ công qua FE sau.

Nhánh độc lập với MQTT:
    - Backend nhận ảnh trước/sau MQTT đều OK.
    - Dùng log_id để nối 2 luồng lại ở DB.
"""