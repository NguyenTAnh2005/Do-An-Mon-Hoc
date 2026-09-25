# Cấu trúc thư mục Frontend — Hệ thống Phân loại Rác

Tạo bằng `npm create vite@latest . -- --template react` **trước**, bat chỉ bổ sung phần `src/` còn thiếu.

```
WEB/frontend/
├── .env
├── .gitignore        (vite đã tạo sẵn)
├── README.md         (vite đã tạo sẵn)
└── src/
    ├── App.jsx        (vite đã tạo sẵn — không đụng vào)
    ├── main.jsx       (vite đã tạo sẵn — không đụng vào)
    ├── contexts/
    ├── hooks/
    ├── routes/
    ├── pages/
    ├── layout/
    ├── components/
    │   ├── ui/
    │   └── wrapper/
    ├── service/
    │   └── config/
    └── utils/
```

---

## 1. Auth & điều hướng (1 role — không còn AdminRoute/ManagerRoute tách biệt)

| File                           | Vai trò                                                      |
| ------------------------------ | ------------------------------------------------------------ |
| `src/contexts/AuthContext.jsx` | Lưu access token qua `useState`/Context (không localStorage) |
| `src/hooks/useAuth.js`         | Lối tắt lấy user/token hiện tại từ AuthContext               |
| `src/routes/AuthProtected.jsx` | Chặn route khi chưa đăng nhập                                |
| `src/routes/AppRoute.jsx`      | Khai báo toàn bộ route của app                               |
| `src/pages/Login.jsx`          | Trang đăng nhập                                              |

## 2. Kết nối realtime (WebSocket)

| File                                | Vai trò                                                                          |
| ----------------------------------- | -------------------------------------------------------------------------------- |
| `src/service/websocket.js`          | Wrap raw `WebSocket` — connect, tự reconnect khi mất mạng, `JSON.parse` message  |
| `src/contexts/WebSocketContext.jsx` | Giữ **1 connection duy nhất** dùng chung toàn app, lưu state mới nhất nhận được  |
| `src/hooks/useWebSocket.js`         | Hook để component lấy đúng phần state cần (fill %, trạng thái online) từ Context |

## 3. Gọi API (REST — mỗi domain 1 file, khớp route backend tương ứng)

| File                                                  | Vai trò                               |
| ----------------------------------------------------- | ------------------------------------- |
| `src/service/config/autoConfig.js`, `manualConfig.js` | Cấu hình axios instance               |
| `src/service/auth.js`                                 | Gọi `/login`, `/refresh`, `/logout`   |
| `src/service/khuVuc.js`                               | Gọi `GET /khu-vuc`                    |
| `src/service/thungRac.js`                             | Gọi `GET /thung-rac`                  |
| `src/service/lichSuPhanLoai.js`                       | Gọi CRUD lịch sử + hàm upload lại ảnh |
| `src/service/thongKe.js`                              | Gọi các endpoint thống kê             |

## 4. Giao diện

| File                                    | Vai trò                                                                |
| --------------------------------------- | ---------------------------------------------------------------------- |
| `src/layout/Layout.jsx`                 | 1 layout duy nhất (bỏ layout riêng theo role)                          |
| `src/pages/Dashboard.jsx`               | Mức đầy 6 thùng + trạng thái thiết bị — nhận qua WebSocket             |
| `src/pages/QuanLyLichSu.jsx`            | List, filter, xác nhận đúng/sai, batch xóa, upload lại ảnh             |
| `src/pages/ThongKe.jsx`                 | Biểu đồ/thống kê theo loại, khu vực, độ chính xác                      |
| `src/components/ThungRacCard.jsx`       | Card hiển thị 1 thùng rác                                              |
| `src/components/KhuVucStatus.jsx`       | Hiển thị trạng thái online/offline 1 khu vực                           |
| `src/components/LichSuPhanLoaiItem.jsx` | 1 dòng trong danh sách lịch sử                                         |
| `src/components/ui/*`                   | Input, Pagination, ThemeToggle, FetchStatus — tái dùng từ portfolio cũ |
| `src/components/wrapper/*`              | Button, Modal, CardItem                                                |

## 5. Utils

| File                       | Vai trò                         |
| -------------------------- | ------------------------------- |
| `src/utils/axiosHelper.js` | Helper xử lý lỗi/response axios |
| `src/utils/dateISO.js`     | Format ngày giờ ISO             |
| `src/utils/string.js`      | Helper chuỗi chung              |
