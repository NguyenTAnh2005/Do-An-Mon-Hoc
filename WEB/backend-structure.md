# Cấu trúc thư mục Backend — Hệ thống Phân loại Rác

Gom nhóm theo **mục đích**, không theo loại file, để dễ hình dung luồng dữ liệu.

```
WEB/backend/
├── main.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── alembic.ini
├── alembic/
│   └── versions/
└── app/
    ├── __init__.py
    ├── db_connection.py
    ├── core/
    ├── models/
    ├── schemas/
    ├── crud/
    ├── services/
    └── api/v1/endpoints/
```

---

## 1. Khởi tạo & cấu hình gốc

| File                                                  | Vai trò                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------- |
| `main.py`                                             | Entry point, khởi động FastAPI app + kết nối MQTT lúc startup |
| `app/core/config.py`                                  | Đọc biến môi trường từ `.env`                                 |
| `app/db_connection.py`                                | Kết nối PostgreSQL                                            |
| `alembic/`                                            | Migration schema, chạy song song lúc dựng model               |
| `requirements.txt`, `.env`, `.gitignore`, `README.md` | Chuẩn dự án                                                   |

## 2. Auth & User (1 loại tài khoản quản lý — đã chốt bỏ RBAC)

| File                              | Vai trò                                               |
| --------------------------------- | ----------------------------------------------------- |
| `app/core/jwt.py`                 | Tạo/verify access token                               |
| `app/core/refresh_token.py`       | Tạo/verify refresh token (lưu hash trong DB)          |
| `app/core/password.py`            | Hash/verify mật khẩu                                  |
| `app/models/user.py`              | Bảng `user` — KHÔNG có cột role, chỉ 1 loại tài khoản |
| `app/schemas/user.py`, `token.py` | Validate input / định hình output                     |
| `app/crud/user.py`, `token.py`    | Thao tác DB thuần                                     |
| `app/services/auth.py`            | Logic login, refresh, logout                          |
| `app/api/v1/endpoints/auth.py`    | Route `/login`, `/refresh`, `/logout`                 |

## 3. MQTT + WebSocket (lõi realtime — không có route tạo/sửa cho FE gọi)

| File                                | Vai trò                                                                                                                                  |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `app/core/mqtt_client.py`           | Chỉ connect broker + đăng ký callback, không xử lý logic                                                                                 |
| `app/core/websocket_manager.py`     | `ConnectionManager` — quản lý danh sách connection đang mở, có hàm `broadcast()`                                                         |
| `app/services/mqtt_service.py`      | Nhận callback MQTT → gọi crud (update mức đầy, trạng thái online, **tạo row `lich_su_phan_loai`**) → gọi `websocket_manager.broadcast()` |
| `app/api/v1/endpoints/websocket.py` | Route `/ws` — chỉ accept + giữ connection sống, logic thật nằm ở `mqtt_service.py`                                                       |

Lưu ý: việc "tạo" 1 dòng lịch sử phân loại **không đi qua HTTP POST** — nó là hệ quả của MQTT message, gọi thẳng hàm `crud.create()` trong process, không cần route riêng.

## 4. Khu vực & Thùng rác (hệ thống ghi qua MQTT, user chỉ đọc)

| File                                     | Vai trò                                                  |
| ---------------------------------------- | -------------------------------------------------------- |
| `app/models/khu_vuc.py`, `thung_rac.py`  | Bảng tương ứng                                           |
| `app/schemas/khu_vuc.py`, `thung_rac.py` | Response shape                                           |
| `app/crud/khu_vuc.py`, `thung_rac.py`    | Chỉ cần `get`/`get_all`, không có create/update cho user |
| `app/api/v1/endpoints/khu_vuc.py`        | `GET /khu-vuc` — load lần đầu cho Dashboard              |
| `app/api/v1/endpoints/thung_rac.py`      | `GET /thung-rac`                                         |

## 5. Lịch sử phân loại (3 nguồn ghi: MQTT tạo row, AI gắn ảnh, quản lý xác nhận/xóa)

| File                                        | Vai trò                                                                                                                                                                                                                       |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `app/models/lich_su_phan_loai.py`           | Bảng chính, `log_id` UUID do AI tự sinh                                                                                                                                                                                       |
| `app/schemas/lich_su_phan_loai.py`          | Schema list/detail + input xác nhận                                                                                                                                                                                           |
| `app/crud/lich_su_phan_loai.py`             | `create` (gọi từ `mqtt_service`), `update_anh`, `update_xac_nhan`, `delete`                                                                                                                                                   |
| `app/services/lich_su_phan_loai.py`         | `attach_anh()` — dùng chung cho cả AI và FE upload lại ảnh                                                                                                                                                                    |
| `app/core/api_key_auth.py`                  | Dependency check header `X-API-Key` — dùng riêng cho route AI gọi                                                                                                                                                             |
| `app/core/cloudinary_config.py`             | Cấu hình upload ảnh lên Cloudinary                                                                                                                                                                                            |
| `app/api/v1/endpoints/lich_su_phan_loai.py` | `GET` (JWT, list+filter) · `PATCH {log_id}` (JWT, xác nhận đúng/sai) · `DELETE` (JWT, batch xóa dòng thiếu ảnh) · `POST {log_id}/anh` (X-API-Key, AI gắn ảnh) · `POST {log_id}/anh/upload-lai` (JWT, quản lý upload thủ công) |

## 6. Thống kê (đọc tổng hợp trên bảng lịch sử — không model/crud riêng)

| File                               | Vai trò                                                                                                           |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `app/schemas/thong_ke.py`          | Response shape cho dữ liệu tổng hợp (khác hẳn schema 1 dòng lịch sử)                                              |
| `app/services/thong_ke.py`         | `theo_loai()`, `theo_khu_vuc()`, `do_chinh_xac_theo_ngay()` — query aggregate trực tiếp, không qua lớp crud riêng |
| `app/api/v1/endpoints/thong_ke.py` | `GET /thong-ke/theo-loai`, `/theo-khu-vuc`, `/do-chinh-xac`                                                       |
