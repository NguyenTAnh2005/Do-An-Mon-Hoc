<div align="center">

# ♻️ Hệ Thống Quản Lý & Phân Loại Rác Thải Thông Minh Trường Học

### Smart School Waste Management & Classification System

**IoT + Deep Learning**

📚 **Đồ án môn học** — Trường Đại học Bình Dương
🎓 Khóa: **K26** &nbsp;|&nbsp; 👨‍🏫 Giảng viên hướng dẫn: **Nguyễn Hồ Hải**

![React](https://img.shields.io/badge/React-JS-61DAFB?logo=react&logoColor=white&style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white&style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white&style=for-the-badge)
![YOLOv8](https://img.shields.io/badge/YOLOv8n-Deep_Learning-purple?logo=pytorch&logoColor=white&style=for-the-badge)
![ESP32](https://img.shields.io/badge/ESP32-IoT-red?logo=espressif&logoColor=white&style=for-the-badge)
![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-660066?logo=eclipsemosquitto&logoColor=white&style=for-the-badge)

</div>

---

## 📖 1. Giới thiệu

Vấn đề phân loại rác thải trong khuôn viên trường học hiện nay phần lớn vẫn dựa vào ý thức thủ công của học sinh — sinh viên, dẫn đến tỷ lệ phân loại sai cao, gây khó khăn cho công tác thu gom và xử lý rác thải sau này.

**Giải pháp:** Hệ thống kết hợp **Internet of Things (IoT)** và **Deep Learning (YOLOv8n)** nhằm:

- 🎥 Tự động **nhận diện & phân loại rác** qua camera ngay tại thùng rác
- 📊 **Giám sát realtime** trạng thái các thùng rác (mực đầy, tình trạng thiết bị)
- 🗂️ **Lưu trữ lịch sử** phân loại kèm hình ảnh để đối soát, kiểm tra
- 📈 **Thống kê trực quan** phục vụ công tác quản lý vệ sinh trường học

> **Phạm vi demo:** 2 khu vực, mỗi khu vực gồm 3 thùng (**Tái chế** / **Hữu cơ** / **Vô cơ**) → tổng **6 thùng rác thông minh**.

---

## 🏗️ 2. Kiến trúc hệ thống

> 🚧 **Đang cập nhật**

---

## ✨ 3. Tính năng chính

| Tính năng                 | Mô tả                                                                                              |
| ------------------------- | -------------------------------------------------------------------------------------------------- |
| 📊 **Dashboard Realtime** | Theo dõi % đầy của 6 thùng, trạng thái online/offline của IoT và AI (tách riêng theo từng khu vực) |
| 🗂️ **Lịch sử phân loại**  | Danh sách các lần phân loại kèm ảnh chụp, hỗ trợ filter, xác nhận đúng/sai thủ công                |
| 📈 **Thống kê**           | Thống kê theo loại rác / khu vực / thời gian, theo dõi độ chính xác model theo từng ngày           |
| 🔐 **Đăng nhập**          | Tài khoản quản lý (JWT access + refresh token)                                                     |

---

## 🛠️ 4. Công nghệ sử dụng

### 🧠 AI / CNN

- **YOLOv8n** (fine-tuned từ Roboflow Universe)
- Python, OpenCV (`cv2`) đọc camera

### 🔌 IoT

- **ESP32** điều khiển thiết bị
- Cảm biến siêu âm **HC-SR04** (đo mực đầy)
- **Servo motor** (đóng/mở nắp thùng)
- Giao tiếp qua **MQTT (Mosquitto)**

### 💻 Web (Frontend + Backend)

- **React JS** — Frontend
- **FastAPI (sync)** — Backend, đồng thời là MQTT Subscriber & WebSocket Server
- **PostgreSQL** + **ORM** (không dùng SQL thuần)
- **Alembic** — quản lý migration
- **JWT** (access + refresh token) — xác thực
- **Cloudinary** — lưu trữ hình ảnh
- **WebSocket** — cập nhật dữ liệu realtime cho Dashboard

---

## 🔧 5. Phần cứng

Mỗi khu vực demo bao gồm:

| Thiết bị                                    | Số lượng    | Chức năng                 |
| ------------------------------------------- | ----------- | ------------------------- |
| 📱 Camera điện thoại (IP Webcam / DroidCam) | 1           | Ghi hình cho AI nhận diện |
| 🔌 ESP32                                    | 1           | Điều khiển 3 thùng rác    |
| 📡 Cảm biến HC-SR04                         | 3 (1/thùng) | Đo mực đầy rác            |
| ⚙️ Servo motor                              | 3 (1/thùng) | Đóng/mở nắp thùng         |

> 💰 **Nguồn cung cấp thiết bị:** Chủ yếu do **Vũ** và **Tường** cung cấp. Trường hợp thiếu, cả 3 thành viên cùng đóng góp chi phí mua sắm.

---

## 📁 6. Cấu trúc thư mục repo

```
├── AI_CNN/     # Model YOLOv8n, xử lý ảnh, gửi kết quả phân loại
├── IOT/        # Firmware ESP32, điều khiển cảm biến & servo
├── WEB/        # Frontend (React) + Backend (FastAPI)
└── DOC/        # Tài liệu, ghi chú, kế hoạch theo từng giai đoạn
```

---

## 🔄 7. Luồng dữ liệu chính

> 🚧 **Đang cập nhật**

---

## 👥 8. Thành viên nhóm

| MSSV     | Họ và tên            | Vai trò       | Phụ trách |
| -------- | -------------------- | ------------- | --------- |
| 23050118 | **Nguyễn Tuấn Anh**  | Quản lý dự án | 💻 Web    |
| 23050102 | **Lý Lâm Vũ**        | Thành viên    | 🧠 AI     |
| 23050112 | **Nguyễn Đức Tường** | Thành viên    | 🔌 IoT    |

---

## 🚀 9. Hướng dẫn cài đặt & chạy thử

> 🚧 **Đang cập nhật**

---

## 🙏 10. Tham khảo & Hỗ trợ

Dự án có sử dụng sự hỗ trợ tham khảo từ các công cụ AI:

- 🤖 **Claude** (Anthropic)
- 🤖 **Gemini Pro** (Google)

---

<div align="center">

**Made with 💚 by nhóm sinh viên K26 — Trường ĐH Bình Dương**

</div>
