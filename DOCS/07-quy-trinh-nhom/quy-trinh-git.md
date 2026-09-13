# Quy trình Git của nhóm

> **Mục đích file này:** mô hình branch, quy tắc đặt tên, và các bước thao tác Git chuẩn cho cả 3 thành viên — dùng làm tài liệu tham chiếu khi có ai quên bước nào.

## 1. Mô hình nhánh

Nhóm dùng mô hình 2 tầng, đơn giản, phù hợp với người mới dùng Git:

```
main                        <- nhánh chính, luôn chạy được, chỉ merge qua PR
 └── feature/<component>-<description>   <- nhánh làm việc của từng người
```

**Quy tắc đặt tên nhánh:**

| Thành phần  | Component | Ví dụ nhánh                                            |
| ------------- | ----------- | --------------------------------------------------------- |
| Web (BE/FE)  | `web`     | `feature/web-jwt-auth`, `feature/web-dashboard-ui`      |
| AI/CNN       | `ai`      | `feature/ai-yolo-finetune`, `feature/ai-state-machine`  |
| IoT          | `iot`     | `feature/iot-servo-control`, `feature/iot-hcsr04-read`  |

- Component khớp đúng tên thư mục repo: `WEB/`, `AI_CNN/`, `IOT/`
- Description ngắn gọn, viết thường, nối bằng dấu `-`, mô tả đúng việc đang làm (không viết chung chung như `feature/web-update`)

Không có nhánh `dev` trung gian — mỗi feature branch tách trực tiếp từ `main` và merge thẳng lại vào `main`.

## 2. Quy trình từng bước (cho mỗi thành viên)

### Bước 1 — Cập nhật `main` trước khi bắt đầu việc mới

```bash
git checkout main
git pull origin main
```

### Bước 2 — Tạo nhánh mới

```bash
git checkout -b feature/<component>-<description>
```

Ví dụ:

```bash
git checkout -b feature/iot-servo-control
```

### Bước 3 — Code, commit

```bash
git add .
git commit -m "iot: thêm điều khiển servo theo tín hiệu MQTT"
```

Commit message nên bắt đầu bằng tên component (`web:`, `ai:`, `iot:`) + mô tả ngắn việc đã làm. Commit nhỏ, thường xuyên — không dồn cả tuần code vào 1 commit.

### Bước 4 — Push nhánh lên GitHub

```bash
git push -u origin feature/<component>-<description>
```

(`-u` chỉ cần lần push đầu tiên của nhánh, sau đó chỉ cần `git push`)

### Bước 5 — Tạo Pull Request (PR) trên GitHub

- Vào GitHub → tab **Pull requests** → **New pull request**
- Base: `main` ← Compare: nhánh vừa push
- Tiêu đề PR: giống format commit, ví dụ `iot: điều khiển servo theo MQTT`
- Mô tả PR nên có: đã làm gì, cách test/kiểm tra (nếu có), có phần nào chưa xong / cần lưu ý khi review
- Gắn reviewer: **Anh (chủ dự án)**

### Bước 6 — Chờ duyệt & merge

- Chỉ Anh (PM) có quyền **approve + merge** PR vào `main`
- Nếu Anh yêu cầu sửa: người tạo PR sửa trực tiếp trên cùng nhánh, commit thêm rồi push — PR tự cập nhật, không cần tạo PR mới
- Sau khi merge xong, xoá nhánh feature trên GitHub để repo gọn

### Bước 7 — Mỗi người tự đồng bộ lại `main`

Sau khi PR được merge, **tất cả thành viên** cần cập nhật lại `main` cục bộ:

```bash
git checkout main
git pull origin main
```

Nếu đang có nhánh feature khác đang làm dở, cần lấy code mới từ `main`:

```bash
git checkout feature/<nhanh-dang-lam>
git merge main
```

## 3. Sơ đồ tóm tắt

```
 main (mới nhất)
    │
    ├─ checkout -b feature/iot-servo-control
    │        │
    │        ├─ code, commit, commit...
    │        │
    │        └─ push origin feature/iot-servo-control
    │                 │
    │                 └─ tạo PR trên GitHub (base: main)
    │                          │
    │                          └─ Anh review → approve → merge vào main
    │                                   │
    └───────────────────────────────────┘
    main (đã cập nhật)
         │
         └─ mọi người: git checkout main && git pull origin main
```

## 4. Quy tắc chung cần nhớ

- **Không push trực tiếp lên `main`** — mọi thay đổi vào `main` đều phải qua PR
- **Không tự merge PR của mình** — chờ Anh duyệt, kể cả khi code chắc chắn chạy được
- Trước khi tạo nhánh mới, luôn `pull` `main` mới nhất
- Mỗi PR nên tập trung 1 việc cụ thể, tránh gộp nhiều thay đổi không liên quan
- Nếu PR bị conflict với `main` khi đang chờ duyệt: người tạo PR tự xử lý conflict trên nhánh của mình, push lại
- Đặt tên nhánh và commit rõ ràng — vì cả nhóm mới dùng Git, tên rõ giúp dễ tra lại lịch sử khi có lỗi

## 5. Vai trò trong quy trình

| Vai trò         | Việc                                                                     |
| ----------------- | --------------------------------------------------------------------------- |
| **Anh (PM)**     | Duyệt/approve PR, merge vào `main`, quản lý xung đột giữa các component     |
| **Vũ (AI)**      | Làm việc trên nhánh `feature/ai-*`, tạo PR, chờ duyệt                       |
| **Tường (IoT)**  | Làm việc trên nhánh `feature/iot-*`, tạo PR, chờ duyệt                      |
