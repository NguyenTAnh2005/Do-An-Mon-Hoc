# Mục lục — Hệ thống quản lý & phân loại rác thải thông minh trường học

> **Mục đích file này:** điểm bắt đầu để đọc toàn bộ tài liệu dự án. Liệt kê tất cả các file, nhóm theo chủ đề, kèm mô tả ngắn để biết nên mở file nào khi cần thông tin gì.

Đề tài: *Xây dựng hệ thống quản lý và phân loại rác thải thông minh tại trường học ứng dụng IoT và Deep Learning*. Nhóm 3 người: **Vũ (AI/CNN)**, **Tường (IoT)**, **Anh (Web — PM)**. Demo trên 2 khu vực, mỗi khu vực 3 thùng (tái chế / hữu cơ / vô cơ).

---

## 0. Tổng quan & quyết định đã chốt

- [Tóm tắt các quyết định đã chốt tính tới hiện tại](./tom-tat-quyet-dinh.md) — đọc file này trước tiên nếu cần nắm nhanh toàn bộ dự án đang ở đâu.

## 1. Kiến trúc tổng thể

- [Danh sách phần cứng & phần mềm cần cho dự án](../01-kien-truc-tong-the/danh-sach-thanh-phan.md)
- [Vai trò của từng thành phần trong hệ thống](../01-kien-truc-tong-the/vai-tro-thanh-phan.md)

## 2. Luồng xử lý (liên quan cả 3 người)

- [Luồng nhận diện & phân loại rác — chi tiết state machine, MQTT, ảnh](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md)
- [Luồng cập nhật mức đầy realtime & trạng thái online/offline](../02-luong-xu-ly/luong-mucday-trangthai-online.md)

## 3. IoT (Tường phụ trách)

- [Thiết kế phần cứng & firmware IoT](../03-iot/thiet-ke-iot.md)
- [Danh sách công việc — IoT](../03-iot/phase-cong-viec-iot.md)

## 4. AI/CNN (Vũ phụ trách)

- Logic nhận diện chi tiết nằm chung ở [luồng nhận diện & phân loại rác](../02-luong-xu-ly/luong-nhan-dien-phan-loai.md) (vì liên quan cả 3 người)
- [Cài đặt môi trường PyTorch + GPU (CUDA)](../04-ai/cai-dat-pytorch-gpu.md)
- [Danh sách công việc — AI](../04-ai/phase-cong-viec-ai.md)

## 5. Web — Backend + Frontend (Anh phụ trách)

- [Kiến trúc Backend: MQTT subscriber + WebSocket server](../05-web/kien-truc-backend-realtime.md)
- [Thiết kế Database](../05-web/thiet-ke-database.md)
- [Danh sách công việc — Web (Module 0 → 6)](../05-web/phase-cong-viec-web.md)

## 6. MQTT (giao tiếp giữa 3 mảng)

- [Danh sách topic & format JSON](../06-mqtt/mqtt-topic-va-json-format.md)
- [Setup broker dùng chung khi tích hợp thật](../06-mqtt/setup-broker-mang-noi-bo.md)
- [Debug MQTT bằng MQTTX](../06-mqtt/debug-voi-mqttx.md)

## 7. Quy trình làm việc nhóm

- [Quy trình Git (branch, PR, review)](../07-quy-trinh-nhom/quy-trinh-git.md)
- [Danh sách công việc chung (setup dự án, MQTT, debug tool)](../07-quy-trinh-nhom/phase-cong-viec-chung.md)

## 8. Checklist tổng hợp

- [Checklist công việc đầy đủ theo từng người, đã cập nhật các thay đổi mới nhất](../08-checklist/checklist-tong-hop-cap-nhat.md)

---

### Ghi chú về cấu trúc thư mục

```
DOC/
├── 00-tong-quan/              ← đọc trước tiên
├── 01-kien-truc-tong-the/     ← bức tranh toàn hệ thống
├── 02-luong-xu-ly/            ← luồng dữ liệu xuyên suốt 3 mảng
├── 03-iot/                    ← riêng cho Tường
├── 04-ai/                     ← riêng cho Vũ
├── 05-web/                    ← riêng cho Anh
├── 06-mqtt/                   ← hợp đồng giao tiếp chung, cả 3 người đều cần đọc
├── 07-quy-trinh-nhom/         ← git, setup chung
└── 08-checklist/              ← tổng hợp task, dùng để rà tiến độ
```
