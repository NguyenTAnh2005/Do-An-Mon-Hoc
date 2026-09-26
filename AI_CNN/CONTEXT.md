# 📄 File `CONTEXT.md` — Bản hoàn chỉnh, copy paste được

Em copy **toàn bộ** nội dung dưới đây vào file `Do-An-Mon-Hoc/CONTEXT.md`:

---

```markdown
# 📋 CONTEXT — Tổng quan dự án & tiến độ

> File này là "bộ nhớ ngoài" của dự án. Gửi file này cho AI assistant mỗi buổi làm việc mới → AI đọc là hiểu toàn bộ context.

**Cập nhật lần cuối:** 2026-09-25

---

## 🎯 1. Dự án là gì?

**Tên:** Hệ thống Quản lý & Phân loại Rác thải Thông minh Trường học
**Môn:** Đồ án môn học — Đại học Bình Dương, khóa K26
**GVHD:** Nguyễn Hồ Hải

**Kiến trúc:** IoT + Deep Learning + Web

- **AI (Vũ):** YOLOv8n nhận diện rác → publish MQTT + gửi ảnh
- **IoT (Tường):** ESP32 đọc HC-SR04 + điều khiển servo + LED
- **Web (Anh):** FastAPI backend + React frontend + subscriber MQTT
- **MQTT Broker:** EMQX Cloud Serverless (TLS, port 8883)
- **DB:** PostgreSQL (local, cài thủ công, KHÔNG dùng Docker)

**Phạm vi demo:** 2 khu vực (Khu A + Khu B), mỗi khu 3 thùng (tái chế / hữu cơ / vô cơ).

---

## 👥 2. Thành viên & phân công

| MSSV     | Họ tên           | Vai trò       | Phụ trách                      |
| -------- | ---------------- | ------------- | ------------------------------ |
| 23050118 | Nguyễn Tuấn Anh  | Quản lý dự án | 💻 Web (FastAPI + React)       |
| 23050102 | Lý Lâm Vũ        | Thành viên    | 🧠 AI (YOLOv8n + MQTT publish) |
| 23050112 | Nguyễn Đức Tường | Thành viên    | 🔌 IoT (ESP32 firmware)        |

**Người đang chat với AI:** Anh (Web) — đang hỗ trợ review cho Vũ (AI).

---

## 📁 3. Cấu trúc repo CHỐT CỐI CÙNG
```

Do-An-Mon-Hoc/
├── AI_CNN/ ← VŨ
│ ├── core/
│ │ ├── camera.py # ✅ ĐÃ CODE
│ │ ├── frame_diff.py # ⏳ CHƯA
│ │ ├── detector.py # ⏳ CHƯA (khó nhất)
│ │ ├── mqtt_pub.py # ⏳ CHƯA
│ │ └── uploader.py # ⏳ CHƯA
│ ├── config.py # ✅ ĐÃ XONG
│ ├── worker.py # ⏳ skeleton có
│ ├── demo_ui.py # ✅ ĐÃ CÓ
│ ├── train_model.py # ✅ ĐÃ XONG
│ ├── check_classmap.py # ✅ ĐÃ CÓ
│ ├── check_libs.py # ⏳ CẦN TẠO
│ ├── benchmark.py # ⏳ CẦN TẠO
│ ├── .env # ✅ ĐÃ TẠO (giá trị giả)
│ ├── .env.example # ✅ ĐÃ CÓ
│ ├── requirements.txt # ✅ ĐÃ XONG
│ ├── README.md # ✅ ĐÃ XONG
│ ├── model/yolo_v8_training/weights/v1-best.pt # ✅ ĐÃ CÓ
│ └── local_images/ # (tự tạo khi chạy)
│
├── IOT/ ← TƯỜNG
│ └── firmware/ # ⏳ CHƯA CODE
│
├── WEB/ ← ANH
│ ├── backend/ # ⏳ CHƯA CODE
│ └── frontend/ # ⏳ CHƯA CODE
│
├── DOC/
│ ├── 01-kien-truc-tong-the/
│ ├── 02-luong-xu-ly/
│ ├── 04-ai/
│ ├── 06-mqtt/
│ └── 08-checklist/
│
└── CONTEXT.md ← FILE NÀY

````

**ĐÃ BỎ:** `MQTT/` (tách riêng), `INFRA/`, Docker, docker-compose cho MQTT.

---

## ✅ 4. Những gì ĐÃ LÀM XONG

### Cấu trúc & quyết định
- ✅ Chốt **4 thư mục lớn**: `AI_CNN / IOT / WEB / DOC`
- ✅ Bỏ MQTT/ riêng → code MQTT về từng thư mục người dùng
- ✅ Chốt dùng **EMQX Cloud Serverless** (port 8883, TLS bắt buộc)
- ✅ Bỏ Docker/infra → Postgres cài thủ công
- ✅ Chốt **không deploy** — chỉ chạy local demo

### AI (Vũ)
- ✅ Train xong model YOLOv8n trên máy bạn (GPU NVIDIA)
- ✅ Model classes: `{0: inorganic-waste, 1: organic-waste, 2: recyclable waste}`
- ✅ `CLASS_MAP` chuẩn (verify bằng `check_classmap.py`):
  - `recyclable waste` → `tai_che`
  - `organic-waste` → `huu_co`
  - `inorganic-waste` → `vo_co`
- ✅ `config.py` hoàn chỉnh (đọc `.env`, có `topic_*()` helper)
- ✅ `.env.example` + `.env` (giá trị giả) đã tạo
- ✅ `requirements.txt` đầy đủ (đã trừ torch — cài riêng)
- ✅ Cài đủ thư viện: torch 2.14.0+cpu, opencv, ultralytics, python-dotenv, paho-mqtt, requests
- ✅ `core/camera.py` — code xong (chờ test)
- ✅ `README.md` cho AI_CNN

### Tình trạng máy
- **Máy Vũ (dev/test):** AMD Radeon iGPU, KHÔNG có NVIDIA → torch CPU
- **Máy bạn (demo):** NVIDIA GPU → torch CUDA
- → Dùng `ROI_SIZE` trong `.env` để linh hoạt: 280 cho máy Vũ, 640 cho máy bạn

---

## 🎯 5. ĐANG LÀM Ở ĐÂU (điểm dừng)

**Bước hiện tại:** Test `core/camera.py` trên webcam laptop

**Việc Vũ cần làm tiếp ngay:**
1. Chạy `python core\camera.py` → test webcam
2. Paste output cho AI review
3. Nếu OK → nhận code `core/frame_diff.py` tiếp theo

**Lệnh test:**
```bash
cd D:\Do-An-Mon-Hoc\AI_CNN
python core\camera.py
````

---

## 🚀 6. LỘ TRÌNH CODE TIẾP THEO

| #   | File                 | Trạng thái   | Ghi chú                  |
| --- | -------------------- | ------------ | ------------------------ |
| 1   | `config.py`          | ✅ Xong      |                          |
| 2   | `core/camera.py`     | 🎯 Đang test |                          |
| 3   | `core/frame_diff.py` | ⏳ Tiếp theo | Lọc nhiễu PA3            |
| 4   | `core/detector.py`   | ⏳           | Trái tim — state machine |
| 5   | `core/mqtt_pub.py`   | ⏳           | Publish EMQX Cloud TLS   |
| 6   | `core/uploader.py`   | ⏳           | POST ảnh async           |
| 7   | `worker.py`          | ⏳           | Ghép tất cả              |
| 8   | Test end-to-end      | ⏳           | Trước demo               |

---

## 🔑 7. QUYẾT ĐỊNH KỸ THUẬT QUAN TRỌNG

Đọc để **KHÔNG quên** khi review code sau này:

### Về MQTT

- **`phanloai` retain = FALSE** ⚠️ — nếu retain, ESP32 reboot sẽ nhận lại message cũ → servo mở vô cớ
- **`trangthai/ai` retain = TRUE** — LWT online/offline
- **Client ID PHẢI unique** (`ai-khu{n}-{uuid_hex}`) — tránh kick nhau
- **QoS 1 cho phanloai, QoS 0 cho mucday**
- **Dedup bằng `log_id`** — QoS 1 có thể duplicate
- **TLS bắt buộc** — port 8883, `tls_set()` + `username_pw_set()`

### Về class mapping

- **KHÔNG đổi tên** enum `tai_che/huu_co/vo_co` giữa 3 người
- Tên class model có **DẤU CÁCH** (`recyclable waste`), không phải gạch ngang
- Nếu sửa model → chạy lại `check_classmap.py` verify

### Về AI logic

- **Vote theo tần suất** (Counter), KHÔNG dùng `boxes[0]`
- **Log_id do AI tự sinh** (uuid4), không xin backend
- **2 nhánh độc lập:** MQTT (nhanh) + POST ảnh (async)
- **Không retry tự động** khi POST ảnh fail → lưu local

### Về state machine

- IDLE → DETECTING (1.5s) → COOLDOWN (8s)
- **Chống re-detect:** vật vẫn còn trên khay → không detect lại (trong COOLDOWN)
- **Multi-object:** nếu 2 class vote ngang nhau → coi là "không tự tin"
- **`khongchac` topic** — tín hiệu riêng, không đi qua backend

### Về máy test vs máy demo

- `.env` của Vũ: `ROI_SIZE=280`
- `.env` của máy bạn: `ROI_SIZE=640`
- Không sửa code, chỉ sửa `.env`

---

## ⚠️ 8. BUG/EDGE CASE ĐÃ PHÁT HIỆN

1. ✅ **Class name có dấu cách** (`recyclable waste` không phải `recyclable-waste`) — đã fix
2. ✅ **Torch bản CPU trên máy Vũ** — chấp nhận, dùng ROI_SIZE nhỏ
3. ⚠️ **Retained message trên `phanloai`** — phải set `retain=False` khi code `mqtt_pub.py`
4. ⚠️ **QoS 1 duplicate** — phải dedup bằng `log_id` set
5. ⚠️ **2 ESP32 cùng client_id** — phải unique
6. ⚠️ **Race condition MQTT vs POST ảnh** — backend nên UPSERT, không PATCH
7. ⚠️ **DETECTING timeout** — nếu user che tay liên tục, AI có thể treo — cần max duration
8. ⚠️ **HC-SR04 cross-talk** — 3 cảm biến đọc tuần tự, stagger ≥ 60ms (Tường xử lý)

---

## 🎯 9. NGUYÊN TẮC LÀM VIỆC

1. **Không cài Docker/infra** — không cần cho đồ án môn học
2. **Không hard-code password** — luôn đọc từ `.env`
3. **Không commit `.env`** — chỉ commit `.env.example`
4. **Test từng module riêng** trước khi ghép
5. **Log JSON ra console** để debug dễ
6. **Không sửa code người khác** — chỉ PR rồi Anh merge
7. **Windows CMD:** không dùng `python -c "..."` nhiều dòng → tạo file `.py` rồi chạy

---

## 📊 10. TRẠNG THÁI TỪNG NGƯỜI

| Người           | Đang làm                                             | Blocker                       |
| --------------- | ---------------------------------------------------- | ----------------------------- |
| **Vũ (AI)**     | Test `camera.py`                                     | Chưa test xong                |
| **Tường (IoT)** | Setup EMQX Cloud TLS                                 | Chưa có host/user/pass từ Anh |
| **Anh (Web)**   | Tạo `.gitignore`, `.env.example`, README cho backend | Chưa có EMQX account          |

**Việc chung cả nhóm cần làm:**

- [ ] Chốt file `DOC/06-mqtt/mqtt-topic-va-json-format.md` — schema đầy đủ
- [ ] Anh tạo EMQX account → gửi host/user/pass cho Vũ + Tường qua Zalo
- [ ] Anh tạo `.gitignore` ở gốc repo

---

## 📚 11. TÀI LIỆU ĐÃ CÓ

- `DOC/01-kien-truc-tong-the/danh-sach-thanh-phan.md` — phần cứng + phần mềm
- `DOC/02-luong-xu-ly/luong-nhan-dien-phan-loai.md` — luồng AI chi tiết
- `DOC/02-luong-xu-ly/luong-mucday-trangthai-online.md` — luồng mức đầy + LWT
- `DOC/04-ai/cai-dat-pytorch-gpu.md` — cài torch CUDA
- `DOC/04-ai/phase-cong-viec-ai.md` — checklist việc AI
- `DOC/08-checklist/ai.md` — checklist chi tiết AI
- `DOC/08-checklist/chung.md` — checklist chung

---

## 🔧 12. LỆNH THƯỜNG DÙNG (Windows)

```bash
# Vào thư mục + activate venv
cd D:\Do-An-Mon-Hoc\AI_CNN
venv\Scripts\activate

# Test các module
python check_classmap.py
python check_libs.py
python benchmark.py
python core\camera.py
python core\camera.py 1                    # webcam index 1
python core\camera.py http://IP:8080/video # IP camera

# Chạy worker
python worker.py 1
python worker.py 2

# Cài thư viện
pip install -r requirements.txt
pip install <tên-thư-viện>

# Torch
# Máy CPU:
pip install torch torchvision torchaudio
# Máy CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## 💬 13. CÁCH DÙNG FILE NÀY

**Đầu buổi làm việc mới:**

1. Mở `CONTEXT.md`
2. Cập nhật mục **"ĐANG LÀM Ở ĐÂU"** + **"TRẠNG THÁI TỪNG NGƯỜI"** nếu khác
3. Gửi nguyên file cho AI + câu hỏi cụ thể
4. AI đọc 30 giây → nắm context → trả lời chính xác

**Cuối buổi:**

1. Sửa **"ĐANG LÀM Ở ĐÂU"** — đang ở bước nào
2. Sửa **"TRẠNG THÁI TỪNG NGƯỜI"** — ai xong gì
3. Đổi **"Cập nhật lần cuối"** thành ngày hôm nay
4. Save lại

---

## 📌 14. QUY TẮC VIẾT CODE CHUNG

### Python (AI_CNN)

- Mỗi file có **docstring** ở đầu — mô tả nhiệm vụ, input, output, ai dùng
- Không hard-code — đọc từ `config.py` hoặc `.env`
- Log rõ ràng với emoji: `✅` OK, `❌` lỗi, `⚠️` cảnh báo, `🔄` đang xử lý
- Không `print()` debug lung tung — dùng log có prefix `[tên-module]`

### ESP32 (IOT)

- Non-blocking: dùng `millis()`, KHÔNG dùng `delay()`
- Tách file: `main.cpp` (setup/loop), `sensors.cpp`, `servo.cpp`, `mqtt_handler.cpp`
- LED xanh = detect OK (cấp zone), LED đỏ = không tự tin (cấp zone)
- Servo tự quản lý vòng đời mở → giữ → đóng bằng timer

### Web (WEB)

- Không hard-code password — dùng `.env`
- MQTT subscriber chạy thread riêng
- SQLAlchemy session không share giữa thread
- WebSocket đẩy realtime cho FE

---

## 🎓 15. GHI CHÚ TỪ GIẢNG VIÊN

- **Đừng cố làm Docker/deploy** — đồ án môn học không cần
- **Ưu tiên chức năng + logic** hơn là tốc độ
- **Test từng module** rồi ghép — không code hết 1 lúc
- **Ghi log JSON** để debug dễ khi tích hợp
- **Trước demo 1 tuần:** test full pipeline trên máy GPU
- **Luôn có backup:** video record sẵn phòng camera lỗi

---

**Made with 💚 by nhóm K26 — Đại học Bình Dương**

````

---

## 📌 Việc em làm ngay

1. **Tạo file `CONTEXT.md`** ở gốc repo `Do-An-Mon-Hoc/`
2. **Copy nguyên nội dung trên** vào file
3. **Commit lên Git:**
   ```bash
   cd D:\Do-An-Mon-Hoc
   git add CONTEXT.md
   git commit -m "docs: thêm CONTEXT.md — bộ nhớ ngoài dự án"
   git push
````

---
