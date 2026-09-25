# 📄 Nội dung file `AI_CNN/README.md`

Em tạo file `AI_CNN/README.md` và paste nguyên nội dung dưới đây vào:

---

```markdown
# 🧠 AI_CNN — Module nhận diện & phân loại rác

**Phụ trách:** Vũ · **Vai trò:** Đọc camera → nhận diện rác (YOLOv8n) → publish MQTT + gửi ảnh lên Backend

---

## 📋 Yêu cầu hệ thống

| Thành phần | Version | Ghi chú |
|-----------|---------|---------|
| Python | 3.10+ | Khuyến nghị 3.11 |
| pip | 23.0+ | |
| Git | 2.30+ | |
| Webcam / IP Camera | — | IP Webcam (Android) hoặc webcam laptop |

**Máy dev (test logic):** CPU thường — dùng `ROI_SIZE=280`
**Máy demo (chạy thật):** GPU NVIDIA — dùng `ROI_SIZE=640`

---

## 🚀 Cài đặt lần đầu

### Bước 1: Clone repo + vào thư mục

```bash
git clone <repo-url>
cd Do-An-Mon-Hoc/AI_CNN
```

### Bước 2: Tạo môi trường ảo

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Prompt phải có `(venv)` ở đầu → OK.

### Bước 3: Cài PyTorch

⚠️ `torch` KHÔNG cài qua `requirements.txt` được — phải chọn đúng bản CPU hoặc CUDA.

**Máy có GPU NVIDIA (máy demo):**
```bash
# Kiểm tra driver trước
nvidia-smi

# Cài bản CUDA 12.1 (khuyên dùng)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Máy KHÔNG có GPU NVIDIA (máy test):**
```bash
pip install torch torchvision torchaudio
```

**Verify:**
```bash
python -c "import torch; print('Torch:', torch.__version__); print('GPU:', torch.cuda.is_available())"
```

Kết quả mong đợi:
- Máy GPU: `GPU: True`
- Máy CPU: `GPU: False` (vẫn OK — chạy chậm hơn)

### Bước 4: Cài thư viện còn lại

```bash
pip install -r requirements.txt
```

### Bước 5: Tạo file `.env`

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Mở `.env` và điền thông tin thật:

```bash
# === EMQX Cloud Serverless (Anh cấp qua Zalo) ===
MQTT_HOST=xxxxx.emqx.io
MQTT_PORT=8883
MQTT_USER=nhom_k26
MQTT_PASS=<mật khẩu thật>

# === Backend API ===
BACKEND_URL=http://localhost:8000/api/upload

# === ROI size (280 = máy yếu, 640 = máy GPU) ===
ROI_SIZE=640
```

⚠️ **KHÔNG commit file `.env`** lên Git — mật khẩu xin Anh qua Zalo.

### Bước 6: Kiểm tra model

```bash
dir model\yolo_v8_training\weights
```

Phải có file `v1-best.pt` (~6MB). Nếu chưa có → xin Vũ copy.

### Bước 7: Verify cài đặt

```bash
python check_classmap.py
python check_libs.py
```

Kết quả mong đợi:
```
0: 'inorganic-waste'  → vo_co   ✅
1: 'organic-waste'    → huu_co  ✅
2: 'recyclable waste' → tai_che ✅
🎉 Tất cả class đã map đúng!
```

---

## 🎮 Cách chạy

### Demo UI (test model nhanh)

```bash
python demo_ui.py
```

Mở cửa sổ OpenCV với khung ngắm 4 góc. Nhấn `q` để thoát.
**Không** publish MQTT — chỉ test model.

### Chạy worker thật

```bash
# Khu A
python worker.py 1

# Khu B
python worker.py 2
```

**Chạy 2 khu cùng lúc:** mở 2 terminal, mỗi terminal 1 lệnh.

---

## 📁 Cấu trúc thư mục

```
AI_CNN/
├── core/
│   ├── camera.py               # Đọc camera + reconnect
│   ├── frame_diff.py           # Lọc nhiễu (PA3)
│   ├── detector.py             # State machine
│   ├── mqtt_pub.py             # Publish MQTT (EMQX Cloud)
│   └── uploader.py             # POST ảnh async
├── config.py                   # Hằng số + CLASS_MAP
├── worker.py                   # Entry point (chạy thật)
├── demo_ui.py                  # UI demo
├── train_model.py              # Train model (đã xong)
├── check_classmap.py           # Verify CLASS_MAP
├── check_libs.py               # Verify thư viện
├── benchmark.py                # Đo tốc độ inference
├── .env                        # Config thật (KHÔNG commit)
├── .env.example                # Mẫu (commit)
├── requirements.txt
├── model/yolo_v8_training/weights/v1-best.pt
├── data/                       # Dataset (không commit)
└── local_images/               # Ảnh lưu khi lỗi mạng
```

---

## ⚙️ Cấu hình

### File `.env` — config theo máy

| Biến | Ý nghĩa | Giá trị |
|------|---------|---------|
| `MQTT_HOST` | Host EMQX Cloud | `xxxxx.emqx.io` |
| `MQTT_PORT` | Port MQTT (TLS) | `8883` (bắt buộc) |
| `MQTT_USER` | Username MQTT | Do Anh cấp |
| `MQTT_PASS` | Password MQTT | Do Anh cấp |
| `BACKEND_URL` | URL backend nhận ảnh | `http://localhost:8000/api/upload` |
| `ROI_SIZE` | Kích thước ROI (pixel) | `280` (máy yếu) / `640` (máy GPU) |

**Nguyên tắc `ROI_SIZE`:**
- Máy test (CPU): `280` → ~10 FPS
- Máy demo (GPU): `640` → ~30-50 FPS

### File `config.py` — hằng số dùng chung

**KHÔNG sửa trực tiếp** trừ khi có lý do. Các hằng số quan trọng:

```python
# Class mapping — PHẢI khớp model.names
CLASS_MAP = {
    "recyclable waste": "tai_che",     # ← CHÚ Ý: có DẤU CÁCH
    "organic-waste":    "huu_co",
    "inorganic-waste":  "vo_co",
}

CONF_MIN = 0.6          # confidence tối thiểu
WINDOW_SEC = 1.5        # cửa sổ tích lũy
COOLDOWN_SEC = 8        # nghỉ sau khi chốt
```

Nếu sửa `CLASS_MAP` → chạy lại `check_classmap.py` verify.

---

## 🔧 Troubleshooting

### `FileNotFoundError: v1-best.pt`

Chưa có file model. Kiểm tra:
```bash
dir model\yolo_v8_training\weights
```
Trống → xin Vũ copy file model.

### `RuntimeError: Thiếu biến môi trường`

Chưa tạo `.env` hoặc thiếu biến:
```bash
copy .env.example .env
# Điền thông tin thật vào
```

### `ModuleNotFoundError: No module named 'torch'`

Chưa cài torch hoặc sai venv:
```bash
where python                    # Phải thấy venv\Scripts\python.exe
venv\Scripts\activate           # Nếu chưa activate
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### `GPU: False` nhưng máy có NVIDIA

Đã cài nhầm torch bản CPU:
```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### `nvidia-smi: command not found`

Chưa cài driver NVIDIA. Tải tại [nvidia.com/download](https://www.nvidia.com/download/index.aspx).

### Camera không mở được

- Bật app IP Webcam trên điện thoại
- Đảm bảo điện thoại + laptop cùng WiFi
- Test: mở trình duyệt, truy cập `http://<IP-điện-thoại>:8080`
- Sửa `CAMERAS` trong `config.py` cho đúng IP

### Publish MQTT thất bại

- Verify thông tin `.env` khớp EMQX Dashboard
- Test bằng MQTTX trước
- Nếu WiFi trường chặn port 8883 → dùng hotspot điện thoại

---

## 🎯 Workflow dev

### Khi sửa code

```bash
git checkout -b feature/ai-<mô-tả>
# Sửa code + test
git add .
git commit -m "feat(ai): <mô tả>"
git push
```

Tạo PR → Anh review → merge về `main`.

### Khi pull code mới

```bash
git checkout main
git pull
pip install -r requirements.txt
```

### Trước khi demo

1. Pull code mới nhất về máy demo
2. Đổi `ROI_SIZE=640` trong `.env`
3. Chạy `python check_classmap.py` verify
4. Chạy `python worker.py 1` test 5 phút
5. Chuẩn bị backup: video record sẵn phòng camera lỗi

---

## 📞 Liên hệ

| Vấn đề | Người liên hệ |
|--------|---------------|
| Model AI, code worker | **Vũ** |
| MQTT config, backend | **Anh** |
| ESP32, phần cứng | **Tường** |
| Cấu hình EMQX Cloud | **Anh** |

---

## 📚 Tài liệu liên quan

- [Luồng nhận diện & phân loại](../../DOC/02-luong-xu-ly/luong-nhan-dien-phan-loai.md)
- [Luồng mức đầy & online/offline](../../DOC/02-luong-xu-ly/luong-mucday-trangthai-online.md)
- [MQTT topic & JSON format](../../DOC/06-mqtt/mqtt-topic-va-json-format.md)
- [Cài đặt PyTorch GPU](../../DOC/04-ai/cai-dat-pytorch-gpu.md)

---

**Made with 💚 by Vũ — K26 Đại học Bình Dương**
```

---

## 📌 Việc Vũ cần làm ngay

1. **Tạo file `AI_CNN/README.md`** — paste nguyên block trên
2. **Tạo 2 file test** (nếu chưa có):
   - `check_classmap.py` (đã có — em vừa chạy)
   - `check_libs.py` (nội dung bên dưới)
3. **Commit lên Git:**
   ```bash
   git add AI_CNN/README.md AI_CNN/check_libs.py
   git commit -m "docs(ai): thêm README + check_libs"
   git push
   ```

### Nội dung `check_libs.py` (nếu chưa có)

```python
"""check_libs.py — Kiểm tra thư viện đã cài đủ chưa."""
libs = ['torch', 'torchvision', 'ultralytics', 'cv2', 'dotenv', 'paho.mqtt', 'requests']
all_ok = True
for lib in libs:
    try:
        __import__(lib)
        print(f'✅ {lib}')
    except ImportError:
        print(f'❌ {lib} — THIẾU')
        all_ok = False

print()
print('🎉 Tất cả thư viện đã cài đủ!' if all_ok else '⚠️  Còn thiếu — chạy: pip install -r requirements.txt')
```

---

Em copy README trên gửi Vũ. Sau khi Vũ commit xong → báo thầy để thầy viết code `camera.py`. 💪